"""Report knowledge-graph coverage for a JSONL file or a generated config."""

from __future__ import annotations

import json
from pathlib import Path

from open_reason.coverage import analyze_coverage
from open_reason.generation import generate_config
from open_reason.io import iter_jsonl, record_to_example


def main() -> None:
    path = Path("data/release/education.jsonl")
    if path.exists():
        examples = [record_to_example(row) for row in iter_jsonl(path)]
    else:
        examples = generate_config("education", seed=42)
    print(json.dumps(analyze_coverage(examples), indent=2))


if __name__ == "__main__":
    main()
