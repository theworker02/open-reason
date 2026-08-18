"""Machine-readable source policy engine.

Decisions: AUTO_APPROVED | AUTO_REJECTED | METADATA_ONLY | REVIEW_REQUIRED.
Reddit is always AUTO_REJECTED. Verbatim copying stays false while no crawler exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

from open_reason.config import repo_root
from open_reason.constants import REDDIT_POLICY
from open_reason.sources import SourceRecord

Decision = Literal["AUTO_APPROVED", "AUTO_REJECTED", "METADATA_ONLY", "REVIEW_REQUIRED"]

_POLICY: dict[str, Any] | None = None


def policy_path(root: Path | None = None) -> Path:
    return (root or repo_root()) / "configs" / "source_policy.yaml"


def load_source_policy(root: Path | None = None) -> dict[str, Any]:
    global _POLICY
    if _POLICY is not None and root is None:
        return _POLICY
    payload = yaml.safe_load(policy_path(root).read_text(encoding="utf-8")) or {}
    if str(payload.get("reddit") or "").lower() != "prohibited":
        raise ValueError("source policy must set reddit: prohibited")
    if root is None:
        _POLICY = payload
    return payload


@dataclass(frozen=True)
class PolicyVerdict:
    source_id: str
    decision: Decision
    enabled: bool
    curriculum_use: bool
    verbatim: bool
    status: str
    reason: str
    rule_id: str
    explanation: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "decision": self.decision,
            "enabled": self.enabled,
            "curriculum_use": self.curriculum_use,
            "verbatim": False,
            "status": self.status,
            "reason": self.reason,
            "rule_id": self.rule_id,
            "explanation": self.explanation,
        }


def evaluate_policy(source: SourceRecord, *, root: Path | None = None) -> PolicyVerdict:
    policy = load_source_policy(root)
    sid = source.id
    lowered = sid.lower()
    scores = _dimension_scores(source)

    if "reddit" in lowered or sid == "quora" or source.reddit_allowed:
        return PolicyVerdict(
            sid,
            "AUTO_REJECTED",
            False,
            False,
            False,
            "prohibited",
            REDDIT_POLICY if "reddit" in lowered else "Quora is not a primary source of truth.",
            "forbidden",
            {**scores, "overall": 0.0, "reddit": 1.0, "risk": 1.0},
        )

    for rule in policy.get("rules") or []:
        ids = {(item or "").strip() for item in (rule.get("match") or {}).get("ids") or []}
        if sid in ids or sid.replace("-", "_") in ids:
            decision = rule["decision"]
            return PolicyVerdict(
                sid,
                decision,
                bool(rule.get("enabled")),
                bool(rule.get("curriculum_use")),
                False,
                str(rule.get("status") or source.status),
                str(rule.get("reason") or decision),
                str(rule.get("id") or "matched"),
                {**scores, "overall": _overall(scores, decision), "reddit": 0.0, "risk": scores["risk"]},
            )

    fallback = policy.get("fallback") or {}
    return PolicyVerdict(
        sid,
        fallback.get("decision") or "REVIEW_REQUIRED",
        False,
        False,
        False,
        source.status,
        str(fallback.get("reason") or "Unmatched source."),
        "fallback",
        {**scores, "overall": 0.35, "reddit": 0.0, "risk": scores["risk"]},
    )


def _dimension_scores(source: SourceRecord) -> dict[str, float]:
    authority = {"high": 0.9, "medium": 0.6, "community_validated": 0.45, "low": 0.2}.get(
        str(source.authority or "medium"), 0.5
    )
    educational = 0.8 if source.category in {"education", "documentation", "science"} else 0.5
    technical = 0.85 if source.category in {"documentation", "specification"} else 0.55
    license_clarity = 0.9 if source.license_spdx else 0.3
    provenance = 0.8 if source.license_status else 0.4
    freshness = 0.6
    structure = 0.7 if source.category in {"documentation", "specification"} else 0.5
    verification = 0.75 if source.category in {"documentation", "science", "original"} else 0.4
    risk = 0.9 if source.id in {"reddit", "quora"} else 0.15
    return {
        "authority": authority,
        "educational": educational,
        "technical": technical,
        "license": license_clarity,
        "provenance": provenance,
        "freshness": freshness,
        "structure": structure,
        "verification": verification,
        "risk": risk,
        "reddit": 1.0 if "reddit" in source.id else 0.0,
    }


def _overall(scores: dict[str, float], decision: str) -> float:
    if decision == "AUTO_REJECTED":
        return 0.0
    if decision == "METADATA_ONLY":
        return 0.35
    if decision == "REVIEW_REQUIRED":
        return 0.4
    usable = [scores[k] for k in ("authority", "educational", "technical", "license", "verification")]
    return round(sum(usable) / len(usable), 3)
