#!/usr/bin/env python3
"""Build the current release directory (atomic `all` publish)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    cmd = [
        sys.executable,
        "-m",
        "open_reason",
        "build",
        "--config",
        "all",
        "--seed",
        "42",
        "--out",
        str(ROOT / "data" / "release"),
    ]
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
