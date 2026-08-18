"""Connector registry."""

from __future__ import annotations

from open_reason.ingestion import Connector, connector_manifest
from open_reason.ingestion.documentation import DocumentationConnector
from open_reason.ingestion.educational import EducationalConnector, StackExchangeConnector
from open_reason.ingestion.human import HumanAuthoredConnector
from open_reason.ingestion.opensource import OpenSourceConnector


def all_connectors() -> list[Connector]:
    return [
        HumanAuthoredConnector(),
        OpenSourceConnector(),
        DocumentationConnector(),
        EducationalConnector("khan_academy_computing"),
        EducationalConnector("mit_opencourseware"),
        EducationalConnector("harvard_cs50"),
        EducationalConnector("openstax"),
        EducationalConnector("mdn"),
        EducationalConnector("the_odin_project"),
        StackExchangeConnector(),
    ]


def active_connectors() -> list[Connector]:
    return [c for c in all_connectors() if c.policy.status == "active"]


def manifests() -> list[dict]:
    return [connector_manifest(c) for c in all_connectors()]
