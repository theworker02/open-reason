"""Shared helpers for example construction."""

from __future__ import annotations

from typing import Any

from open_reason.constants import PIPELINE_VERSION
from open_reason.generation.difficulty import apply_difficulty
from open_reason.ids import make_example_id
from open_reason.models import (
    Difficulty,
    Domain,
    EducationLevel,
    Evidence,
    Example,
    Provenance,
    Quality,
    QualityTier,
    Verification,
)
from open_reason.normalization import normalize_example
from open_reason.scoring import apply_evidence_score


def build_example(
    *,
    domain: Domain | str,
    task_type: str,
    prompt: str,
    provenance: Provenance,
    quality: Quality,
    source_key: str,
    answer: str | None = None,
    solution: str | None = None,
    context: dict[str, Any] | None = None,
    observations: list[str] | None = None,
    constraints: list[str] | None = None,
    assumptions: list[str] | None = None,
    plan: list[str] | None = None,
    strategy: list[str] | None = None,
    verification: Verification | None = None,
    metadata: dict[str, Any] | None = None,
    difficulty: Difficulty | str = Difficulty.BEGINNER,
    education_level: EducationLevel | str | None = None,
    concept_id: str | None = None,
    evidence: Evidence | dict[str, Any] | None = None,
    transformation: list[str] | None = None,
) -> Example:
    domain_value = domain.value if isinstance(domain, Domain) else domain
    payload = {
        "domain": domain_value,
        "task_type": task_type,
        "prompt": prompt,
        "answer": answer,
        "solution": solution,
        "context": context or {},
    }
    extra_meta = {
        "pipeline_version": PIPELINE_VERSION,
        "schema_version": PIPELINE_VERSION,
        **(metadata or {}),
    }
    example = Example(
        id=make_example_id(domain_value, source_key, payload),
        domain=Domain(domain_value),
        task_type=task_type,
        difficulty=Difficulty(difficulty) if isinstance(difficulty, str) else difficulty,
        prompt=prompt,
        context=context or {},
        observations=observations or [],
        constraints=constraints or [],
        assumptions=assumptions or [],
        plan=plan or [],
        strategy=strategy if strategy is not None else (plan or []),
        solution=solution,
        answer=answer,
        verification=verification,
        provenance=provenance,
        quality=quality,
        education_level=(
            EducationLevel(education_level) if isinstance(education_level, str) else education_level
        ),
        concept_id=concept_id,
        evidence=Evidence.model_validate(evidence) if isinstance(evidence, dict) else evidence,
        transformation=transformation
        or [
            "task_generation",
            "difficulty_assignment",
            "verification" if quality.verified else "unverified",
        ],
        metadata=extra_meta,
    )
    example = normalize_example(example)
    example = apply_difficulty(example)
    return apply_evidence_score(example)


def verified_quality(method: str, notes: list[str] | None = None) -> Quality:
    return Quality(tier=QualityTier.S, verified=True, verification_method=method, notes=notes or [])


def generated_quality(method: str | None = None, notes: list[str] | None = None) -> Quality:
    _ = method  # A method name is not a check. Never set verified=true here.
    return Quality(
        tier=QualityTier.B,
        verified=False,
        verification_method=None,
        notes=notes or ["synthetic; structurally valid"],
    )


def reviewed_quality(notes: list[str] | None = None) -> Quality:
    return Quality(
        tier=QualityTier.A,
        verified=False,
        notes=notes or ["human-authored or strongly validated; not executed"],
    )
