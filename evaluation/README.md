# Evaluation (holdout)

Score model **predictions** against `benchmarks/` gold. Do not train on this
directory. `open-reason score` writes `evaluation/reports/last_score.json`.

## Commands

```bash
open-reason benchmark --path benchmarks/items.jsonl --train data/release/all.jsonl
open-reason score --predictions evaluation/fixtures/sample_predictions.jsonl --gold benchmarks/items.jsonl
```

Exact-match and numeric-match rates are computed only when you supply
predictions. Missing checkpoints do not produce invented accuracy numbers.

## Files

| Path | Role |
| --- | --- |
| `metrics.yaml` | Metric definitions |
| `fixtures/sample_predictions.jsonl` | Tiny fixture for tests (not a model run) |
| `reports/` | Local score JSON (gitignored except `.gitkeep`) |
| `src/open_reason/evaluation` | Implementation |
