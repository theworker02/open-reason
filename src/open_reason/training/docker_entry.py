"""CLI entry used inside the CPU training image."""

from __future__ import annotations

import os
from pathlib import Path

from open_reason.training.causal import LOCAL_HUB_ID, MEDIUM_HUB_ID, train_local_causal


def main() -> int:
    data = Path("/app/data/release/all.jsonl")
    if not data.exists():
        data = Path("data/release/all.jsonl")
    name = os.environ.get("OPEN_REASON_MODEL_NAME", "open-reason-local")
    out = Path("/app/training/work") / name
    steps = int(os.environ.get("OPEN_REASON_STEPS", "200"))
    n_layer = int(os.environ.get("OPEN_REASON_N_LAYER", "4"))
    n_embd = int(os.environ.get("OPEN_REASON_N_EMBD", "128"))
    n_head = int(os.environ.get("OPEN_REASON_N_HEAD", "4"))
    vocab = int(os.environ.get("OPEN_REASON_VOCAB", "4096"))
    seq = int(os.environ.get("OPEN_REASON_MAX_SEQ", "128"))
    batch = int(os.environ.get("OPEN_REASON_BATCH", "4"))
    hub = os.environ.get("OPEN_REASON_HUB_ID") or (
        MEDIUM_HUB_ID if "medium" in name else LOCAL_HUB_ID
    )
    return train_local_causal(
        data_path=data,
        out_dir=out,
        steps=steps,
        n_layer=n_layer,
        n_embd=n_embd,
        n_head=n_head,
        vocab_size=vocab,
        max_seq_len=seq,
        batch_size=batch,
        hub_id=hub,
    )


if __name__ == "__main__":
    raise SystemExit(main())
