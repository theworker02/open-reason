#!/usr/bin/env python3
"""Fail if Reddit source patterns appear outside documented policy text."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    ROOT / "docs" / "data-sources.md",
    ROOT / "docs" / "architecture.md",
    ROOT / "README.md",
    ROOT / "DATA_CARD.md",
    ROOT / "CHANGELOG.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "configs" / "sources.yaml",
    ROOT / "configs" / "denylist.yaml",
    ROOT / "src" / "open_reason" / "constants.py",
    ROOT / "src" / "open_reason" / "provenance" / "reddit.py",
    ROOT / "src" / "open_reason" / "cli.py",
    ROOT / "src" / "open_reason" / "sources" / "catalog.py",
    ROOT / "tests" / "test_reddit.py",
    ROOT / "tests" / "test_sources.py",
    ROOT / "tests" / "test_catalog.py",
    ROOT / "scripts" / "check_no_reddit.py",
    ROOT / "sources" / "registry.yaml",
    ROOT / "src" / "open_reason" / "sources" / "__init__.py",
}

# Policy catalogs that enumerate forbidden hosts (they are the exclusion).
ALLOWED_DIRS = (
    ROOT / "sources" / "prohibited",
    ROOT / "sources" / "restricted",
)

NEEDLES = ("reddit.com", "redd.it", "pushshift")


def _is_allowed(path: Path) -> bool:
    resolved = path.resolve()
    if resolved in {p.resolve() for p in ALLOWED} or path.name == "reddit.py":
        return True
    return any(resolved.is_relative_to(directory.resolve()) for directory in ALLOWED_DIRS)


def main() -> int:
    failed = []
    for path in ROOT.rglob("*"):
        if path.suffix.lower() not in {".py", ".md", ".yaml", ".yml", ".json", ".jsonl"}:
            continue
        if any(part in {".git", ".venv", "data"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        if not any(needle in text for needle in NEEDLES):
            continue
        if _is_allowed(path):
            continue
        failed.append(path)
    if failed:
        print("Unexpected Reddit references:")
        for path in failed:
            print(f"  {path}")
        return 1
    print("Reddit source check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
