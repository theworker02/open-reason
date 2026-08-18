"""Deterministic example identifiers."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def make_example_id(domain: str, source_key: str, payload: Any) -> str:
    """Build a stable id: or-{domain}-{source}-{hash12}."""
    digest = sha256_hex(canonical_json(payload))[:12]
    source = _slug(source_key)
    domain_slug = _slug(domain)
    return f"or-{domain_slug}-{source}-{digest}"


def _slug(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or "unknown"
