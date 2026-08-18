# Evidence confidence is not a claim of philosophical truth.

from __future__ import annotations

from open_reason.constants import HIGH_RISK_DOMAINS
from open_reason.models import Example, QualityTier, SourceType

AUTHORITY_BY_SOURCE = {
    SourceType.SPECIFICATION: 0.95,
    SourceType.DOCUMENTATION: 0.9,
    SourceType.SCIENTIFIC: 0.85,
    SourceType.EDUCATIONAL: 0.8,
    SourceType.HUMAN_AUTHORED: 0.75,
    SourceType.OPEN_SOURCE: 0.65,
    SourceType.SYNTHETIC: 0.55,
    SourceType.COMMUNITY: 0.35,
    SourceType.UNKNOWN: 0.1,
}


def evidence_components(example: Example) -> dict[str, float]:
    authority = AUTHORITY_BY_SOURCE.get(example.provenance.source_type, 0.4)
    verified = (
        example.quality.verified
        and example.verification is not None
        and example.verification.passed is True
    )
    verification = 1.0 if verified else 0.0

    evidence = example.evidence
    independent = 0
    if evidence:
        independent += len(evidence.educational_sources)
        independent += len(evidence.authoritative_sources)
        independent += len(evidence.implementation_evidence)
        independent += len(evidence.verification_methods)
        if evidence.community_evidence:
            independent += 1
    cross_source = min(independent / 4.0, 1.0)

    community = 0.0
    if evidence and isinstance(evidence.community_evidence, dict):
        score = evidence.community_evidence.get("score")
        accepted = bool(evidence.community_evidence.get("accepted"))
        try:
            community = min(max(float(score or 0) / 200.0, 0.0), 0.45)
        except (TypeError, ValueError):
            community = 0.2 if accepted else 0.1
        if accepted:
            community = min(community + 0.1, 0.5)
        # Community signals inform scoring only. They never imply verified=true.

    recency = 0.55
    if example.temporal and example.temporal.last_verified:
        recency = 0.85
    elif example.provenance.retrieved_at or example.provenance.generated_at:
        recency = 0.7

    provenance = 0.3
    if example.provenance.license_spdx:
        provenance += 0.35
    if example.provenance.source or example.provenance.generator:
        provenance += 0.2
    if example.provenance.source_type != SourceType.UNKNOWN:
        provenance += 0.15
    provenance = min(provenance, 1.0)

    return {
        "authority_score": round(authority, 4),
        "verification_score": round(verification, 4),
        "cross_source_score": round(cross_source, 4),
        "community_score": round(community, 4),
        "recency_score": round(recency, 4),
        "provenance_score": round(provenance, 4),
    }


def evidence_confidence(components: dict[str, float]) -> float:
    weights = {
        "authority_score": 0.22,
        "verification_score": 0.28,
        "cross_source_score": 0.18,
        "community_score": 0.08,
        "recency_score": 0.08,
        "provenance_score": 0.16,
    }
    total = sum(components[key] * weight for key, weight in weights.items())
    return round(min(max(total, 0.0), 1.0), 4)


def apply_evidence_score(example: Example) -> Example:
    components = evidence_components(example)
    data = example.model_dump()
    quality = dict(data["quality"])
    quality["score_components"] = components
    quality["evidence_confidence"] = evidence_confidence(components)
    # Community votes never flip verified.
    if quality.get("verification_method") in {"community_votes", "accepted_answer", "upvotes"}:
        quality["verified"] = False
        if quality.get("tier") == QualityTier.S.value:
            quality["tier"] = QualityTier.A.value
    data["quality"] = quality
    return Example.model_validate(data)


def high_risk_domain(example: Example) -> str | None:
    meta = example.metadata or {}
    context = example.context or {}
    candidate = meta.get("high_risk_domain") or context.get("high_risk_domain")
    if isinstance(candidate, str) and candidate in HIGH_RISK_DOMAINS:
        return candidate
    return None
