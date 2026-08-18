"""Discover candidate sources. Never ingest. Never consider Reddit."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from open_reason.config import repo_root
from open_reason.policy import evaluate_policy
from open_reason.sources import load_registry


@dataclass
class DiscoveryScore:
    source_id: str
    authority: float
    educational_quality: float
    license_clarity: float
    technical_relevance: float
    maintenance: float
    freshness: float
    structuredness: float
    originality: float
    verification_potential: float

    @property
    def total(self) -> float:
        parts = [
            self.authority,
            self.educational_quality,
            self.license_clarity,
            self.technical_relevance,
            self.maintenance,
            self.freshness,
            self.structuredness,
            self.originality,
            self.verification_potential,
        ]
        return sum(parts) / len(parts)

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "total": round(self.total, 3),
            "authority": self.authority,
            "educational_quality": self.educational_quality,
            "license_clarity": self.license_clarity,
            "technical_relevance": self.technical_relevance,
            "maintenance": self.maintenance,
            "freshness": self.freshness,
            "structuredness": self.structuredness,
            "originality": self.originality,
            "verification_potential": self.verification_potential,
            "ingest": False,
            "note": "Discovery only. Policy must approve before enablement. Never Reddit.",
        }


def score_candidate(
    source_id: str,
    *,
    authority: float,
    educational_quality: float,
    license_clarity: float,
    technical_relevance: float,
    maintenance: float = 0.5,
    freshness: float = 0.5,
    structuredness: float = 0.5,
    originality: float = 0.5,
    verification_potential: float = 0.5,
) -> DiscoveryScore:
    if "reddit" in source_id.lower():
        raise ValueError("Reddit cannot be a discovery candidate")
    if "quora" in source_id.lower():
        raise ValueError("Quora is not a primary source of truth")
    return DiscoveryScore(
        source_id=source_id,
        authority=_clip(authority),
        educational_quality=_clip(educational_quality),
        license_clarity=_clip(license_clarity),
        technical_relevance=_clip(technical_relevance),
        maintenance=_clip(maintenance),
        freshness=_clip(freshness),
        structuredness=_clip(structuredness),
        originality=_clip(originality),
        verification_potential=_clip(verification_potential),
    )


def discover_candidates(root: Path | None = None) -> list[dict[str, Any]]:
    """Score catalog + registry sources. Does not write examples or scrape."""
    root = root or repo_root()
    catalog_path = root / "configs" / "discovery_catalog.yaml"
    raw = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw.get("candidates") or []:
        source_id = str(item["id"])
        if "reddit" in source_id.lower():
            continue
        score = score_candidate(
            source_id,
            authority=float(item.get("authority") or 0.5),
            educational_quality=float(item.get("educational_quality") or 0.5),
            license_clarity=float(item.get("license_clarity") or 0.5),
            technical_relevance=float(item.get("technical_relevance") or 0.5),
            verification_potential=float(item.get("verification_potential") or 0.5),
            structuredness=0.7 if item.get("kind") in {"official_docs", "standards"} else 0.5,
            originality=0.9,
        )
        rows.append({**score.as_dict(), "kind": item.get("kind"), "license_hint": item.get("license_hint")})
        seen.add(source_id)

    registry = load_registry(root)
    for source in registry.sources:
        if source.id in seen or "reddit" in source.id or "quora" in source.id:
            continue
        verdict = evaluate_policy(source, root=root)
        score = score_candidate(
            source.id,
            authority=verdict.explanation.get("authority", 0.5),
            educational_quality=verdict.explanation.get("educational", 0.5),
            license_clarity=verdict.explanation.get("license", 0.5),
            technical_relevance=verdict.explanation.get("technical", 0.5),
            verification_potential=verdict.explanation.get("verification", 0.5),
        )
        rows.append({**score.as_dict(), "kind": source.category, "policy": verdict.decision})
    rows.sort(key=lambda row: (-float(row["total"]), str(row["source_id"])))
    return rows


def _clip(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
