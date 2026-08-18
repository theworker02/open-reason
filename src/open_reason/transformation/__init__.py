"""Knowledge-unit transforms. Source text is not the training example."""

from __future__ import annotations

from open_reason.knowledge import load_knowledge_graph, match_concept
from open_reason.models import Example
from open_reason.normalization import normalize_example
from open_reason.scoring import apply_evidence_score


def transform_example(example: Example) -> Example:
    example = normalize_example(example)
    example = apply_evidence_score(example)
    steps = list(example.transformation)
    if "knowledge_normalization" not in steps:
        steps.append("knowledge_normalization")
    if example.quality.verified and "verification" not in steps:
        steps.append("verification")
    data = example.model_dump()
    data["transformation"] = steps
    if not data.get("concept_id"):
        graph = load_knowledge_graph()
        blob = " ".join(
            filter(
                None,
                [example.prompt, example.solution, example.answer, *(example.observations or [])],
            )
        )
        matched = match_concept(graph, blob)
        if matched:
            data["concept_id"] = matched
            extra = dict(example.metadata)
            extra["concept_id_inferred"] = True
            data["metadata"] = extra
    return Example.model_validate(data)
