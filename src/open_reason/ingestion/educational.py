"""Incomplete educational and community connectors.

They exist so adding Khan Academy, MIT OCW, CS50, OpenStax, MDN, Odin Project,
or Stack Exchange later does not require a rewrite. They emit zero examples
until the registry marks the source enabled after license review.
"""

from __future__ import annotations

from collections.abc import Iterator

from open_reason.ingestion import IncompleteConnector, SourcePolicy
from open_reason.models import Example
from open_reason.sources import SourceAdmissionError, assert_can_ingest


def _blocked_policy(source: str, license_name: str) -> SourcePolicy:
    return SourcePolicy(
        source=source,
        license=license_name,
        terms="Not enabled. License review required before any fetch.",
        collection_method="none_until_approved",
        allowed_usage="none",
        retention_policy="do_not_store_unreviewed_content",
        attribution_requirements="n/a until approved",
        status="incomplete",
    )


class EducationalConnector(IncompleteConnector):
    """Khan Academy / MIT OCW / CS50 / OpenStax / MDN / Odin Project gate."""

    name = "educational"
    policy = _blocked_policy("educational_oer", "review_required")

    def __init__(self, source_id: str) -> None:
        self.source_id = source_id
        self.name = f"educational:{source_id}"

    def iter_examples(self) -> Iterator[Example]:
        try:
            source = assert_can_ingest(self.source_id)
        except SourceAdmissionError:
            return
        if source.verbatim:
            yield from super().iter_examples()
            return
        from open_reason.generation.curriculum import generate_original_for_source

        yield from generate_original_for_source(source.id)


class StackExchangeConnector(IncompleteConnector):
    """Community evidence connector. Votes never set verified=true."""

    name = "stack_exchange"
    policy = _blocked_policy(
        "stack_exchange",
        "CC-BY-SA (version depends on contribution date)",
    )

    def iter_examples(self) -> Iterator[Example]:
        try:
            assert_can_ingest("stack_exchange")
        except SourceAdmissionError:
            return
        yield from super().iter_examples()
