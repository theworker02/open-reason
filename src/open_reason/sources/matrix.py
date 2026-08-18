"""Render the source matrix from the registry. Discovery is not ingestion."""

from __future__ import annotations

from typing import Any

from open_reason.sources import Registry, SourceRecord, load_registry

MATRIX_COLUMNS = (
    "Source",
    "Domain",
    "Authority",
    "License",
    "Redistribution",
    "Commercial",
    "Attribution",
    "Derivatives",
    "Content types",
    "Status",
    "Enabled",
    "Ingestion method",
)


def row_for(source: SourceRecord) -> dict[str, Any]:
    return {
        "Source": source.name,
        "id": source.id,
        "Domain": ", ".join(source.domains) or "n/a",
        "Authority": source.authority or "n/a",
        "License": source.license_spdx or source.license or "review_required",
        "Redistribution": source.redistribution or "n/a",
        "Commercial": source.commercial or "n/a",
        "Attribution": str(source.attribution_required),
        "Derivatives": source.derivatives or "n/a",
        "Content types": ", ".join(source.extraction_method) or "n/a",
        "Status": source.status,
        "Enabled": "yes" if source.enabled else "no",
        "Ingestion method": ", ".join(source.extraction_method) or "none",
        "trust_tier": source.trust_tier,
        "notes": (source.notes or "").strip(),
    }


def render_markdown(registry: Registry | None = None) -> str:
    registry = registry or load_registry()
    lines = [
        "# Open Reason source matrix",
        "",
        "Discovery is not ingestion. `enabled: true` requires license review.",
        "**Open Reason does not use Reddit as a data source.**",
        "Quora is not a primary source of truth.",
        "",
        "| " + " | ".join(MATRIX_COLUMNS) + " |",
        "| " + " | ".join("---" for _ in MATRIX_COLUMNS) + " |",
    ]
    for source in registry.sources:
        row = row_for(source)
        lines.append(
            "| "
            + " | ".join(
                str(row[col] if col != "Source" else f"{source.name} (`{source.id}`)")
                .replace("|", "/")
                .replace("\n", " ")
                for col in MATRIX_COLUMNS
            )
            + " |"
        )
    lines.append("")
    lines.append("Educational value, technical value, verification potential, and freshness")
    lines.append("are scored during discovery and are not a license grant.")
    lines.append("")
    return "\n".join(lines)
