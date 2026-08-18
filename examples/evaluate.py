"""Minimal evaluation stub: exact-match on answers for a JSONL split.

This script reads Open Reason *training* files only as a demo. Real evaluation
must use `benchmarks/` so labels do not leak into training subsets.
"""

from __future__ import annotations

import json
from pathlib import Path


def exact_match(path: Path) -> None:
    n = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            n += 1
    print(f"{path}: {n} rows (wire your model here; do not train on benchmarks/)")


if __name__ == "__main__":
    exact_match(Path("benchmarks/items.jsonl"))
