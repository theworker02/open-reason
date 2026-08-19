# Training

The training pipeline is real scaffolding, not a published Hugging Face model.

```bash
python training/scripts/prepare_sft.py data/release/all.jsonl training/work/sft.jsonl
open-reason train --smoke --config training/configs/smoke.yaml --data data/release/all.jsonl
```

`--smoke` runs a tiny CPU embedding loop so the trainer is not a no-op. It is
**not** TinyLlama and must not be uploaded as `theworker02/open-reason-1b`.

The 2026-08-18 developer machine had CPU-only torch (`cuda=false`). Smoke
metrics live in `training/work/smoke_metrics.json` and are not 1B eval scores.

Full 1B training needs a GPU, `torch`, and `transformers`. Missing pieces exit
with an honest message and write no fake eval tables.

See `training/README.md`, `training/eval/protocol.yaml`, and `training/MODEL_CARD.md`.
