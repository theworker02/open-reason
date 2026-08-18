"""Example generation entry points."""

from __future__ import annotations

from collections.abc import Callable

from open_reason.generation.coding import generate_coding
from open_reason.generation.curriculum import generate_approved_curriculum
from open_reason.generation.education import generate_education
from open_reason.generation.human import generate_human
from open_reason.generation.mathematics import generate_mathematics
from open_reason.generation.reasoning import generate_reasoning
from open_reason.generation.science import generate_science
from open_reason.models import Example, QualityTier

DOMAIN_ALIASES = {
    "programming": "coding",
    "coding": "coding",
    "math": "mathematics",
    "mathematics": "mathematics",
    "science": "science",
    "reasoning": "reasoning",
    "human": "human",
    "education": "education",
    "all": "all",
    "core": "core",
    "verified": "verified",
}

GENERATORS: dict[str, Callable[..., list[Example]]] = {
    "coding": generate_coding,
    "reasoning": generate_reasoning,
    "science": generate_science,
    "mathematics": generate_mathematics,
    "human": generate_human,
    "education": generate_education,
}


def generate_education_release(seed: int = 42) -> list[Example]:
    examples = list(generate_education(seed=seed))
    examples.extend(generate_approved_curriculum(seed=seed))
    return examples


GENERATORS["education"] = generate_education_release

BASE_CONFIGS = ("coding", "reasoning", "science", "mathematics", "human", "education")


def resolve_domain(name: str) -> str:
    key = name.strip().lower().replace(" ", "_").replace("-", "_")
    if key not in DOMAIN_ALIASES:
        raise ValueError(f"unknown domain or configuration: {name}")
    return DOMAIN_ALIASES[key]


def generate_config(name: str, seed: int = 42) -> list[Example]:
    resolved = resolve_domain(name)
    if resolved == "all":
        examples: list[Example] = []
        for key in BASE_CONFIGS:
            examples.extend(GENERATORS[key](seed=seed))
        return examples
    if resolved == "core":
        return [
            example
            for example in generate_config("all", seed=seed)
            if example.quality.tier in {QualityTier.S, QualityTier.A}
        ]
    if resolved == "verified":
        return [
            example
            for example in generate_config("all", seed=seed)
            if example.quality.verified and example.quality.tier is QualityTier.S
        ]
    return GENERATORS[resolved](seed=seed)
