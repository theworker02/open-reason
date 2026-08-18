"""Build, validate, deduplicate, and export dataset configurations."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from open_reason.config import PipelineConfig, load_pipeline_config, repo_root
from open_reason.constants import CURRENT_CONFIGS, PIPELINE_VERSION
from open_reason.contamination import scan_examples
from open_reason.deduplication import Deduplicator
from open_reason.export.huggingface import sync_repo_docs, write_release_catalog
from open_reason.generation import BASE_CONFIGS, generate_config
from open_reason.io import example_to_record, write_jsonl, write_parquet
from open_reason.models import Example, QualityTier
from open_reason.provenance.reddit import inspect_record
from open_reason.review import enqueue
from open_reason.scoring import apply_evidence_score
from open_reason.statistics import summarize
from open_reason.transformation import transform_example
from open_reason.validation import validate_record


@dataclass
class BuildReport:
    config: str
    generated: int = 0
    validated: int = 0
    kept: int = 0
    validation_failures: int = 0
    reddit_rejected: int = 0
    dedup: dict[str, int] = field(default_factory=dict)
    contamination: dict[str, Any] = field(default_factory=dict)
    statistics: dict[str, Any] = field(default_factory=dict)
    dropped_reasons: list[str] = field(default_factory=list)
    review_queue: list[dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "config": self.config,
            "generated": self.generated,
            "validated": self.validated,
            "kept": self.kept,
            "validation_failures": self.validation_failures,
            "reddit_rejected": self.reddit_rejected,
            "dedup": self.dedup,
            "contamination": self.contamination,
            "statistics": self.statistics,
            "review_queue_size": len(self.review_queue),
        }


def process_examples(
    examples: list[Example],
    *,
    config: str,
    pipeline: PipelineConfig,
    strict: bool = False,
) -> tuple[list[Example], BuildReport]:
    report = BuildReport(config=config, generated=len(examples))
    dedup = Deduplicator(max_similarity=pipeline.max_near_duplicate_similarity)
    kept: list[Example] = []
    seen_ids: set[str] = set()

    for example in examples:
        example = transform_example(example)
        example = apply_evidence_score(example)
        record = example_to_record(example)
        reddit = inspect_record(record)
        if reddit:
            report.reddit_rejected += 1
            report.dropped_reasons.append(f"{example.id}:reddit")
            continue
        parsed, result = validate_record(record, strict=strict or pipeline.strict)
        if parsed is None or not result.ok:
            report.validation_failures += 1
            report.dropped_reasons.append(
                f"{example.id}:" + ",".join(issue.code for issue in result.issues)
            )
            continue
        report.validated += 1
        if parsed.id in seen_ids:
            continue
        if not dedup.keep(parsed):
            continue
        seen_ids.add(parsed.id)
        kept.append(parsed)

    report.kept = len(kept)
    report.dedup = dedup.as_dict()
    contamination = scan_examples(kept)
    report.contamination = contamination.as_dict()
    if strict and contamination.hits:
        raise RuntimeError(
            f"contamination hits in strict mode: {len(contamination.hits)}"
        )
    report.statistics = summarize(kept, config=config)
    report.review_queue = [
        {"example_id": item.example_id, "reasons": item.reasons} for item in enqueue(kept)
    ]
    return kept, report


def build_config(
    name: str,
    *,
    seed: int | None = None,
    strict: bool = False,
    root: Path | None = None,
) -> tuple[list[Example], BuildReport]:
    root = root or repo_root()
    pipeline = load_pipeline_config(root)
    if name not in CURRENT_CONFIGS:
        raise ValueError(f"unsupported config '{name}'")
    examples = generate_config(name, seed=seed if seed is not None else pipeline.seed)
    return process_examples(examples, config=name, pipeline=pipeline, strict=strict)


def configs_to_build(name: str) -> list[str]:
    if name == "all":
        return list(BASE_CONFIGS)
    return [name]


def export_examples(examples: list[Example], directory: Path, config: str) -> dict[str, int]:
    directory.mkdir(parents=True, exist_ok=True)
    records = [example_to_record(ex) for ex in examples]
    jsonl_path = directory / f"{config}.jsonl"
    parquet_path = directory / f"{config}.parquet"
    n_jsonl = write_jsonl(jsonl_path, records)
    n_parquet = write_parquet(parquet_path, records)
    return {"jsonl": n_jsonl, "parquet": n_parquet}


def assert_release_complete(directory: Path) -> None:
    """Raise if a full release is missing configs, parquet, or a matching catalog."""
    missing: list[str] = []
    for name in CURRENT_CONFIGS:
        if not (directory / f"{name}.jsonl").exists():
            missing.append(f"{name}.jsonl")
        if not (directory / f"{name}.parquet").exists():
            missing.append(f"{name}.parquet")
    for extra in ("manifest.yaml", "statistics.md", "README.md"):
        if not (directory / extra).exists():
            missing.append(extra)
    if missing:
        raise RuntimeError("incomplete release: " + ", ".join(missing))
    manifest = yaml.safe_load((directory / "manifest.yaml").read_text(encoding="utf-8")) or {}
    version = manifest.get("pipeline_version")
    if version != PIPELINE_VERSION:
        raise RuntimeError(
            f"release manifest pipeline_version={version!r} does not match {PIPELINE_VERSION}"
        )
    if not manifest.get("complete"):
        raise RuntimeError("release manifest is not marked complete")
    reports = manifest.get("reports") or {}
    for name in CURRENT_CONFIGS:
        if name not in reports:
            raise RuntimeError(f"release manifest missing report for {name}")


def publish_staging(staging: Path, dest: Path) -> None:
    """Replace dest with staging. Falls back to copy if rename is locked."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    backup = dest.with_name(dest.name + ".bak")
    if backup.exists():
        shutil.rmtree(backup)
    try:
        if dest.exists():
            dest.rename(backup)
        staging.rename(dest)
    except OSError:
        if not dest.exists() and backup.exists():
            backup.rename(dest)
        dest.mkdir(parents=True, exist_ok=True)
        for item in staging.iterdir():
            target = dest / item.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            if item.is_dir():
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)
        shutil.rmtree(staging, ignore_errors=True)
    if backup.exists():
        shutil.rmtree(backup, ignore_errors=True)


def build_release(
    *,
    config: str = "all",
    seed: int = 42,
    strict: bool = False,
    out: Path,
    auto_approve_sources: bool = False,
    update_docs: bool = True,
    progress: Any | None = None,
) -> dict[str, dict[str, Any]]:
    """Generate and export a configuration. `all` is published atomically."""
    if auto_approve_sources:
        from open_reason.sources.approve import auto_approve as run_auto_approve

        run_auto_approve(apply=True)
        if progress:
            progress("Applied curriculum auto-approve to sources/registry.yaml")

    out = Path(out)
    if config != "all":
        examples, report = build_config(config, seed=seed, strict=strict)
        export_examples(examples, out, config)
        if progress:
            progress(f"{config} kept={report.kept}")
        return {config: report.as_dict()}

    staging = out.parent / f".{out.name}.staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    pipeline = load_pipeline_config()
    reports: dict[str, dict[str, Any]] = {}
    all_examples: list[Example] = []
    published = False
    try:
        for name in BASE_CONFIGS:
            examples, report = build_config(name, seed=seed, strict=strict)
            export_examples(examples, staging, name)
            reports[name] = report.as_dict()
            all_examples.extend(examples)
            if progress:
                progress(f"{name} kept={report.kept}")
        combined, combined_report = process_examples(
            all_examples, config="all", pipeline=pipeline, strict=strict
        )
        export_examples(combined, staging, "all")
        reports["all"] = combined_report.as_dict()
        if progress:
            progress(f"all kept={combined_report.kept}")
        core = [ex for ex in combined if ex.quality.tier in {QualityTier.S, QualityTier.A}]
        verified = [
            ex for ex in combined if ex.quality.verified and ex.quality.tier is QualityTier.S
        ]
        core_kept, core_report = process_examples(
            core, config="core", pipeline=pipeline, strict=strict
        )
        ver_kept, ver_report = process_examples(
            verified, config="verified", pipeline=pipeline, strict=strict
        )
        export_examples(core_kept, staging, "core")
        export_examples(ver_kept, staging, "verified")
        reports["core"] = core_report.as_dict()
        reports["verified"] = ver_report.as_dict()
        if progress:
            progress(f"core kept={core_report.kept}")
            progress(f"verified kept={ver_report.kept}")
        write_release_catalog(staging, reports)
        from open_reason.sources.catalog import write_source_catalogs

        write_source_catalogs()
        publish_staging(staging, out)
        published = True
    except Exception:
        if not published and staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        raise
    assert_release_complete(out)
    if update_docs:
        sync_repo_docs(reports, root=repo_root())
    return reports
