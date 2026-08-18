"""Dataset statistics for releases and Hugging Face cards."""

from __future__ import annotations

from collections import Counter
from typing import Any

from open_reason.models import Example, SourceType


def summarize(examples: list[Example], *, config: str) -> dict[str, Any]:
    total = len(examples)
    by_domain = Counter(ex.domain.value for ex in examples)
    by_task = Counter(ex.task_type for ex in examples)
    by_difficulty = Counter(ex.difficulty.value for ex in examples)
    by_tier = Counter(ex.quality.tier.value for ex in examples)
    by_source = Counter(ex.provenance.source_type.value for ex in examples)
    by_license = Counter(ex.provenance.license_spdx or "missing" for ex in examples)
    by_language = Counter(
        str((ex.context or {}).get("language") or "n/a") for ex in examples
    )
    by_education = Counter(
        (ex.education_level.value if ex.education_level else "unspecified") for ex in examples
    )
    by_source_id = Counter(
        (ex.provenance.source_id or ex.provenance.source or ex.provenance.generator or "missing")
        for ex in examples
    )
    verified = sum(1 for ex in examples if ex.quality.verified)
    synthetic = sum(1 for ex in examples if ex.provenance.source_type == SourceType.SYNTHETIC)
    human = sum(1 for ex in examples if ex.provenance.source_type == SourceType.HUMAN_AUTHORED)
    source_derived = sum(
        1
        for ex in examples
        if ex.provenance.source_type
        in {
            SourceType.OPEN_SOURCE,
            SourceType.DOCUMENTATION,
            SourceType.SPECIFICATION,
            SourceType.SCIENTIFIC,
            SourceType.EDUCATIONAL,
            SourceType.COMMUNITY,
        }
    )
    return {
        "config": config,
        "total_examples": total,
        "verified_examples": verified,
        "synthetic_examples": synthetic,
        "human_authored_examples": human,
        "source_derived_examples": source_derived,
        "by_domain": dict(by_domain),
        "by_task_type": dict(by_task),
        "by_difficulty": dict(by_difficulty),
        "by_education_level": dict(by_education),
        "by_quality_tier": dict(by_tier),
        "by_source_type": dict(by_source),
        "by_source": dict(by_source_id),
        "by_license": dict(by_license),
        "by_language": dict(by_language),
    }


def markdown_table(counter: dict[str, Any], header: str) -> str:
    lines = [f"| {header} | count |", "| --- | ---: |"]
    for key, value in sorted(counter.items(), key=lambda kv: (-int(kv[1]), str(kv[0]))):
        lines.append(f"| {key} | {value} |")
    return "\n".join(lines)


def render_markdown(summary: dict[str, Any]) -> str:
    parts = [
        f"## Statistics (`{summary.get('config', '?')}`)",
        "",
        f"- Total examples: **{summary.get('total_examples', 0)}**",
        f"- Verified: {summary.get('verified_examples', 0)}",
        f"- Synthetic: {summary.get('synthetic_examples', 0)}",
        f"- Human-authored: {summary.get('human_authored_examples', 0)}",
        f"- Source-derived: {summary.get('source_derived_examples', 0)}",
        "",
        markdown_table(summary.get("by_domain") or {}, "domain"),
        "",
        markdown_table(summary.get("by_quality_tier") or {}, "quality"),
        "",
        markdown_table(summary.get("by_difficulty") or {}, "difficulty"),
        "",
        markdown_table(summary.get("by_education_level") or {}, "education_level"),
        "",
        markdown_table(summary.get("by_source_type") or {}, "source_type"),
        "",
        markdown_table(summary.get("by_source") or {}, "source"),
        "",
        markdown_table(summary.get("by_task_type") or {}, "task_type"),
        "",
        markdown_table(summary.get("by_license") or {}, "license"),
        "",
        markdown_table(summary.get("by_language") or {}, "language"),
        "",
    ]
    return "\n".join(parts)
