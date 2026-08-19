# Open Reason model training

This directory is the **training pipeline**. A 1B Hub model is **not** published
from CPU-only machines.

## Small CPU model (what this repo actually trains)

- Hub id (if upload succeeds): `theworker02/open-reason-small`
- Architecture: GPT-2-style, from scratch, ~2–8M parameters
- Data: `data/release/all.jsonl` after `open-reason build --config all --seed 42`
- Device: **CPU**. Docker CPU image when Docker is installed. **Not AMD GPU.**
- Checkpoints: `training/work/open-reason-local/`

```bash
docker build -t open-reason-train:cpu -f training/Dockerfile .
docker run --rm \
  -e OPEN_REASON_IN_DOCKER=1 \
  -e OPEN_REASON_DISABLE_CUDA=1 \
  -v "${PWD}/data/release:/app/data/release:ro" \
  -v "${PWD}/training/work:/app/training/work" \
  open-reason-train:cpu
```

Windows PowerShell:

```powershell
docker build -t open-reason-train:cpu -f training/Dockerfile .
docker run --rm `
  -e OPEN_REASON_IN_DOCKER=1 `
  -e OPEN_REASON_DISABLE_CUDA=1 `
  -v "${PWD}/data/release:/app/data/release:ro" `
  -v "${PWD}/training/work:/app/training/work" `
  open-reason-train:cpu
```

If Docker is missing, the CLI trains the same small causal LM on **host CPU**:

```bash
python training/scripts/prepare_sft.py data/release/all.jsonl training/work/sft.jsonl
open-reason train --config training/configs/open-reason-local.yaml --data data/release/all.jsonl
```

`--smoke` runs a few CPU steps of the **same** GPT-2-style model (tiny layers),
not a 1B checkpoint.

Do **not** upload this directory as `theworker02/open-reason-1b`.

## Intended 1B (CUDA only, not this machine)

- Hub id (later): `theworker02/open-reason-1b`
- Base: `TinyLlama/TinyLlama-1.1B-Chat-v1.0` (Apache-2.0)
- Requires NVIDIA CUDA (`nvidia-smi` + CUDA torch). AMD/ROCm is not used.

Eval protocol: `training/eval/protocol.yaml`.
