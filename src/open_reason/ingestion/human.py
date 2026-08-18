"""Human-authored JSONL connector."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from open_reason.config import repo_root
from open_reason.ingestion import Connector, SourcePolicy
from open_reason.io import iter_jsonl, record_to_example
from open_reason.models import Example


class HumanAuthoredConnector(Connector):
    name = "human_authored"
    policy = SourcePolicy(
        source="open-reason authors",
        license="CC-BY-4.0",
        terms="Original examples written for Open Reason.",
        collection_method="authored_in_repository",
        allowed_usage="Redistribute with LICENSE-DATA attribution.",
        retention_policy="Keep across releases; never silently rewrite published ids.",
        attribution_requirements="Cite Open Reason.",
        status="active",
    )

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (repo_root() / "examples" / "seed")

    def iter_examples(self) -> Iterator[Example]:
        if not self.path.exists():
            return
        files = [self.path] if self.path.is_file() else sorted(self.path.glob("*.jsonl"))
        for file in files:
            for record in iter_jsonl(file):
                yield record_to_example(record)
