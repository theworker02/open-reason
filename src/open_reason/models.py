"""Core dataset models.

These models are the source of truth for JSON Schema, validation, Hugging Face
features, and the CLI. Configuration-specific fields live in `context` rather
than exploding the core record.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Domain(str, Enum):
    CODING = "coding"
    REASONING = "reasoning"
    SCIENCE = "science"
    MATHEMATICS = "mathematics"
    HUMAN = "human"


class QualityTier(str, Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"


class Difficulty(str, Enum):
    INTRODUCTORY = "introductory"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    RESEARCH = "research"


class SourceType(str, Enum):
    OPEN_SOURCE = "open_source"
    DOCUMENTATION = "documentation"
    SPECIFICATION = "specification"
    SCIENTIFIC = "scientific"
    EDUCATIONAL = "educational"
    COMMUNITY = "community"
    HUMAN_AUTHORED = "human_authored"
    SYNTHETIC = "synthetic"
    UNKNOWN = "unknown"


class EducationLevel(str, Enum):
    K5 = "k5"
    MIDDLE_SCHOOL = "middle_school"
    HIGH_SCHOOL = "high_school"
    INTRODUCTORY_COLLEGE = "introductory_college"
    UNDERGRADUATE = "undergraduate"
    GRADUATE = "graduate"
    PROFESSIONAL = "professional"
    EXPERT = "expert"
    RESEARCH = "research"


class TranslationStatus(str, Enum):
    ORIGINAL = "original"
    HUMAN_TRANSLATED = "human_translated"
    MACHINE_TRANSLATED = "machine_translated"
    MACHINE_TRANSLATED_AND_VERIFIED = "machine_translated_and_verified"


class Provenance(BaseModel):
    """Where an example came from. Unknown provenance is explicit, never implied."""

    model_config = ConfigDict(extra="forbid")

    source_type: SourceType
    source: str | None = None
    source_id: str | None = None
    source_url: str | None = None
    source_version: str | None = None
    license: str | None = None
    license_spdx: str | None = None
    commit: str | None = None
    retrieved_at: str | None = None
    derived: bool = False
    generator: str | None = None
    generator_version: str | None = None
    generated_at: str | None = None
    derived_from: str | None = None
    transformation: str | None = None
    unknown_reason: str | None = None
    trust_tier: str | None = None

    @model_validator(mode="after")
    def _consistency(self) -> Provenance:
        if self.source_type == SourceType.UNKNOWN and not self.unknown_reason:
            raise ValueError("unknown provenance must include unknown_reason")
        if self.source_type == SourceType.SYNTHETIC:
            if not self.generator:
                raise ValueError("synthetic examples must name a generator")
            if not self.generator_version:
                raise ValueError("synthetic examples must include generator_version")
        if self.source_type == SourceType.HUMAN_AUTHORED and not self.source:
            raise ValueError("human-authored examples must name a source")
        return self


class Quality(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tier: QualityTier
    verified: bool = False
    verification_method: str | None = None
    notes: list[str] = Field(default_factory=list)
    evidence_confidence: float | None = None
    score_components: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _verified_implies_method(self) -> Quality:
        if self.verified and not self.verification_method:
            raise ValueError("verified=true requires verification_method")
        if self.tier == QualityTier.S and not self.verified:
            raise ValueError("quality tier S requires verified=true")
        return self


class Evidence(BaseModel):
    """Supporting edges for a claim. Community votes never imply verified=true."""

    model_config = ConfigDict(extra="forbid")

    educational_sources: list[str] = Field(default_factory=list)
    authoritative_sources: list[str] = Field(default_factory=list)
    community_evidence: dict[str, Any] | None = None
    implementation_evidence: list[str] = Field(default_factory=list)
    verification_methods: list[str] = Field(default_factory=list)
    conflicts: list[dict[str, Any]] = Field(default_factory=list)


class TemporalValidity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    valid_from: str | None = None
    valid_until: str | None = None
    last_verified: str | None = None
    verification_version: str | None = None
    status: str | None = None  # historically_correct, currently_correct, deprecated, obsolete, version_specific, unknown


class RuntimeContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    language: str | None = None
    language_version: str | None = None
    library: str | None = None
    library_version: str | None = None
    os: str | None = None
    runtime: str | None = None
    framework: str | None = None
    api_version: str | None = None


class Verification(BaseModel):
    """Machine-check results. Never claim success that was not actually run."""

    model_config = ConfigDict(extra="forbid")

    method: str
    passed: bool | None = None
    result: str | None = None
    command: str | None = None
    tests_passed: int | None = None
    tests_failed: int | None = None
    runtime_s: float | None = None
    memory_mb: float | None = None
    exit_code: int | None = None
    compiler_version: str | None = None
    runtime_version: str | None = None
    stdout: str | None = None
    stderr: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class Example(BaseModel):
    """Shared core record for every Open Reason configuration."""

    model_config = ConfigDict(extra="forbid")

    id: str
    domain: Domain
    task_type: str
    difficulty: Difficulty
    prompt: str
    context: dict[str, Any] = Field(default_factory=dict)
    observations: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    plan: list[str] = Field(default_factory=list)
    strategy: list[str] = Field(default_factory=list)
    solution: str | None = None
    answer: str | None = None
    verification: Verification | None = None
    provenance: Provenance
    quality: Quality
    education_level: EducationLevel | None = None
    concept_id: str | None = None
    evidence: Evidence | None = None
    transformation: list[str] = Field(default_factory=list)
    temporal: TemporalValidity | None = None
    runtime: RuntimeContext | None = None
    natural_language: str = "en"
    translation_status: TranslationStatus = TranslationStatus.ORIGINAL
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id")
    @classmethod
    def _id_prefix(cls, value: str) -> str:
        if not value.startswith("or-"):
            raise ValueError("example ids must start with 'or-'")
        if len(value) < 10:
            raise ValueError("example id is too short")
        return value

    @field_validator("prompt")
    @classmethod
    def _prompt_present(cls, value: str) -> str:
        text = value.strip()
        if len(text) < 8:
            raise ValueError("prompt is too short")
        return value

    @model_validator(mode="after")
    def _has_outcome(self) -> Example:
        if not self.solution and not self.answer:
            raise ValueError("example must include solution and/or answer")
        return self

    def content_fingerprint_payload(self) -> dict[str, Any]:
        """Fields used for exact/normalized deduplication."""
        return {
            "domain": self.domain.value,
            "task_type": self.task_type,
            "prompt": self.prompt,
            "answer": self.answer or "",
            "solution": self.solution or "",
        }
