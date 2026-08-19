# Training

Open Reason trains GPT-2-style causal LMs on `data/release/all.jsonl`.
It does not invent a 1B Hugging Face model on CPU-only hardware.

| Model | Hub | Params | Config |
| --- | --- | ---: | --- |
| Small | [`theworker02/open-reason-small`](https://huggingface.co/theworker02/open-reason-small) | ~1.3M | `training/configs/open-reason-local.yaml` |
| Medium | [`theworker02/open-reason-medium`](https://huggingface.co/theworker02/open-reason-medium) | 13,867,008 | `training/configs/open-reason-medium.yaml` |
| Large | [`theworker02/open-reason-large`](https://huggingface.co/theworker02/open-reason-large) | 91,544,064 | `training/configs/open-reason-large.yaml` |
| XL | [`theworker02/open-reason-xl`](https://huggingface.co/theworker02/open-reason-xl) | 443,719,680 | `training/configs/open-reason-xl.yaml` |

```bash
python training/scripts/prepare_sft.py data/release/all.jsonl training/work/sft.jsonl
open-reason train --config training/configs/open-reason-xl.yaml --data data/release/all.jsonl
```

Prefer CPU **Docker** when Docker is installed and NVIDIA CUDA is not:

```bash
docker build -t open-reason-train:cpu -f training/Dockerfile .
docker run --rm -e OPEN_REASON_IN_DOCKER=1 -e OPEN_REASON_DISABLE_CUDA=1 \
  -e OPEN_REASON_MODEL_NAME=open-reason-medium \
  -e OPEN_REASON_HUB_ID=theworker02/open-reason-medium \
  -v "$PWD/data/release:/app/data/release:ro" \
  -v "$PWD/training/work:/app/training/work" \
  open-reason-train:cpu
```

v1.4.2 XL-model training on this developer machine used **host CPU** because
Docker was not installed and `nvidia-smi` was not present. `torch` is
2.12.0+cpu. AMD GPUs are not used. Weights are uploaded to the Hub only; they
are gitignored under `training/work/`. The XL checkpoint has 443,719,680
parameters (22×1280, vocab 8192). It is not a 1B model.

Do **not** upload these checkpoints as `theworker02/open-reason-1b`.

See `training/README.md`, `training/eval/protocol.yaml`, and the card written
next to the checkpoint after a successful train.
