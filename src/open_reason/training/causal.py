"""Train a small causal LM on Open Reason SFT rows.

This is a real Hugging Face `transformers` GPT-2-style model trained from
scratch on CPU (Docker or host). It is not TinyLlama and must not be uploaded
as `theworker02/open-reason-1b`.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from open_reason.config import repo_root
from open_reason.io import iter_jsonl

TRAIN_IMAGE = "open-reason-train:cpu"
LOCAL_MODEL_DIR = Path("training/work/open-reason-local")
LOCAL_HUB_ID = "theworker02/open-reason-small"
MEDIUM_HUB_ID = "theworker02/open-reason-medium"
MEDIUM_MODEL_DIR = Path("training/work/open-reason-medium")
LARGE_HUB_ID = "theworker02/open-reason-large"
LARGE_MODEL_DIR = Path("training/work/open-reason-large")


def inside_docker() -> bool:
    if os.environ.get("OPEN_REASON_IN_DOCKER") == "1":
        return True
    return Path("/.dockerenv").exists()


def docker_available() -> bool:
    return shutil.which("docker") is not None


def cuda_usable() -> bool:
    """NVIDIA CUDA only. AMD GPUs / ROCm / DirectML are not a training path."""
    if os.environ.get("OPEN_REASON_DISABLE_CUDA") == "1":
        return False
    try:
        import torch
    except ImportError:
        return False
    if not torch.cuda.is_available():
        return False
    try:
        name = torch.cuda.get_device_name(0).lower()
    except Exception:
        name = ""
    if "amd" in name or "radeon" in name or "hip" in name:
        print("AMD GPU detected; refusing CUDA/ROCm training. Use CPU Docker or host CPU.")
        return False
    return True


def docker_train_argv(*, repo: Path, data: Path, out: Path) -> list[str]:
    data_abs = data if data.is_absolute() else (repo / data)
    out_abs = out if out.is_absolute() else (repo / out)
    release_dir = data_abs.parent if data_abs.is_file() else data_abs
    work_dir = out_abs.parent if out_abs.name == "open-reason-local" else out_abs
    return [
        "docker",
        "run",
        "--rm",
        "-e",
        "OPEN_REASON_IN_DOCKER=1",
        "-e",
        "OPEN_REASON_DISABLE_CUDA=1",
        "-v",
        f"{release_dir}:/app/data/release:ro",
        "-v",
        f"{work_dir}:/app/training/work",
        "-w",
        "/app",
        TRAIN_IMAGE,
    ]


def ensure_cpu_image(repo: Path) -> int:
    dockerfile = repo / "training" / "Dockerfile"
    cmd = ["docker", "build", "-t", TRAIN_IMAGE, "-f", str(dockerfile), str(repo)]
    print(" ".join(cmd))
    return subprocess.call(cmd)


def run_docker_training(*, data_path: Path, out_dir: Path) -> int:
    repo = repo_root()
    code = ensure_cpu_image(repo)
    if code != 0:
        print("docker build failed")
        return code
    argv = docker_train_argv(repo=repo, data=data_path, out=out_dir)
    print(" ".join(argv))
    return subprocess.call(argv)


def _write_card(out_dir: Path, payload: dict) -> None:
    hub_id = payload.get("hub_id_if_uploaded") or LOCAL_HUB_ID
    title = payload.get("card_title") or "Open Reason small (CPU)"
    size_note = payload.get("size_note") or (
        "This is a **small** GPT-2-style causal LM trained from scratch on the "
        "Open Reason SFT split. It is **not** a 1B model and is **not** "
        "`theworker02/open-reason-1b`."
    )
    lines = [
        "---",
        "language:",
        "  - en",
        "license: apache-2.0",
        "library_name: transformers",
        "tags:",
        "  - open-reason",
        "  - causal-lm",
        "  - cpu",
        "datasets:",
        "  - theworker02/open-reason",
        f"base_model: {payload.get('architecture', 'gpt2-scratch')}",
        "---",
        "",
        f"# {title}",
        "",
        size_note,
        "",
        f"- Parameters: {payload.get('param_count')}",
        f"- Architecture: n_layer={payload.get('n_layer')} n_embd={payload.get('n_embd')} n_head={payload.get('n_head')}",
        f"- Steps: {payload.get('steps')}",
        f"- Backend: {payload.get('backend')}",
        f"- CUDA used: {payload.get('cuda')}",
        f"- Hardware: {payload.get('hardware') or 'CPU (Docker when available). AMD GPU is not used.'}",
        f"- Dataset: theworker02/open-reason pipeline {payload.get('dataset_version')}",
        f"- SFT rows: {payload.get('rows')}",
        f"- Final loss: {payload.get('final_loss')}",
        "",
        "Related checkpoints (none of these is a 1B model):",
        "- Dataset: https://huggingface.co/datasets/theworker02/open-reason",
        "- Small: https://huggingface.co/theworker02/open-reason-small",
        "- Medium: https://huggingface.co/theworker02/open-reason-medium",
        "- Large: https://huggingface.co/theworker02/open-reason-large",
        "",
        "No Reddit sources. Project license Apache-2.0.",
        "",
        "```python",
        "from transformers import AutoModelForCausalLM, AutoTokenizer",
        f'tok = AutoTokenizer.from_pretrained("{hub_id}")',
        f'model = AutoModelForCausalLM.from_pretrained("{hub_id}")',
        "```",
        "",
    ]
    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")
    (out_dir / "train_metrics.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def train_local_causal(
    *,
    data_path: Path,
    out_dir: Path,
    steps: int = 200,
    max_seq_len: int = 128,
    n_layer: int = 4,
    n_embd: int = 128,
    n_head: int = 4,
    batch_size: int = 4,
    vocab_size: int = 4096,
    hub_id: str = LOCAL_HUB_ID,
    card_title: str | None = None,
    size_note: str | None = None,
    smoke: bool = False,
) -> int:
    try:
        import torch
        from tokenizers import Tokenizer
        from tokenizers.models import BPE
        from tokenizers.pre_tokenizers import ByteLevel
        from tokenizers.trainers import BpeTrainer
        from transformers import GPT2Config, GPT2LMHeadModel, PreTrainedTokenizerFast
    except ImportError as exc:
        print(f"missing training dependency: {exc}")
        print("Install torch, transformers, and tokenizers. No checkpoint was written.")
        return 2

    data_path = Path(data_path)
    out_dir = Path(out_dir)
    if not data_path.exists():
        print(f"no JSONL at {data_path}; build the dataset first")
        return 2
    from open_reason.constants import PIPELINE_VERSION
    from open_reason.training import prepare_sft_rows

    rows = prepare_sft_rows(list(iter_jsonl(data_path)))
    if not rows:
        print("no prompt/completion pairs")
        return 2
    if smoke:
        rows = rows[:32]
        steps = min(steps, 8)
        n_layer, n_embd, n_head = 2, 64, 4

    texts = [f"{row['prompt']}\n\n{row['completion']}" for row in rows]
    work = out_dir.parent
    work.mkdir(parents=True, exist_ok=True)
    corpus = work / "sft_corpus.txt"
    corpus.write_text("\n".join(texts), encoding="utf-8")

    try:
        import torch as _torch

        threads = max(1, min(16, os.cpu_count() or 4))
        os.environ.setdefault("OMP_NUM_THREADS", str(threads))
        os.environ.setdefault("MKL_NUM_THREADS", str(threads))
        _torch.set_num_threads(threads)
        try:
            _torch.set_num_interop_threads(max(1, min(4, threads // 4)))
        except Exception:
            pass
        print(f"torch cpu threads={threads}")
    except Exception:
        pass

    tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
    tokenizer.pre_tokenizer = ByteLevel()
    trainer = BpeTrainer(
        vocab_size=512 if smoke else vocab_size,
        special_tokens=["[UNK]", "[PAD]", "[BOS]", "[EOS]"],
    )
    tokenizer.train([str(corpus)], trainer)
    hf_tok = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer,
        unk_token="[UNK]",
        pad_token="[PAD]",
        bos_token="[BOS]",
        eos_token="[EOS]",
    )
    vocab = hf_tok.vocab_size
    config = GPT2Config(
        vocab_size=vocab,
        n_positions=max_seq_len,
        n_ctx=max_seq_len,
        n_embd=n_embd,
        n_layer=n_layer,
        n_head=n_head,
        bos_token_id=hf_tok.bos_token_id,
        eos_token_id=hf_tok.eos_token_id,
        pad_token_id=hf_tok.pad_token_id,
    )
    model = GPT2LMHeadModel(config)
    device = torch.device("cpu")
    model.to(device)
    model.train()
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4)
    param_count = sum(p.numel() for p in model.parameters())
    print(f"architecture=gpt2-scratch params={param_count} device=cpu steps={steps} rows={len(rows)}")
    print("This is not a 1B model. AMD GPU is not used.")

    encoded = []
    for text in texts:
        ids = hf_tok.encode(text, add_special_tokens=False)
        ids = ids[: max_seq_len - 1] + [hf_tok.eos_token_id]
        if len(ids) < 8:
            continue
        encoded.append(ids)
    if not encoded:
        print("tokenization produced no sequences")
        return 2

    losses: list[float] = []
    t0 = time.time()
    for step in range(steps):
        batch_ids = []
        for offset in range(batch_size):
            seq = encoded[(step * batch_size + offset) % len(encoded)]
            batch_ids.append(seq)
        max_len = min(max_seq_len, max(len(s) for s in batch_ids))
        tensor = torch.full((len(batch_ids), max_len), hf_tok.pad_token_id, dtype=torch.long)
        for i, seq in enumerate(batch_ids):
            cut = seq[:max_len]
            tensor[i, : len(cut)] = torch.tensor(cut, dtype=torch.long)
        tensor = tensor.to(device)
        opt.zero_grad()
        out = model(input_ids=tensor, labels=tensor)
        loss = out.loss
        loss.backward()
        opt.step()
        losses.append(float(loss.detach()))
        if step % 10 == 0 or step == steps - 1:
            elapsed = time.time() - t0
            print(f"step={step} loss={losses[-1]:.4f} elapsed_s={elapsed:.1f}")

    out_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(out_dir)
    hf_tok.save_pretrained(out_dir)
    backend = "cpu-docker" if inside_docker() else "cpu-host"
    if "large" in hub_id:
        default_title = "Open Reason large (CPU)"
    elif "medium" in hub_id:
        default_title = "Open Reason medium (CPU)"
    else:
        default_title = "Open Reason small (CPU)"
    payload = {
        "smoke": smoke,
        "cuda": False,
        "backend": backend,
        "architecture": "gpt2-scratch",
        "param_count": param_count,
        "n_layer": n_layer,
        "n_embd": n_embd,
        "n_head": n_head,
        "vocab_size": vocab,
        "max_seq_len": max_seq_len,
        "steps": steps,
        "rows": len(rows),
        "dataset_version": PIPELINE_VERSION,
        "final_loss": losses[-1] if losses else None,
        "losses_tail": losses[-10:],
        "hub_id_if_uploaded": hub_id,
        "card_title": card_title or default_title,
        "size_note": size_note,
        "hardware": (
            f"Host CPU; torch {torch.__version__}; cuda_available={bool(torch.cuda.is_available())}; "
            f"docker_installed={docker_available()}; docker_used={inside_docker()}. "
            "NVIDIA CUDA was not used. AMD GPU/ROCm/DirectML were not used."
        ),
        "docker_used": inside_docker(),
        "docker_installed": docker_available(),
        "torch_version": torch.__version__,
        "note": "CPU causal LM. Not open-reason-1b. Not AMD GPU. No Reddit.",
    }
    _write_card(out_dir, payload)
    print(f"saved transformers checkpoint to {out_dir}")
    return 0


def maybe_upload_small_model(out_dir: Path) -> str | None:
    return maybe_upload_model(out_dir, LOCAL_HUB_ID)


def maybe_upload_model(out_dir: Path, hub_id: str) -> str | None:
    """Upload only a real save_pretrained directory. Never as open-reason-1b."""
    out_dir = Path(out_dir)
    hub_id = str(hub_id)
    if "1b" in hub_id.lower():
        print("refusing to upload as a 1b id from this CPU trainer")
        return None
    if not (out_dir / "config.json").exists():
        print("no config.json; refusing Hub upload")
        return None
    if not any(out_dir.glob("*.safetensors")) and not any(out_dir.glob("pytorch_model.bin")):
        print("no weight files; refusing Hub upload")
        return None
    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("huggingface_hub missing; skip upload. Manual:")
        print(f"  hf upload {hub_id} {out_dir} --repo-type model")
        return None
    api = HfApi()
    try:
        api.create_repo(hub_id, repo_type="model", exist_ok=True, private=False)
        api.upload_folder(
            folder_path=str(out_dir),
            repo_id=hub_id,
            repo_type="model",
            commit_message=f"Upload Open Reason CPU causal LM {hub_id} (not 1B)",
        )
    except Exception as exc:
        print(f"Hub upload failed: {exc}")
        print(f"Manual: hf upload {hub_id} {out_dir} --repo-type model")
        return None
    url = f"https://huggingface.co/{hub_id}"
    print(f"uploaded {url}")
    return url


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    smoke = "--smoke" in argv
    data = Path("data/release/all.jsonl")
    out = LOCAL_MODEL_DIR
    return train_local_causal(data_path=data, out_dir=out, smoke=smoke)


if __name__ == "__main__":
    raise SystemExit(main())
