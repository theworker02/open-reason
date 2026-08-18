"""Difficulty scoring from measurable characteristics, not random assignment."""

from __future__ import annotations

import re

from open_reason.models import Difficulty, Example

KEYWORD_WEIGHTS = {
    "proof": 2,
    "induction": 3,
    "asymptotic": 2,
    "concurrency": 3,
    "deadlock": 3,
    "compiler": 3,
    "distributed": 3,
    "np-hard": 4,
    "measure": 2,
    "partial differential": 4,
    "lagrange": 2,
    "eigen": 2,
    "quantum": 3,
    "topology": 3,
}


def score_example(example: Example) -> tuple[Difficulty, dict[str, float]]:
    score = 0.0
    parts: dict[str, float] = {}

    constraint_score = min(len(example.constraints), 6) * 0.7
    parts["constraints"] = constraint_score
    score += constraint_score

    observation_score = min(len(example.observations), 6) * 0.3
    parts["observations"] = observation_score
    score += observation_score

    plan_score = min(len(example.plan), 8) * 0.4
    parts["plan"] = plan_score
    score += plan_score

    prompt_len = len(example.prompt.split())
    length_score = min(prompt_len / 40.0, 4.0)
    parts["prompt_length"] = length_score
    score += length_score

    solution_text = " ".join(
        filter(None, [example.solution, example.answer, example.prompt])
    ).lower()
    keyword_score = 0.0
    for keyword, weight in KEYWORD_WEIGHTS.items():
        if keyword in solution_text:
            keyword_score += weight
    parts["keywords"] = keyword_score
    score += keyword_score

    context = example.context or {}
    tests = context.get("tests") or context.get("verification") or {}
    if isinstance(tests, dict):
        n_tests = tests.get("tests_passed") or tests.get("n_tests") or 0
        try:
            test_score = min(float(n_tests) / 4.0, 3.0)
        except (TypeError, ValueError):
            test_score = 0.0
        parts["tests"] = test_score
        score += test_score

    files = (context.get("repository") or {}).get("files") or {}
    if isinstance(files, dict) and files:
        loc = sum(str(body).count("\n") + 1 for body in files.values())
        loc_score = min(loc / 40.0, 4.0)
        parts["code_size"] = loc_score
        score += loc_score

    math_ops = len(re.findall(r"[\^*/+\-]|\bintegr|\bderiv|\bmatrix|\bprove", solution_text))
    math_score = min(math_ops / 8.0, 3.0)
    parts["math_ops"] = math_score
    score += math_score

    difficulty = _bucket(score)
    parts["total"] = score
    return difficulty, parts


def _bucket(score: float) -> Difficulty:
    if score < 2.5:
        return Difficulty.INTRODUCTORY
    if score < 4.5:
        return Difficulty.BEGINNER
    if score < 7.5:
        return Difficulty.INTERMEDIATE
    if score < 11:
        return Difficulty.ADVANCED
    if score < 15:
        return Difficulty.EXPERT
    return Difficulty.RESEARCH


def apply_difficulty(example: Example) -> Example:
    difficulty, parts = score_example(example)
    data = example.model_dump()
    data["difficulty"] = difficulty.value
    metadata = dict(example.metadata)
    metadata["difficulty_score"] = parts
    data["metadata"] = metadata
    return Example.model_validate(data)
