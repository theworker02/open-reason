"""Schema, license, provenance, content, and PII validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import ValidationError

from open_reason.constants import HIGH_RISK_DOMAINS, QUORA_POLICY
from open_reason.models import Example, QualityTier, SourceType
from open_reason.pii import pii_hits
from open_reason.provenance.licenses import evaluate_license
from open_reason.provenance.quora import inspect_quora
from open_reason.provenance.reddit import inspect_record
from open_reason.scoring import high_risk_domain


@dataclass
class ValidationIssue:
    code: str
    message: str
    path: str | None = None


@dataclass
class ValidationResult:
    ok: bool
    issues: list[ValidationIssue] = field(default_factory=list)

    def add(self, code: str, message: str, path: str | None = None) -> None:
        self.issues.append(ValidationIssue(code, message, path))
        self.ok = False


def validate_record(record: dict[str, Any], *, strict: bool = False) -> tuple[Example | None, ValidationResult]:
    result = ValidationResult(ok=True)
    example: Example | None = None

    reddit = inspect_record(record)
    if reddit:
        result.add("reddit", f"Reddit-derived material is forbidden: {', '.join(reddit)}")
        return None, result

    quora = inspect_quora(record)
    if quora:
        result.add("quora", QUORA_POLICY + f" ({', '.join(quora)})")
        return None, result

    try:
        example = Example.model_validate(record)
    except ValidationError as exc:
        for err in exc.errors():
            loc = ".".join(str(part) for part in err.get("loc", ()))
            result.add("schema", err.get("msg", "invalid"), loc)
        return None, result

    license_decision = evaluate_license(example.provenance.license_spdx)
    if example.provenance.source_type != SourceType.UNKNOWN and not license_decision.allowed:
        result.add("license", license_decision.reason, "provenance.license_spdx")

    if example.quality.verified:
        if example.verification is None or example.verification.passed is not True:
            result.add(
                "verification",
                "quality.verified is true but verification.passed is not true",
                "quality.verified",
            )
        method = (example.quality.verification_method or "").lower()
        if method in {"community_votes", "accepted_answer", "upvotes", "views"}:
            result.add(
                "community_not_verification",
                "community signals cannot set quality.verified",
                "quality.verification_method",
            )

    risk = high_risk_domain(example)
    if risk and risk in HIGH_RISK_DOMAINS and example.quality.tier == QualityTier.S:
        has_auth = bool(example.evidence and example.evidence.authoritative_sources)
        executed = bool(example.verification and example.verification.passed is True)
        if not (has_auth and executed):
            result.add(
                "high_risk",
                "high-risk domain cannot be tier S without authoritative "
                "evidence and independent verification",
                "quality.tier",
            )

    if example.quality.tier == QualityTier.S:
        if example.provenance.source_type == SourceType.UNKNOWN:
            result.add("provenance", "tier S forbids unknown provenance", "provenance")

    blobs = [example.prompt, example.solution or "", example.answer or ""]
    blobs.extend(example.observations)
    blobs.extend(example.constraints)
    for blob in blobs:
        hits = pii_hits(blob)
        if hits:
            result.add("pii", f"possible PII: {', '.join(hits)}")

    language = (example.context or {}).get("language")
    if example.domain.value == "coding" and not language:
        result.add("language", "coding examples must set context.language")

    if strict and example.provenance.source_type == SourceType.UNKNOWN:
        result.add("provenance", "unknown provenance rejected in strict mode")

    return example, result
