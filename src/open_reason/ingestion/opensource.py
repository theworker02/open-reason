"""Open-source repository connector.

Status: incomplete. This module defines the snapshot contract (license, commit,
path, SPDX) but does not clone or scrape repositories in v0.1. It must not emit
examples until a reviewed source list is provided.
"""

from __future__ import annotations

from collections.abc import Iterator

from open_reason.ingestion import IncompleteConnector, SourcePolicy
from open_reason.models import Example


class OpenSourceConnector(IncompleteConnector):
    name = "open_source"
    policy = SourcePolicy(
        source="commit-pinned permissive repositories",
        license="per-file SPDX",
        terms="Only SPDX allowlisted licenses; no relicensing of copyleft as CC-BY-4.0.",
        collection_method="git snapshot at a recorded commit",
        allowed_usage="Follow original license; record attribution.",
        retention_policy="Store commit hash; drop files that fail license or Reddit checks.",
        attribution_requirements="repository, commit, path, license_spdx",
        status="incomplete",
    )

    def iter_examples(self) -> Iterator[Example]:
        yield from super().iter_examples()
