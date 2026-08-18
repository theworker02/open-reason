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

# Open Reason 1B (template)

Fill this card **only after a real training run**. Do not publish an empty or
randomly initialized network as `theworker02/open-reason-1b`.

## Training data

Local shards from `open-reason build --config all --seed 42 --out data/release`.
Reddit is not used.

## Eval

Compare the base checkpoint and the finetune on held-out coding, mathematics,
science, and reasoning items. Report exact-match / sandbox pass rates that were
actually measured.

## Status

Not trained in the default developer environment unless a GPU job wrote
`training/work/`.
