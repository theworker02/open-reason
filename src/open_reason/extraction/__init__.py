"""Extraction helpers for future source snapshots."""

from __future__ import annotations

from pathlib import Path

from open_reason.knowledge import load_knowledge_graph, match_concept
from open_reason.models import Example


def list_source_files(root: Path, suffixes: tuple[str, ...] = (".py", ".js", ".ts", ".sql")) -> list[Path]:
    return [path for path in root.rglob("*") if path.suffix.lower() in suffixes and path.is_file()]


def extract_concept(example: Example) -> Example:
    """Attach a concept_id from the knowledge graph when one is not already set."""
    if example.concept_id:
        return example
    graph = load_knowledge_graph()
    blob = " ".join(filter(None, [example.prompt, example.solution, example.answer]))
    matched = match_concept(graph, blob)
    if not matched:
        return example
    data = example.model_dump()
    data["concept_id"] = matched
    extra = dict(example.metadata)
    extra["concept_id_inferred"] = True
    data["metadata"] = extra
    return Example.model_validate(data)
