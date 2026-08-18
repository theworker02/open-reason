# Evaluation

Holdout gold lives in `benchmarks/`. Training shards live in `data/release/`.
Those trees must not share example ids.

```bash
open-reason benchmark --path benchmarks/items.jsonl --train data/release/all.jsonl
open-reason score --predictions PATH.jsonl --gold benchmarks/items.jsonl
```

`open-reason score` writes `evaluation/reports/last_score.json`. It does not
invent accuracy for a missing model.

Implementation: `src/open_reason/evaluation/`. Metric list: `evaluation/metrics.yaml`.
