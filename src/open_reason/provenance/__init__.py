"""Provenance construction and validation."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from open_reason.models import Provenance, SourceType
from open_reason.provenance.reddit import inspect_record


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def synthetic_provenance(
    *,
    generator: str,
    generator_version: str,
    generated_at: str | None = None,
    derived_from: str | None = None,
    license_spdx: str = "Apache-2.0",
    transformation: str | None = None,
    trust_tier: str | None = "tier7_synthetic",
    source_id: str | None = None,
) -> Provenance:
    return Provenance(
        source_type=SourceType.SYNTHETIC,
        source=generator,
        source_id=source_id,
        license="Apache License 2.0",
        license_spdx=license_spdx,
        derived=derived_from is not None,
        generator=generator,
        generator_version=generator_version,
        generated_at=generated_at or utc_now(),
        derived_from=derived_from,
        transformation=transformation,
        trust_tier=trust_tier,
    )


def human_provenance(
    *,
    source: str,
    source_id: str | None = None,
    license_spdx: str = "Apache-2.0",
    retrieved_at: str | None = None,
) -> Provenance:
    return Provenance(
        source_type=SourceType.HUMAN_AUTHORED,
        source=source,
        source_id=source_id,
        license="Apache License 2.0",
        license_spdx=license_spdx,
        retrieved_at=retrieved_at or utc_now(),
        derived=False,
        trust_tier="tier6_human_authored",
    )


def unknown_provenance(reason: str) -> Provenance:
    return Provenance(
        source_type=SourceType.UNKNOWN,
        unknown_reason=reason,
    )


def reject_if_reddit(record: dict[str, Any]) -> None:
    hits = inspect_record(record)
    if hits:
        joined = ", ".join(hits)
        raise ValueError(f"Reddit-derived material is forbidden: {joined}")
