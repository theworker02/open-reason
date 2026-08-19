"""Open Reason command-line interface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from open_reason import __version__
from open_reason.config import repo_root
from open_reason.constants import REDDIT_POLICY
from open_reason.generation import generate_config
from open_reason.io import example_to_record, iter_jsonl, record_to_example
from open_reason.pipeline import build_config, build_release, export_examples
from open_reason.statistics import render_markdown, summarize
from open_reason.validation import validate_record

app = typer.Typer(
    name="open-reason",
    no_args_is_help=True,
    help=(
        "Open Reason dataset infrastructure: ingest, validate, verify, and export "
        "provenance-aware reasoning data. Open Reason does not use Reddit as a data source."
    ),
)
console = Console()


def _config_option() -> str:
    return typer.Option(
        "all",
        "--config",
        "-c",
        help="Dataset configuration name (coding, education, core, verified, all, ...).",
    )


@app.callback()
def _root() -> None:
    """Open Reason pipeline."""


@app.command()
def version() -> None:
    """Print the pipeline version."""
    console.print(f"open-reason {__version__}")


@app.command()
def sources(
    matrix: bool = typer.Option(False, "--matrix", help="Print the source matrix Markdown."),
    json_out: bool = typer.Option(False, "--json", help="Print registry JSON."),
    approve: bool = typer.Option(
        False,
        "--approve",
        help="Run license-policy auto-approve (curriculum / original tasks only).",
    ),
    apply: bool = typer.Option(
        False,
        "--apply",
        help="Write auto-approve decisions into sources/registry.yaml.",
    ),
) -> None:
    """List the source registry, or auto-approve sources under the license policy."""
    from open_reason.sources import load_registry
    from open_reason.sources.approve import auto_approve
    from open_reason.sources.matrix import render_markdown

    if approve or apply:
        decisions = auto_approve(apply=apply)
        table = Table(title="Source auto-approve")
        table.add_column("id")
        table.add_column("action")
        table.add_column("enabled")
        table.add_column("verbatim")
        table.add_column("reason")
        for item in decisions:
            table.add_row(
                item.source_id,
                item.action,
                "yes" if item.enabled else "no",
                "yes" if item.verbatim else "no",
                item.reason,
            )
        console.print(table)
        if apply:
            console.print("[green]Wrote sources/registry.yaml[/green]")
        else:
            console.print("Dry run. Re-run with --approve --apply to write the registry.")
        console.print(REDDIT_POLICY)
        return
    registry = load_registry()
    if matrix:
        console.print(render_markdown(registry))
        return
    if json_out:
        console.print_json(data=registry.raw)
        return
    table = Table(title="Open Reason sources")
    table.add_column("id")
    table.add_column("status")
    table.add_column("enabled")
    table.add_column("curriculum")
    table.add_column("license")
    for source in registry.sources:
        table.add_row(
            source.id,
            source.status,
            "yes" if source.enabled else "no",
            "yes" if source.curriculum_use else "no",
            str(source.license_spdx or source.license or "n/a"),
        )
    console.print(table)
    console.print(REDDIT_POLICY)
    console.print("Auto-approve: open-reason sources --approve --apply")


@app.command("discover")
def discover(
    json_out: bool = typer.Option(True, "--json/--table", help="Print JSON (default) or a table."),
) -> None:
    """Score candidate sources. Does not ingest and never includes Reddit."""
    from open_reason.sources.discovery import discover_candidates

    rows = discover_candidates()
    if json_out:
        console.print_json(data=rows)
        return
    table = Table(title="Discovery (no ingest)")
    table.add_column("id")
    table.add_column("total")
    table.add_column("kind")
    for row in rows:
        table.add_row(str(row["source_id"]), str(row["total"]), str(row.get("kind") or ""))
    console.print(table)
    console.print(REDDIT_POLICY)


@app.command("evaluate-sources")
def evaluate_sources_cmd() -> None:
    """Structured policy evaluation for every registry source."""
    from open_reason.sources.evaluate import evaluate_all_sources

    reports = evaluate_all_sources()
    console.print_json(data=reports)
    decisions = {item["decision"] for item in reports}
    console.print(f"decisions={sorted(decisions)}")
    console.print(REDDIT_POLICY)


@app.command("analyze-coverage")
def analyze_coverage_cmd(
    config: str = typer.Option("education", "--config", "-c"),
    path: Optional[Path] = typer.Option(None, "--path", help="JSONL to score instead of rebuilding."),
) -> None:
    """Report knowledge-graph coverage, including insufficient_coverage."""
    from open_reason.coverage import analyze_coverage

    if path:
        examples = [record_to_example(rec) for rec in iter_jsonl(path)]
    else:
        examples, _report = build_config(config)
    report = analyze_coverage(examples)
    console.print_json(data=report)


@app.command("train")
def train_cmd(
    smoke: bool = typer.Option(False, "--smoke", help="Tiny CPU run that proves the trainer, not a 1B model."),
    config: Path = typer.Option(Path("training/configs/open-reason-local.yaml"), "--config"),
    data: Path = typer.Option(Path("data/release/all.jsonl"), "--data"),
) -> None:
    """Run the Open Reason training entrypoint. Does not invent metrics."""
    from open_reason.training import run_training

    code = run_training(config_path=config, data_path=data, smoke=smoke)
    raise typer.Exit(code=code)


@app.command("evaluate-model")
def evaluate_model_cmd(
    model: Path = typer.Option(Path("training/work/model"), "--model"),
    data: Path = typer.Option(Path("data/release/verified.jsonl"), "--data"),
    limit: int = typer.Option(32, "--limit"),
) -> None:
    """Compare a trained checkpoint to a documented base. Fails honestly if missing."""
    from open_reason.training import evaluate_model

    code = evaluate_model(model_dir=model, data_path=data, limit=limit)
    raise typer.Exit(code=code)


@app.command("release")
def release_cmd(
    out: Path = typer.Option(Path("data/release"), "--out"),
    seed: int = typer.Option(42, "--seed"),
    auto_approve_sources: bool = typer.Option(True, "--auto-approve/--no-auto-approve"),
) -> None:
    """Discover, evaluate, auto-approve, build, and write coverage. Does not upload to Hugging Face."""
    from open_reason.coverage import analyze_coverage
    from open_reason.pipeline import assert_release_complete
    from open_reason.sources.approve import auto_approve
    from open_reason.sources.discovery import discover_candidates
    from open_reason.sources.evaluate import evaluate_all_sources

    discover_candidates()
    console.print_json(data=evaluate_all_sources())
    if auto_approve_sources:
        auto_approve(apply=True)
        console.print("[green]Applied source policy auto-approve[/green]")
    reports = build_release(
        config="all",
        seed=seed,
        out=out,
        auto_approve_sources=False,
        progress=lambda message: console.print(f"[green]{message}[/green]"),
    )
    assert_release_complete(out)
    examples = [record_to_example(rec) for rec in iter_jsonl(out / "all.jsonl")] if (out / "all.jsonl").exists() else []
    coverage = analyze_coverage(examples)
    (out / "coverage.json").write_text(json.dumps(coverage, indent=2) + "\n", encoding="utf-8")
    console.print_json(data={"kept": {k: v.get("kept") for k, v in reports.items()}, "coverage": coverage})
    console.print("Hugging Face upload is not part of this command. Publish later via GitHub Release.")
    console.print(REDDIT_POLICY)


@app.command()
def ingest(
    config: str = typer.Option("all", "--config", "-c", help="Configuration to generate."),
    source: str | None = typer.Option(
        None,
        "--source",
        help="Registry source id (must be enabled).",
    ),
    seed: int = typer.Option(42, "--seed", help="Deterministic generator seed."),
    out: Path = typer.Option(Path("data/work/raw.jsonl"), "--out", help="JSONL output path."),
) -> None:
    """Collect examples from an enabled source or from in-repo generators.

    Unreviewed third-party sources fail closed. Open Reason does not use Reddit.
    """
    if source:
        from open_reason.sources import SourceAdmissionError, assert_can_ingest

        try:
            record = assert_can_ingest(source)
        except SourceAdmissionError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(code=1) from exc
        if record.id == "open-reason-generators":
            examples = generate_config(config, seed=seed)
        elif record.id == "open-reason-authors":
            from open_reason.ingestion.human import HumanAuthoredConnector

            examples = list(HumanAuthoredConnector().iter_examples())
        else:
            from open_reason.generation.curriculum import generate_original_for_source

            examples = generate_original_for_source(record.id, seed=seed)
            if not examples:
                console.print(
                    f"Source '{record.id}' is enabled for original tasks but has no bank yet."
                )
    else:
        examples = generate_config(config, seed=seed)
    n = _write_examples(out, examples)
    console.print(f"Wrote {n} examples to {out}")


@app.command()
def extract(
    path: Path = typer.Argument(..., help="Input JSONL."),
    out: Path = typer.Option(Path("data/work/extracted.jsonl"), "--out"),
) -> None:
    """Attach knowledge-graph concept ids where they can be inferred."""
    from open_reason.extraction import extract_concept

    examples = [extract_concept(record_to_example(rec)) for rec in iter_jsonl(path)]
    n = _write_examples(out, examples)
    console.print(f"Extracted concepts for {n} examples to {out}")


@app.command()
def transform(
    path: Path = typer.Argument(..., help="Input JSONL."),
    out: Path = typer.Option(Path("data/work/transformed.jsonl"), "--out"),
) -> None:
    """Normalize knowledge units, score evidence, and record transformation history."""
    from open_reason.transformation import transform_example

    examples = [transform_example(record_to_example(rec)) for rec in iter_jsonl(path)]
    n = _write_examples(out, examples)
    console.print(f"Transformed {n} examples to {out}")


@app.command()
def generate(
    domain: str = typer.Option("programming", "--domain", "-d", help="Domain or config name."),
    seed: int = typer.Option(42, "--seed"),
    out: Path = typer.Option(Path("data/work/generated.jsonl"), "--out"),
) -> None:
    """Generate original examples for a domain. Does not fetch third-party websites."""
    examples = generate_config(domain, seed=seed)
    n = _write_examples(out, examples)
    console.print(f"Generated {n} examples for {domain} -> {out}")


@app.command()
def normalize(
    path: Path = typer.Argument(..., help="Input JSONL."),
    out: Path = typer.Option(Path("data/work/normalized.jsonl"), "--out"),
) -> None:
    """Normalize text fields without changing meaning."""
    from open_reason.normalization import normalize_example

    examples = [normalize_example(record_to_example(rec)) for rec in iter_jsonl(path)]
    n = _write_examples(out, examples)
    console.print(f"Normalized {n} examples to {out}")


@app.command()
def deduplicate(
    path: Path = typer.Argument(..., help="Input JSONL."),
    out: Path = typer.Option(Path("data/work/dedup.jsonl"), "--out"),
    threshold: float = typer.Option(0.92, "--threshold", help="Near-duplicate similarity cap."),
) -> None:
    """Drop exact, normalized, and near-duplicate examples."""
    from open_reason.deduplication import Deduplicator

    examples = [record_to_example(rec) for rec in iter_jsonl(path)]
    dedup = Deduplicator(max_similarity=threshold)
    kept = dedup.filter(examples)
    n = _write_examples(out, kept)
    console.print(json.dumps(dedup.as_dict(), indent=2))
    console.print(f"Wrote {n} examples to {out}")


@app.command()
def validate(
    path: Optional[Path] = typer.Argument(None, help="JSONL file or directory of JSONL files."),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Build and validate a config instead of a path."),
    strict: bool = typer.Option(False, "--strict", help="Reject unknown provenance and contamination hits."),
) -> None:
    """Validate schema, licenses, provenance, Reddit exclusion, and PII heuristics."""
    if config:
        _, report = build_config(config, strict=strict)
        console.print(json.dumps(report.as_dict(), indent=2, default=str))
        if report.validation_failures or report.reddit_rejected:
            raise typer.Exit(code=1)
        return
    if path is None:
        path = repo_root() / "data"
    files = _jsonl_files(path)
    failures = 0
    total = 0
    for file in files:
        for rec in iter_jsonl(file):
            total += 1
            _, result = validate_record(rec, strict=strict)
            if not result.ok:
                failures += 1
                console.print(f"[red]{file} {rec.get('id')}:[/red] " + "; ".join(i.message for i in result.issues))
    console.print(f"Checked {total} records in {len(files)} files; failures={failures}")
    console.print(REDDIT_POLICY)
    if failures:
        raise typer.Exit(code=1)


@app.command()
def verify(
    config: str = typer.Option("coding", "--config", "-c"),
    strict: bool = typer.Option(False, "--strict"),
) -> None:
    """Run executable verification for a configuration (coding uses the sandbox)."""
    examples, report = build_config(config, strict=strict)
    verified = sum(1 for ex in examples if ex.quality.verified)
    console.print(f"kept={report.kept} verified={verified} validation_failures={report.validation_failures}")
    if config == "coding" and verified == 0:
        raise typer.Exit(code=1)


@app.command()
def statistics(
    config: str = typer.Option("all", "--config", "-c"),
    path: Optional[Path] = typer.Option(None, "--path", help="Optional JSONL to summarize instead of rebuilding."),
) -> None:
    """Print dataset statistics as JSON and a Markdown table."""
    if path:
        examples = [record_to_example(rec) for rec in iter_jsonl(path)]
        summary = summarize(examples, config=config)
    else:
        examples, report = build_config(config)
        summary = report.statistics
    console.print(json.dumps(summary, indent=2))
    console.print()
    console.print(render_markdown(summary))


@app.command()
def build(
    config: str = typer.Option("all", "--config", "-c"),
    seed: int = typer.Option(42, "--seed"),
    strict: bool = typer.Option(False, "--strict"),
    out: Path = typer.Option(Path("data/release"), "--out", help="Release directory."),
    auto_approve_sources: bool = typer.Option(
        False,
        "--auto-approve",
        help="Run curriculum auto-approve before generating.",
    ),
) -> None:
    """Generate, validate, deduplicate, and export a configuration."""
    reports = build_release(
        config=config,
        seed=seed,
        strict=strict,
        out=out,
        auto_approve_sources=auto_approve_sources,
        progress=lambda message: console.print(f"[green]{message}[/green]"),
    )
    table = Table(title="Open Reason build")
    table.add_column("config")
    table.add_column("kept", justify="right")
    for name, rep in reports.items():
        table.add_row(name, str(rep.get("kept", 0)))
    console.print(table)


@app.command()
def export(
    config: str = typer.Option("all", "--config", "-c"),
    format: str = typer.Option("parquet", "--format", help="jsonl, parquet, or both"),
    out: Path = typer.Option(Path("data/release"), "--out"),
) -> None:
    """Export an already-built configuration. Rebuilds if needed."""
    examples, _report = build_config(config)
    if format not in {"jsonl", "parquet", "both"}:
        raise typer.BadParameter("format must be jsonl, parquet, or both")
    counts = export_examples(examples, out, config)
    console.print(counts)


@app.command()
def benchmark(
    path: Path = typer.Option(Path("benchmarks/items.jsonl"), "--path"),
    train: Path = typer.Option(Path("data/release/all.jsonl"), "--train"),
) -> None:
    """Report overlap between holdout benchmark items and a training JSONL."""
    bench_ids = {rec.get("id") for rec in iter_jsonl(path)} if path.exists() else set()
    train_ids: set[str] = set()
    if train.exists():
        train_ids = {rec.get("id") for rec in iter_jsonl(train)}
    overlap = sorted(i for i in bench_ids & train_ids if i)
    report = {
        "benchmark_items": len(bench_ids),
        "train_items": len(train_ids),
        "id_overlap": len(overlap),
        "overlap_ids": overlap[:20],
    }
    console.print(json.dumps(report, indent=2))
    if overlap:
        raise typer.Exit(code=1)


@app.command()
def catalogs(
    apply: bool = typer.Option(
        True,
        "--apply/--dry-run",
        help="Write sources/approved|restricted|prohibited catalogs from the registry.",
    ),
) -> None:
    """Export machine-readable source catalogs. Does not scrape third-party sites."""
    from open_reason.sources.catalog import partition_sources, write_source_catalogs

    buckets = partition_sources()
    console.print(
        json.dumps(
            {name: [row["id"] for row in rows] for name, rows in buckets.items()},
            indent=2,
        )
    )
    if apply:
        written = write_source_catalogs()
        for label, path in written.items():
            console.print(f"{label}: {path}")
    console.print(REDDIT_POLICY)


@app.command("score")
def score_cmd(
    predictions: Path = typer.Option(Path("evaluation/fixtures/sample_predictions.jsonl"), "--predictions"),
    gold: Path = typer.Option(Path("benchmarks/items.jsonl"), "--gold"),
    train: Optional[Path] = typer.Option(Path("data/release/all.jsonl"), "--train"),
) -> None:
    """Score predictions against holdout gold. Refuses to invent model metrics."""
    from open_reason.evaluation import evaluate_paths, write_metrics

    train_path = train if train and train.exists() else None
    report = evaluate_paths(predictions=predictions, gold=gold, train=train_path)
    out = repo_root() / "evaluation" / "reports" / "last_score.json"
    write_metrics(out, report)
    console.print_json(data=report)
    if report.get("contaminated"):
        raise typer.Exit(code=1)


@app.command()
def inspect(
    path: Path = typer.Argument(..., help="JSONL file."),
    example_id: Optional[str] = typer.Option(None, "--id", help="Example id to show."),
    limit: int = typer.Option(3, "--limit"),
) -> None:
    """Pretty-print one or more examples."""
    shown = 0
    for rec in iter_jsonl(path):
        if example_id and rec.get("id") != example_id:
            continue
        console.print_json(data=rec)
        shown += 1
        if not example_id and shown >= limit:
            break
    if shown == 0:
        raise typer.Exit(code=1)


def _write_examples(path: Path, examples) -> int:
    from open_reason.io import write_jsonl

    return write_jsonl(path, [example_to_record(ex) for ex in examples])


def _jsonl_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.rglob("*.jsonl"))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
