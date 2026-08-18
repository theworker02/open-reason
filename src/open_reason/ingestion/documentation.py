"""Documentation connector. Incomplete in v0.1 — no live scraping."""

from __future__ import annotations

from collections.abc import Iterator

from open_reason.ingestion import IncompleteConnector, SourcePolicy
from open_reason.models import Example


class DocumentationConnector(IncompleteConnector):
    name = "documentation"
    policy = SourcePolicy(
        source="official documentation with redistributable licenses",
        license="per-document",
        terms="Must record license and terms of use before any fetch.",
        collection_method="version-pinned HTML/text snapshot",
        allowed_usage="Only when the publisher permits dataset redistribution.",
        retention_policy="Keep snapshot hash; delete on license revocation.",
        attribution_requirements="canonical URL, version, retrieved_at",
        status="incomplete",
    )

    def iter_examples(self) -> Iterator[Example]:
        yield from super().iter_examples()
