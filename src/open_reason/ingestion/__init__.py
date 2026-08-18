"""Ingestion connectors. Each connector declares license and collection policy."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from open_reason.models import Example


@dataclass(frozen=True)
class SourcePolicy:
    source: str
    license: str
    terms: str
    collection_method: str
    allowed_usage: str
    retention_policy: str
    attribution_requirements: str
    status: str = "active"


class Connector(ABC):
    name: str
    policy: SourcePolicy

    @abstractmethod
    def iter_examples(self) -> Iterator[Example]:
        raise NotImplementedError


class IncompleteConnector(Connector):
    """Declared source that is not yet implemented. Must not silently emit data."""

    def iter_examples(self) -> Iterator[Example]:
        if False:  # pragma: no cover
            yield  # type: ignore[misc]
        return iter(())


def connector_manifest(connector: Connector) -> dict[str, Any]:
    policy = connector.policy
    return {
        "name": connector.name,
        "source": policy.source,
        "license": policy.license,
        "terms": policy.terms,
        "collection_method": policy.collection_method,
        "allowed_usage": policy.allowed_usage,
        "retention_policy": policy.retention_policy,
        "attribution_requirements": policy.attribution_requirements,
        "status": policy.status,
    }
