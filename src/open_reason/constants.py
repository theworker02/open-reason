"""Stable identifiers, configuration names, and policy constants."""

from __future__ import annotations

PIPELINE_NAME = "open-reason"
PIPELINE_VERSION = "1.0.1"
DATASET_NAME = "open-reason"
SCHEMA_VERSION = "1.0.1"

CURRENT_CONFIGS = (
    "coding",
    "reasoning",
    "science",
    "mathematics",
    "human",
    "education",
    "core",
    "verified",
    "all",
)

FUTURE_CONFIGS = (
    "systems",
    "languages",
    "research",
    "planning",
    "technical",
    "multilingual",
)

DOMAINS = (
    "coding",
    "reasoning",
    "science",
    "mathematics",
    "human",
)

QUALITY_TIERS = ("S", "A", "B", "C")

DIFFICULTY_LEVELS = (
    "introductory",
    "beginner",
    "intermediate",
    "advanced",
    "expert",
    "research",
)

SOURCE_TYPES = (
    "open_source",
    "documentation",
    "specification",
    "scientific",
    "educational",
    "community",
    "human_authored",
    "synthetic",
    "unknown",
)

EDUCATION_LEVELS = (
    "k5",
    "middle_school",
    "high_school",
    "introductory_college",
    "undergraduate",
    "graduate",
    "professional",
    "expert",
    "research",
)

SOURCE_ADMISSION = (
    "approved",
    "conditionally_approved",
    "metadata_only",
    "prohibited",
    "review_required",
)

TRUST_TIERS = (
    "tier0_verification",
    "tier1_authoritative",
    "tier2_educational",
    "tier3_scientific",
    "tier4_community",
    "tier5_implementation",
    "tier6_human_authored",
    "tier7_synthetic",
)

HIGH_RISK_DOMAINS = (
    "medicine",
    "law",
    "finance",
    "cybersecurity_offensive",
    "physical_safety",
    "electrical_safety",
    "chemical_procedures",
)

QUORA_POLICY = (
    "Quora is not a primary source of truth for Open Reason. Popularity "
    "metrics are not a substitute for verification."
)

CODING_LANGUAGES = (
    "python",
    "javascript",
    "typescript",
    "rust",
    "go",
    "c",
    "cpp",
    "java",
    "csharp",
    "ruby",
    "php",
    "swift",
    "kotlin",
    "dart",
    "lua",
    "julia",
    "r",
    "zig",
    "haskell",
    "ocaml",
    "elixir",
    "shell",
    "sql",
    "wasm",
)

DEFAULT_SEED = 42

# Absolute policy: Reddit is never a permitted source.
REDDIT_POLICY = (
    "Open Reason does not use Reddit as a data source. Reddit posts, comments, "
    "subreddit dumps, APIs, archives, Reddit-derived datasets, and third-party "
    "datasets whose provenance includes Reddit are rejected."
)
