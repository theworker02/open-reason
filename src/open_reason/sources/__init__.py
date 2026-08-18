"""Load and enforce the source registry.

Discovery is not ingestion. `enabled: true` is allowed only after license review.
Reddit cannot be enabled. Community votes never imply verification.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from open_reason.config import repo_root

ADMISSION_STATES = (
    "approved",
    "conditionally_approved",
    "metadata_only",
    "prohibited",
    "review_required",
)

SOURCE_ALIASES = {
    "khan-academy": "khan_academy_computing",
    "khan_academy": "khan_academy_computing",
    "mit-ocw": "mit_opencourseware",
    "mit_ocw": "mit_opencourseware",
    "cs50": "harvard_cs50",
    "harvard-cs50": "harvard_cs50",
    "openstax": "openstax",
    "mdn": "mdn",
    "odin": "the_odin_project",
    "the-odin-project": "the_odin_project",
    "python-docs": "python_docs",
    "stack-exchange": "stack_exchange",
    "stackoverflow": "stackoverflow",
    "stack-overflow": "stackoverflow",
    "openalex": "openalex",
    "github": "github_permissive",
}


def normalize_source_id(source_id: str) -> str:
    raw = source_id.strip().lower().replace(" ", "_")
    hyphen = raw.replace("_", "-")
    underscore = raw.replace("-", "_")
    return SOURCE_ALIASES.get(hyphen) or SOURCE_ALIASES.get(underscore) or underscore


class SourceRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    category: str
    trust_tier: int | None = None
    domains: list[str] = Field(default_factory=list)
    authority: str | None = None
    license: str | None = None
    license_spdx: str | None = None
    license_status: str | None = None
    redistribution: str | None = None
    commercial: str | None = None
    derivatives: str | None = None
    share_alike: Any = None
    attribution_required: Any = None
    reddit_allowed: bool = False
    status: str
    enabled: bool = False
    curriculum_use: bool = False
    verbatim: bool = False
    auto_approved: bool = False
    auto_approval_mode: str | None = None
    auto_approval_reason: str | None = None
    auto_approved_at: str | None = None
    extraction_method: list[str] = Field(default_factory=list)
    notes: str | None = None
    parent: str | None = None

    @model_validator(mode="after")
    def _enforce_hard_rules(self) -> SourceRecord:
        if self.reddit_allowed:
            raise ValueError(f"{self.id}: reddit_allowed must be false")
        if self.id in {"reddit", "quora"} and self.enabled:
            raise ValueError(f"{self.id} cannot be enabled")
        if self.status == "prohibited" and self.enabled:
            raise ValueError(f"{self.id}: prohibited sources cannot be enabled")
        if self.enabled and self.status not in {"approved", "conditionally_approved"}:
            raise ValueError(
                f"{self.id}: enabled=true requires approved or "
                f"conditionally_approved, not {self.status}"
            )
        return self


class RegistryPolicy(BaseModel):
    model_config = ConfigDict(extra="allow")

    reddit: str = "prohibited"
    quora_as_authority: str = "prohibited"
    auto_ingest_discovered: bool = False
    community_votes_are_not_verification: bool = True
    auto_approve_curriculum: bool = True


@dataclass
class Registry:
    policy: RegistryPolicy
    sources: list[SourceRecord]
    raw: dict[str, Any]

    def by_id(self, source_id: str) -> SourceRecord:
        wanted = normalize_source_id(source_id)
        for source in self.sources:
            if source.id == wanted or source.id.replace("_", "-") == wanted.replace("_", "-"):
                return source
        raise KeyError(source_id)

    def enabled(self) -> list[SourceRecord]:
        return [source for source in self.sources if source.enabled]


def registry_path(root: Path | None = None) -> Path:
    return (root or repo_root()) / "sources" / "registry.yaml"


def load_registry(root: Path | None = None) -> Registry:
    path = registry_path(root)
    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}
    policy = RegistryPolicy.model_validate(raw.get("policy") or {})
    sources = [SourceRecord.model_validate(item) for item in raw.get("sources") or []]
    if policy.reddit != "prohibited":
        raise ValueError("registry policy.reddit must be prohibited")
    return Registry(policy=policy, sources=sources, raw=raw)


def save_registry(registry: Registry, root: Path | None = None) -> Path:
    """Write registry YAML. Comments are not preserved."""
    path = registry_path(root)
    payload = dict(registry.raw)
    payload["policy"] = {
        **(payload.get("policy") or {}),
        **registry.policy.model_dump(mode="json"),
    }
    by_id = {source.id: source.model_dump(mode="json") for source in registry.sources}
    written: list[dict[str, Any]] = []
    for item in payload.get("sources") or []:
        source_id = item.get("id")
        if source_id in by_id:
            item = {**item, **_public_source_fields(by_id[source_id])}
        written.append(item)
    payload["sources"] = written
    header = (
        "# Open Reason source registry\n"
        "# Discovery is not ingestion. Auto-approve enables original curriculum tasks only.\n"
        "# Open Reason does not use Reddit as a data source.\n"
        "# Verbatim third-party copying still requires an explicit license review.\n\n"
    )
    path.write_text(header + yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def _public_source_fields(dumped: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "status",
        "enabled",
        "curriculum_use",
        "verbatim",
        "auto_approved",
        "auto_approval_mode",
        "auto_approval_reason",
        "auto_approved_at",
    )
    return {key: dumped.get(key) for key in keys}


def assert_can_ingest(source_id: str, root: Path | None = None) -> SourceRecord:
    """Hard gate: unreviewed, prohibited, and disabled sources emit nothing."""
    registry = load_registry(root)
    lowered = source_id.lower().replace("_", "-")
    if "reddit" in lowered:
        raise SourceAdmissionError("Open Reason does not use Reddit as a data source.")
    if lowered in {"quora"} or "quora" in lowered:
        raise SourceAdmissionError("Quora is not a primary source of truth and is not enabled.")
    try:
        source = registry.by_id(source_id)
    except KeyError as exc:
        raise SourceAdmissionError(f"Unknown source '{source_id}'.") from exc
    if not source.enabled:
        raise SourceAdmissionError(
            f"Source '{source.id}' is not enabled (status={source.status}). "
            "Discovery is not ingestion; complete license review first."
        )
    if source.status in {"prohibited", "review_required", "metadata_only"}:
        raise SourceAdmissionError(
            f"Source '{source.id}' status={source.status} forbids example emission."
        )
    return source


class SourceAdmissionError(RuntimeError):
    """Raised when a connector attempts to ingest a source that is not enabled."""

