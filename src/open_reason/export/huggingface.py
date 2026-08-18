"""Hugging Face dataset card helpers and release catalog writers."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from open_reason.constants import CURRENT_CONFIGS, DATASET_NAME, PIPELINE_VERSION
from open_reason.statistics import render_markdown

SNAPSHOT_START = "<!-- BEGIN_RELEASE_SNAPSHOT -->"
SNAPSHOT_END = "<!-- END_RELEASE_SNAPSHOT -->"


HF_FEATURES = {
    "id": {"dtype": "string", "_type": "Value"},
    "domain": {"dtype": "string", "_type": "Value"},
    "task_type": {"dtype": "string", "_type": "Value"},
    "difficulty": {"dtype": "string", "_type": "Value"},
    "prompt": {"dtype": "string", "_type": "Value"},
    "context": {"dtype": "string", "_type": "Value"},
    "observations": {"dtype": "string", "_type": "Value"},
    "constraints": {"dtype": "string", "_type": "Value"},
    "assumptions": {"dtype": "string", "_type": "Value"},
    "plan": {"dtype": "string", "_type": "Value"},
    "strategy": {"dtype": "string", "_type": "Value"},
    "solution": {"dtype": "string", "_type": "Value"},
    "answer": {"dtype": "string", "_type": "Value"},
    "verification": {"dtype": "string", "_type": "Value"},
    "provenance": {"dtype": "string", "_type": "Value"},
    "quality": {"dtype": "string", "_type": "Value"},
    "education_level": {"dtype": "string", "_type": "Value"},
    "concept_id": {"dtype": "string", "_type": "Value"},
    "evidence": {"dtype": "string", "_type": "Value"},
    "transformation": {"dtype": "string", "_type": "Value"},
    "temporal": {"dtype": "string", "_type": "Value"},
    "runtime": {"dtype": "string", "_type": "Value"},
    "natural_language": {"dtype": "string", "_type": "Value"},
    "translation_status": {"dtype": "string", "_type": "Value"},
    "metadata": {"dtype": "string", "_type": "Value"},
}


def dataset_yaml_frontmatter(stats_by_config: dict[str, dict[str, Any]]) -> str:
    configs = []
    for name in CURRENT_CONFIGS:
        configs.append(
            {
                "config_name": name,
                "data_files": {"train": f"data/release/{name}.parquet"},
            }
        )
    payload = {
        "pretty_name": "Open Reason",
        "license": "cc-by-4.0",
        "task_categories": [
            "text-generation",
            "question-answering",
            "text2text-generation",
        ],
        "language": ["en"],
        "tags": [
            "reasoning",
            "coding",
            "mathematics",
            "science",
            "education",
            "provenance",
            "evaluation",
        ],
        "size_categories": ["1K<n<10K"],
        "dataset_info": {
            "dataset_name": DATASET_NAME,
            "config_name": "all",
            "features": HF_FEATURES,
            "splits": {
                "train": {
                    "name": "train",
                    "num_examples": (stats_by_config.get("all") or {}).get("total_examples", 0),
                }
            },
        },
        "configs": configs,
    }
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)


def write_release_manifest(path: Path, reports: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "dataset": DATASET_NAME,
        "pipeline_version": PIPELINE_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "complete": True,
        "configs": [name for name in CURRENT_CONFIGS if name in reports],
        "reports": reports,
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def snapshot_table(reports: dict[str, Any]) -> str:
    lines = [
        "| Configuration | Examples | Verified | Human-authored |",
        "| --- | ---: | ---: | ---: |",
    ]
    for name in CURRENT_CONFIGS:
        report = reports.get(name) or {}
        stats = report.get("statistics") or {}
        if not report and not stats:
            continue
        total = stats.get("total_examples", report.get("kept", 0))
        verified = stats.get("verified_examples", 0)
        human = stats.get("human_authored_examples", 0)
        lines.append(f"| {name} | {total} | {verified} | {human} |")
    return "\n".join(lines)


def snapshot_markdown(reports: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"Pipeline version **{PIPELINE_VERSION}**.",
            "",
            snapshot_table(reports),
            "",
            "Rebuild with `open-reason build --config all --seed 42 --out data/release`.",
            "Full tables: `data/release/statistics.md`.",
        ]
    )


def statistics_markdown(reports: dict[str, Any]) -> str:
    chunks: list[str] = []
    for name in CURRENT_CONFIGS:
        stats = (reports.get(name) or {}).get("statistics")
        if stats:
            chunks.append(render_markdown(stats))
    return "\n\n".join(chunks).rstrip() + "\n"


def write_release_readme(path: Path, reports: dict[str, Any]) -> None:
    body = "\n".join(
        [
            f"# Open Reason v{PIPELINE_VERSION} release files",
            "",
            "Generated by `open-reason build --config all --seed 42`.",
            "",
            snapshot_table(reports),
            "",
            "- `*.jsonl` — human-readable rows",
            "- `*.parquet` — Hugging Face / analytics",
            "- `core.*` — quality tiers S and A",
            "- `verified.*` — independently checked tier S",
            "- `statistics.md` — per-config tables",
            "- `manifest.yaml` — validation, dedup, contamination, and version",
            "",
            "Parquet and JSONL shards are local build products (gitignored).",
            "GitHub stores this catalog; Hugging Face receives shards on a GitHub Release.",
            "",
            "**Open Reason does not use Reddit as a data source.**",
            "",
            "Do not mix `benchmarks/items.jsonl` into these files.",
            "",
        ]
    )
    path.write_text(body, encoding="utf-8")


def replace_marked_section(text: str, body: str, *, start: str = SNAPSHOT_START, end: str = SNAPSHOT_END) -> str:
    if start not in text or end not in text:
        raise ValueError(f"missing {start} / {end} markers")
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    inner = body.strip("\n")
    return f"{before}{start}\n{inner}\n{end}{after}"


def update_marked_file(path: Path, body: str) -> None:
    original = path.read_text(encoding="utf-8")
    path.write_text(replace_marked_section(original, body), encoding="utf-8")


def write_release_catalog(directory: Path, reports: dict[str, Any]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    write_release_manifest(directory / "manifest.yaml", reports)
    (directory / "statistics.md").write_text(statistics_markdown(reports), encoding="utf-8")
    write_release_readme(directory / "README.md", reports)


def sync_distribution_card(root: Path) -> None:
    """Copy DATA_CARD.md into the Hugging Face sync directory."""
    src = root / "DATA_CARD.md"
    dest = root / "distribution" / "dataset" / "README.md"
    if not src.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def sync_repo_docs(reports: dict[str, Any], *, root: Path) -> None:
    body = snapshot_markdown(reports)
    data_card = root / "DATA_CARD.md"
    readme = root / "README.md"
    if data_card.exists() and SNAPSHOT_START in data_card.read_text(encoding="utf-8"):
        update_marked_file(data_card, body)
    if readme.exists() and SNAPSHOT_START in readme.read_text(encoding="utf-8"):
        update_marked_file(readme, body)
    sync_distribution_card(root)
