"""Training and evaluation entrypoints.

These prove a reproducible pipeline. They do not invent a published 1B model.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from open_reason.config import repo_root
from open_reason.io import iter_jsonl


def run_training(*, config_path: Path, data_path: Path, smoke: bool = False) -> int:
    config_path = Path(config_path)
    data_path = Path(data_path)
    if not config_path.exists():
        print(f"missing training config: {config_path}")
        return 2
    spec = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    print(f"intended_base={spec.get('base_model')}")
    print(f"intended_hub={spec.get('hub_model_id')}")
    print("This command does not upload to Hugging Face.")
    try:
        import torch
        import torch.nn as nn
    except ImportError:
        print("torch is not installed. Training pipeline is documented in training/README.md.")
        print("No metrics were written because no training ran.")
        return 2

    if not smoke and not torch.cuda.is_available():
        print("No GPU detected. Re-run with --smoke for a tiny CPU proof, or train on a GPU machine.")
        print("No 1B–3B model was trained.")
        return 2

    rows = list(iter_jsonl(data_path)) if data_path.exists() else []
    if not rows:
        print(f"no JSONL rows at {data_path}; build the dataset first")
        return 2
    subset = rows[:8] if smoke else rows
    vocab = 64
    model = nn.Sequential(nn.Embedding(vocab, 16), nn.Flatten(), nn.Linear(16 * 8, vocab))
    opt = torch.optim.SGD(model.parameters(), lr=0.05)
    loss_fn = nn.CrossEntropyLoss()
    losses: list[float] = []
    steps = 3 if smoke else 50
    for step in range(steps):
        batch = torch.randint(0, vocab, (len(subset), 8))
        target = torch.randint(0, vocab, (len(subset),))
        opt.zero_grad()
        logits = model(batch)
        loss = loss_fn(logits, target)
        loss.backward()
        opt.step()
        losses.append(float(loss.detach()))
        print(f"step={step} loss={losses[-1]:.4f} rows={len(subset)}")
    work = repo_root() / "training" / "work"
    work.mkdir(parents=True, exist_ok=True)
    payload = {
        "smoke": smoke,
        "cuda": bool(torch.cuda.is_available()),
        "steps": steps,
        "rows": len(subset),
        "losses": losses,
        "note": "Toy embedding run to prove the trainer. Not open-reason-1b.",
        "base_model_not_loaded": spec.get("base_model"),
    }
    (work / "smoke_metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {work / 'smoke_metrics.json'}")
    return 0


def evaluate_model(*, model_dir: Path, data_path: Path, limit: int = 32) -> int:
    model_dir = Path(model_dir)
    data_path = Path(data_path)
    if not model_dir.exists():
        print(f"no checkpoint at {model_dir}. Train on GPU before claiming a finetune comparison.")
        return 2
    if not data_path.exists():
        print(f"missing eval JSONL {data_path}")
        return 2
    n = sum(1 for _ in iter_jsonl(data_path))
    print(json.dumps({"checkpoint": str(model_dir), "eval_rows": n, "limit": limit, "ran": False}))
    print("Load the checkpoint with your trainer to compute real exact-match; this stub refuses fake scores.")
    return 2
