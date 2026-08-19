"""CLI entry used inside the CPU training image."""

from __future__ import annotations

from pathlib import Path

from open_reason.training.causal import train_local_causal


def main() -> int:
    data = Path("/app/data/release/all.jsonl")
    if not data.exists():
        data = Path("data/release/all.jsonl")
    out = Path("/app/training/work/open-reason-local")
    return train_local_causal(data_path=data, out_dir=out, steps=200)


if __name__ == "__main__":
    raise SystemExit(main())
