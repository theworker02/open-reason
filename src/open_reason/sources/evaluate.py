"""Structured source evaluation used by `open-reason evaluate-sources`."""

from __future__ import annotations

from typing import Any

from open_reason.policy import evaluate_policy
from open_reason.sources import load_registry


def evaluate_all_sources(root=None) -> list[dict[str, Any]]:
    registry = load_registry(root)
    reports: list[dict[str, Any]] = []
    for source in registry.sources:
        verdict = evaluate_policy(source, root=root)
        payload = verdict.as_dict()
        payload["name"] = source.name
        payload["category"] = source.category
        payload["license_spdx"] = source.license_spdx
        payload["scores"] = verdict.explanation
        reports.append(payload)
    return reports
