#!/usr/bin/env python3
"""Write held-out benchmark items using a different seed than training (42)."""

from __future__ import annotations

import json
from pathlib import Path

from open_reason.generation.mathematics import generate_mathematics
from open_reason.generation.reasoning import generate_reasoning
from open_reason.generation.science import generate_science
from open_reason.io import example_to_record, write_jsonl
from open_reason.pipeline import process_examples
from open_reason.config import load_pipeline_config

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmarks" / "items.jsonl"


def main() -> None:
    pipeline = load_pipeline_config(ROOT)
    examples = []
    examples.extend(generate_mathematics(seed=2026)[:40])
    examples.extend(generate_science(seed=2026)[:40])
    examples.extend(generate_reasoning(seed=2026)[:40])
    kept, report = process_examples(examples, config="benchmarks", pipeline=pipeline)
    # Mark as eval-only in metadata
    records = []
    train_ids = set()
    release = ROOT / "data" / "release" / "all.jsonl"
    if release.exists():
        for line in release.read_text(encoding="utf-8").splitlines():
            if line.strip():
                train_ids.add(json.loads(line)["id"])
    for ex in kept:
        if ex.id in train_ids:
            continue
        data = example_to_record(ex)
        data["metadata"] = dict(data.get("metadata") or {})
        data["metadata"]["split"] = "benchmark"
        data["metadata"]["holdout"] = True
        records.append(data)
    write_jsonl(OUT, records)
    print(
        f"wrote {len(records)} benchmark items to {OUT} "
        f"(dropped_dups={report.dedup}; excluded_train_overlap={len(kept) - len(records)})"
    )


if __name__ == "__main__":
    main()
