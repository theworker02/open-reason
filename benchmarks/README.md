# Open Reason evaluation suite

Held-out items live in JSONL under this directory. **Do not mix them into
training exports.**

`open-reason build` writes training/release data under `data/release/` only.

## Files

| File | Role |
| --- | --- |
| `items.jsonl` | v0.1 holdout (seed 2026, disjoint from train seed 42) |
| `v1.jsonl` | Additional original holdout items for v1.0.0 |
| `splits.yaml` | Seed and file list |

```bash
open-reason benchmark --path benchmarks/items.jsonl --train data/release/all.jsonl
open-reason score --predictions evaluation/fixtures/sample_predictions.jsonl --gold benchmarks/items.jsonl
```

## Metrics

| Area | Metric |
| --- | --- |
| Coding | execution success, tests passed, pass@k (when a real model is scored) |
| Reasoning | exact match on the structured answer, constraint satisfaction |
| Mathematics | exact/symbolic match, numeric tolerance |
| Science | numeric tolerance, interpretation labels |

v1.0.0 ships holdout JSONL generated from a **different seed** than the training
split (`seed=2026`) plus extra original items in `v1.jsonl`.
