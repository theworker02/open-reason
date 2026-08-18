"""Inspect a local JSONL release file."""

import json
import sys
from pathlib import Path

path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/release/mathematics.jsonl")
with path.open(encoding="utf-8") as handle:
    row = json.loads(handle.readline())
print(row["id"])
print(row["prompt"])
print("answer:", row.get("answer"))
print("verified:", row["quality"])
