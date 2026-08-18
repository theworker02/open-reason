"""Map a release JSONL to prompt/completion pairs for a later SFT job."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from open_reason.io import iter_jsonl
from open_reason.training import prepare_sft_rows


def main() -> None:
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "data/release/all.jsonl")
    dest = Path(sys.argv[2] if len(sys.argv) > 2 else "training/work/sft.jsonl")
    rows = prepare_sft_rows(list(iter_jsonl(src)))
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"wrote {len(rows)} rows to {dest}")


if __name__ == "__main__":
    main()
