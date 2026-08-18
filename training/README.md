# Open Reason model training (not a published model)

This directory is the **training pipeline** for a future `theworker02/open-reason-1b`
model. It is **not** a Hugging Face upload and it does not invent eval numbers.

## Intended first model

- Hub id (later): `theworker02/open-reason-1b`
- Permissive base (documented, not auto-downloaded here): `TinyLlama/TinyLlama-1.1B-Chat-v1.0` (Apache-2.0)
- Data: local `data/release/*.jsonl` from `open-reason build --config all`

## Commands

```bash
open-reason train --smoke --data data/release/all.jsonl
open-reason evaluate-model --model training/work/model --data data/release/verified.jsonl
```

`--smoke` runs a tiny CPU embedding loop (a few steps) so the trainer is real.
It is **not** TinyLlama and must not be uploaded as `open-reason-1b`.

```bash
python training/scripts/prepare_sft.py data/release/all.jsonl training/work/sft.jsonl
open-reason train --smoke --config training/configs/smoke.yaml --data data/release/all.jsonl
```

Full 1B–3B training needs a GPU, `torch`, and `transformers`. If those are missing,
the CLI exits with an honest message and writes no fake metrics.

Eval protocol: `training/eval/protocol.yaml`. Holdout scoring: `docs/evaluation.md`.

## GitHub vs Hub

Train on a machine with GPU. Attach checkpoints to a **GitHub Release**.
Do not publish a placeholder model to Hugging Face.
