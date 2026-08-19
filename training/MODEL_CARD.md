---
language:
  - en
license: apache-2.0
library_name: transformers
tags:
  - open-reason
  - reasoning
base_model: TinyLlama/TinyLlama-1.1B-Chat-v1.0
datasets:
  - theworker02/open-reason
---

# Open Reason 1B — not trained on this machine

Do **not** treat this file as a published `theworker02/open-reason-1b` model.
No 1B–3B SFT ran here. No finetune was uploaded.

## Hardware that was inspected (2026-08-18)

- OS: Windows AMD64
- RAM: ~61 GB
- `torch`: 2.12.0+**cpu**
- `torch.cuda.is_available()`: **false**
- No CUDA GPU in this environment

A real 1.1B chat SFT (TinyLlama, Apache-2.0) needs a CUDA GPU (about 8 GB+ VRAM
with LoRA, more for full finetune), `transformers`, and the local
`data/release/all.jsonl` from `open-reason build --config all --seed 42`.

Intended command once GPU + CUDA torch exist:

```text
python training/scripts/prepare_sft.py data/release/all.jsonl training/work/sft.jsonl
open-reason train --config training/configs/open-reason-1b.yaml --data data/release/all.jsonl
```

Then evaluate the **base** TinyLlama checkpoint against the finetune on held-out
coding / mathematics / science / reasoning items and write measured exact-match
or sandbox pass rates. Upload to `theworker02/open-reason-1b` only after that
job finishes.

## Smoke trainer (CPU, labeled smoke)

Command:

```text
open-reason train --smoke --config training/configs/smoke.yaml --data data/release/all.jsonl
```

Recorded in `training/work/smoke_metrics.json`:

- smoke: true
- cuda: false
- steps: 3
- rows: 8
- losses: 4.2393, 4.0729, 4.4579 (toy embedding net, random token ids)
- note: not TinyLlama, not open-reason-1b

These losses are **not** model-quality metrics.
