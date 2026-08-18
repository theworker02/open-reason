"""Deterministic source auto-approval.

Auto-approve is not a web scrape and is not a verbatim license grant.
It enables *original* Open Reason task generation inspired by a source's
public curriculum or documentation structure.

Hard blocks:
- Reddit
- Quora as authority
- prohibited status
- verbatim copying of NC, SA, unknown, or non-allowlisted licenses
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from open_reason.policy import evaluate_policy
from open_reason.sources import Registry, SourceRecord, load_registry, save_registry


@dataclass(frozen=True)
class ApprovalDecision:
    source_id: str
    action: str
    reason: str
    curriculum_use: bool
    verbatim: bool
    status: str
    enabled: bool


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def evaluate_source(source: SourceRecord) -> ApprovalDecision:
    verdict = evaluate_policy(source)
    action = {
        "AUTO_APPROVED": "keep" if source.id in {"open-reason-authors", "open-reason-generators"} else "approve_curriculum",
        "AUTO_REJECTED": "blocked",
        "METADATA_ONLY": "metadata_only",
        "REVIEW_REQUIRED": "skip",
    }.get(verdict.decision, "skip")
    return ApprovalDecision(
        source.id,
        action,
        verdict.reason,
        verdict.curriculum_use,
        False,
        verdict.status,
        verdict.enabled,
    )


def auto_approve(registry: Registry | None = None, *, apply: bool = False) -> list[ApprovalDecision]:
    """Evaluate every source. apply=True writes curriculum/conditional enablement."""
    registry = registry or load_registry()
    decisions = [evaluate_source(source) for source in registry.sources]
    if not apply:
        return decisions

    by_decision = {item.source_id: item for item in decisions}
    updated: list[SourceRecord] = []
    stamp = utc_now()
    for source in registry.sources:
        decision = by_decision[source.id]
        data = source.model_dump()
        if decision.action in {"blocked", "skip", "metadata_only", "keep"}:
            if decision.action == "keep":
                data["curriculum_use"] = True
                data["verbatim"] = False
            elif decision.action == "blocked":
                data["enabled"] = False
                data["curriculum_use"] = False
                data["verbatim"] = False
                data["status"] = "prohibited"
            updated.append(SourceRecord.model_validate(data))
            continue
        data["status"] = decision.status
        data["enabled"] = decision.enabled
        data["curriculum_use"] = decision.curriculum_use
        data["verbatim"] = False
        data["auto_approved"] = True
        data["auto_approval_mode"] = "curriculum"
        data["auto_approval_reason"] = decision.reason
        data["auto_approved_at"] = stamp
        updated.append(SourceRecord.model_validate(data))
    registry.sources = updated
    save_registry(registry)
    return decisions
