# Training

Open Reason trains a **small** GPT-2-style causal LM on `data/release/all.jsonl`.
It does not invent a 1B Hugging Face model on CPU-only hardware.

```bash
python training/scripts/prepare_sft.py data/release/all.jsonl training/work/sft.jsonl
open-reason train --config training/configs/open-reason-local.yaml --data data/release/all.jsonl
```

Prefer CPU **Docker** when Docker is installed and NVIDIA CUDA is not:

```bash
docker build -t open-reason-train:cpu -f training/Dockerfile .
docker run --rm -e OPEN_REASON_IN_DOCKER=1 -e OPEN_REASON_DISABLE_CUDA=1 \
  -v "$PWD/data/release:/app/data/release:ro" \
  -v "$PWD/training/work:/app/training/work" \
  open-reason-train:cpu
```

That image is `open-reason-train:cpu`. Checkpoints write to
`training/work/open-reason-local/`. If the checkpoint is a real
`transformers` `save_pretrained` tree, it may be uploaded as
`theworker02/open-reason-small` — never as `open-reason-1b`.

This developer machine uses CPU torch (`cuda=false`). AMD GPUs are not used.

See `training/README.md`, `training/eval/protocol.yaml`, and the card written
next to the checkpoint after a successful train.
