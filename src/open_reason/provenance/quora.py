"""Quora is not a primary source of truth."""

from __future__ import annotations

import re
from typing import Any

QUORA_RE = re.compile(r"(?i)\bquora\.com\b|\bquora\b")


def inspect_quora(record: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    provenance = record.get("provenance") or {}
    if isinstance(provenance, dict):
        for key in ("source", "source_id", "source_url", "generator"):
            value = provenance.get(key)
            if isinstance(value, str) and QUORA_RE.search(value):
                reasons.append(f"quora_provenance:{key}")
    return reasons
