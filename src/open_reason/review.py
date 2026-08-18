"""Human review queue for uncertain, conflicting, or high-risk examples."""

from __future__ import annotations

from dataclasses import dataclass, field

from open_reason.constants import HIGH_RISK_DOMAINS
from open_reason.models import Example, QualityTier, SourceType
from open_reason.scoring import high_risk_domain

REVIEW_REASONS = (
    "conflicting_sources",
    "low_confidence",
    "ambiguous_licensing",
    "high_risk_domain",
    "community_only",
    "obsolete",
    "insufficient_verification",
)


@dataclass
class ReviewItem:
    example_id: str
    reasons: list[str]
    notes: list[str] = field(default_factory=list)


def review_reasons(example: Example) -> list[str]:
    reasons: list[str] = []
    if example.evidence and example.evidence.conflicts:
        reasons.append("conflicting_sources")
    confidence = example.quality.evidence_confidence
    if confidence is not None and confidence < 0.45:
        reasons.append("low_confidence")
    if example.provenance.source_type == SourceType.UNKNOWN:
        reasons.append("ambiguous_licensing")
    risk = high_risk_domain(example)
    if risk and risk in HIGH_RISK_DOMAINS:
        reasons.append("high_risk_domain")
        if example.quality.tier == QualityTier.S:
            reasons.append("insufficient_verification")
    if example.provenance.source_type == SourceType.COMMUNITY:
        has_auth = bool(example.evidence and example.evidence.authoritative_sources)
        executed = bool(example.verification and example.verification.passed)
        if not (has_auth or executed):
            reasons.append("community_only")
    if example.temporal and example.temporal.status in {"obsolete", "deprecated"}:
        reasons.append("obsolete")
    return reasons


def enqueue(examples: list[Example]) -> list[ReviewItem]:
    queued: list[ReviewItem] = []
    for example in examples:
        reasons = review_reasons(example)
        if reasons:
            queued.append(ReviewItem(example_id=example.id, reasons=reasons))
    return queued
