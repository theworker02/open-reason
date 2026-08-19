"""Training and evaluation entrypoints.

Default training is a small CPU causal LM on Open Reason JSONL.
It does not invent a published 1B model and does not use AMD GPUs.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from open_reason.config import repo_root
from open_reason.io import iter_jsonl


def prepare_sft_rows(rows: list[dict]) -> list[dict]:
    """Map Open Reason examples to prompt/completion pairs. No fake labels."""
    prepared: list[dict] = []
    for row in rows:
        prompt = str(row.get("prompt") or "").strip()
        completion = str(row.get("answer") or row.get("solution") or "").strip()
        if not prompt or not completion:
            continue
        prepared.append(
            {
                "id": row.get("id"),
                "prompt": prompt,
                "completion": completion,
                "domain": row.get("domain"),
                "verified": bool((row.get("quality") or {}).get("verified")),
            }
        )
    return prepared


def run_training(*, config_path: Path, data_path: Path, smoke: bool = False) -> int:
    config_path = Path(config_path)
    data_path = Path(data_path)
    if not config_path.exists():
        print(f"missing training config: {config_path}")
        return 2
    spec = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    print(f"intended_base={spec.get('base_model')}")
    print(f"intended_hub={spec.get('hub_model_id')}")
    print("This command does not claim a 1B model unless CUDA 1B SFT actually ran.")

    from open_reason.training.causal import (
        LARGE_MODEL_DIR,
        LOCAL_MODEL_DIR,
        MEDIUM_MODEL_DIR,
        XL_MODEL_DIR,
        cuda_usable,
        docker_available,
        inside_docker,
        is_xl_name,
        maybe_upload_model,
        run_docker_training,
        train_local_causal,
    )

    model_name = str(spec.get("model_name") or "open-reason-small")
    hub_id = str(spec.get("hub_model_id") or "theworker02/open-reason-small")
    if is_xl_name(model_name) or is_xl_name(hub_id):
        out_dir = repo_root() / XL_MODEL_DIR
    elif "large" in model_name:
        out_dir = repo_root() / LARGE_MODEL_DIR
    elif "medium" in model_name:
        out_dir = repo_root() / MEDIUM_MODEL_DIR
    else:
        out_dir = repo_root() / LOCAL_MODEL_DIR
    cuda = cuda_usable()
    print(f"cuda_usable={cuda} docker={docker_available()} in_docker={inside_docker()}")
    if cuda:
        print("NVIDIA CUDA is available. 1B LoRA is not auto-started here without an explicit GPU job.")
        print("Falling through to the CPU causal LM unless OPEN_REASON_FORCE_1B=1.")

    named_cpu_size = (
        "medium" in model_name
        or "large" in model_name
        or is_xl_name(model_name)
        or is_xl_name(hub_id)
    )
    if (
        not smoke
        and not cuda
        and docker_available()
        and not inside_docker()
        and spec.get("hub_model_id") != "theworker02/open-reason-1b"
        and not named_cpu_size
    ):
        print("No NVIDIA CUDA. Preferring CPU Docker training (not AMD GPU).")
        code = run_docker_training(data_path=data_path, out_dir=out_dir)
        if code == 0 and (out_dir / "config.json").exists():
            maybe_upload_model(out_dir, hub_id)
        return code

    if not data_path.exists():
        print(f"no JSONL rows at {data_path}; build the dataset first")
        return 2

    steps = 8 if smoke else int(spec.get("steps") or 200)
    print(f"Training GPT-2-style causal LM '{model_name}' on CPU. Not AMD GPU. Not 1B.")
    size_note = None
    if is_xl_name(model_name) or is_xl_name(hub_id):
        size_note = (
            "This is an **XL** GPT-2-style causal LM (~450M parameters) trained from "
            "scratch on the Open Reason SFT split. It is larger than "
            "`theworker02/open-reason-large` and is **not** a 1B model and is **not** "
            "`theworker02/open-reason-1b`."
        )
    elif "large" in model_name:
        size_note = (
            "This is a **large** GPT-2-style causal LM trained from scratch on the "
            "Open Reason SFT split. It is larger than `theworker02/open-reason-medium` "
            "and is **not** a 1B model and is **not** `theworker02/open-reason-1b`."
        )
    elif "medium" in model_name:
        size_note = (
            "This is a **medium** GPT-2-style causal LM trained from scratch on the "
            "Open Reason SFT split. It is larger than `theworker02/open-reason-small` "
            "and is **not** a 1B model and is **not** `theworker02/open-reason-1b`."
        )
    code = train_local_causal(
        data_path=data_path,
        out_dir=out_dir,
        steps=steps,
        smoke=smoke,
        max_seq_len=int(spec.get("max_seq_len") or (64 if smoke else 128)),
        n_layer=int(spec.get("n_layer") or (2 if smoke else 4)),
        n_embd=int(spec.get("n_embd") or (64 if smoke else 128)),
        n_head=int(spec.get("n_head") or 4),
        batch_size=int(spec.get("batch_size") or (2 if smoke else 4)),
        vocab_size=int(spec.get("vocab_size") or 4096),
        hub_id=hub_id,
        card_title=f"Open Reason {model_name} (CPU)",
        size_note=size_note,
        gradient_checkpointing=bool(spec.get("gradient_checkpointing") or is_xl_name(model_name)),
        gradient_accumulation=int(spec.get("gradient_accumulation") or 1),
        learning_rate=float(spec.get("learning_rate") or 3e-4),
        save_every=int(spec.get("save_every") or (10 if is_xl_name(model_name) else 50)),
    )
    if code == 0 and not smoke:
        maybe_upload_model(out_dir, hub_id)
    return code


def evaluate_model(*, model_dir: Path, data_path: Path, limit: int = 32) -> int:
    model_dir = Path(model_dir)
    data_path = Path(data_path)
    if not model_dir.exists() or not (model_dir / "config.json").exists():
        print(f"no transformers checkpoint at {model_dir}. Train first.")
        return 2
    if not data_path.exists():
        print(f"missing eval JSONL {data_path}")
        return 2
    n = sum(1 for _ in iter_jsonl(data_path))
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
    except ImportError:
        print("transformers/torch missing; cannot load checkpoint for eval")
        return 2
    tok = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForCausalLM.from_pretrained(model_dir)
    model.eval()
    rows = list(iter_jsonl(data_path))[:limit]
    losses = []
    with torch.no_grad():
        for row in rows:
            text = str(row.get("prompt") or "") + "\n\n" + str(row.get("answer") or row.get("solution") or "")
            ids = tok(text, return_tensors="pt", truncation=True, max_length=128)
            if ids["input_ids"].shape[-1] < 4:
                continue
            out = model(**ids, labels=ids["input_ids"])
            losses.append(float(out.loss))
    report = {
        "checkpoint": str(model_dir),
        "eval_rows": n,
        "scored": len(losses),
        "mean_nll": (sum(losses) / len(losses)) if losses else None,
        "ran": True,
        "note": "NLL on prompt+answer, not exact-match. Not a 1B eval.",
    }
    print(json.dumps(report, indent=2))
    (repo_root() / "training" / "work" / "eval_metrics.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return 0 if losses else 2
