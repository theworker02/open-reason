"""Contamination reporting against known evaluation sets.

The denylist stores fingerprints and distinctive prompt prefixes, not full
benchmark answers. Hits are reported; they are not silently dropped unless
`--strict` is set.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from open_reason.config import repo_root
from open_reason.models import Example
from open_reason.normalization import normalize_prompt_key


@dataclass
class ContaminationHit:
    example_id: str
    benchmark: str
    reason: str


@dataclass
class ContaminationReport:
    checked: int = 0
    hits: list[ContaminationHit] = field(default_factory=list)

    @property
    def hit_count(self) -> int:
        return len(self.hits)

    def as_dict(self) -> dict[str, Any]:
        return {
            "checked": self.checked,
            "hit_count": self.hit_count,
            "rate": (len(self.hits) / self.checked) if self.checked else 0.0,
            "hits": [
                {"id": hit.example_id, "benchmark": hit.benchmark, "reason": hit.reason}
                for hit in self.hits
            ],
        }


def load_denylist(path: Path | None = None) -> dict[str, Any]:
    path = path or (repo_root() / "configs" / "denylist.yaml")
    if not path.exists():
        return {"benchmarks": []}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {"benchmarks": []}


def scan_examples(examples: list[Example], denylist: dict[str, Any] | None = None) -> ContaminationReport:
    denylist = denylist or load_denylist()
    report = ContaminationReport()
    prefixes: list[tuple[str, str]] = []
    needles: list[tuple[str, str]] = []
    for bench in denylist.get("benchmarks", []):
        name = str(bench.get("name", "unknown"))
        for prefix in bench.get("prompt_prefixes", []) or []:
            prefixes.append((name, normalize_prompt_key(str(prefix))))
        for needle in bench.get("needles", []) or []:
            needles.append((name, str(needle).lower()))

    for example in examples:
        report.checked += 1
        key = normalize_prompt_key(example.prompt)
        lowered = example.prompt.lower()
        for name, prefix in prefixes:
            if prefix and (key.startswith(prefix) or prefix in key):
                report.hits.append(
                    ContaminationHit(example.id, name, f"prompt prefix overlap: {prefix[:80]}")
                )
        for name, needle in needles:
            if needle and needle in lowered:
                report.hits.append(
                    ContaminationHit(example.id, name, f"needle overlap: {needle[:80]}")
                )
    return report
