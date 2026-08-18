"""Coverage analysis over the knowledge graph vs emitted examples."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from open_reason.knowledge import load_knowledge_graph
from open_reason.models import Example

TASK_TYPES_PER_CONCEPT = (
    "concept_explanation",
    "simple_exercise",
    "applied_exercise",
    "debugging_exercise",
    "diagnostic_misconception",
)


def analyze_coverage(examples: Iterable[Example], *, root=None) -> dict[str, Any]:
    graph = load_knowledge_graph(root)
    by_concept: dict[str, set[str]] = defaultdict(set)
    unlabeled = 0
    for example in examples:
        cid = example.concept_id
        if not cid:
            unlabeled += 1
            continue
        by_concept[cid].add(example.task_type)

    concepts_total = len(graph.concepts)
    covered = [cid for cid in graph.concepts if by_concept.get(cid)]
    missing = sorted(cid for cid in graph.concepts if cid not in by_concept)
    thin = sorted(
        cid
        for cid in graph.concepts
        if 0 < len(by_concept.get(cid, ())) < 2
    )
    percent = 0.0 if not concepts_total else round(100.0 * len(covered) / concepts_total, 1)
    insufficient = percent < 80.0
    return {
        "concepts_total": concepts_total,
        "concepts_with_examples": len(covered),
        "coverage_percent": percent,
        "insufficient_coverage": insufficient,
        "missing_concepts": missing,
        "thin_concepts": thin,
        "unlabeled_examples": unlabeled,
        "examples_scanned": unlabeled + sum(len(v) for v in by_concept.values()),
        "task_types_by_concept": {k: sorted(v) for k, v in sorted(by_concept.items())},
        "expected_task_types": list(TASK_TYPES_PER_CONCEPT),
    }
