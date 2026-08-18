"""Open Reason knowledge graph: concepts, prerequisites, misconceptions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from open_reason.config import repo_root


class Concept(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    domain: str
    education_level: str
    prerequisites: list[str] = Field(default_factory=list)
    related_concepts: list[str] = Field(default_factory=list)
    common_mistakes: list[str] = Field(default_factory=list)
    verification_methods: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


class Misconception(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    concept_id: str
    statement: str
    why_it_is_wrong: str
    correct_explanation: str
    diagnostic_prompt: str | None = None
    diagnostic_answer: str | None = None


class Trajectory(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    domain: str
    steps: list[str]


class KnowledgeGraph(BaseModel):
    model_config = ConfigDict(extra="forbid")

    concepts: dict[str, Concept]
    misconceptions: dict[str, Misconception]
    trajectories: dict[str, Trajectory]

    @model_validator(mode="after")
    def _links_exist(self) -> KnowledgeGraph:
        for concept in self.concepts.values():
            for prereq in concept.prerequisites:
                if prereq not in self.concepts:
                    raise ValueError(f"{concept.id} prerequisite missing: {prereq}")
            for related in concept.related_concepts:
                if related not in self.concepts:
                    raise ValueError(f"{concept.id} related concept missing: {related}")
            for mistake in concept.common_mistakes:
                if mistake not in self.misconceptions:
                    raise ValueError(f"{concept.id} misconception missing: {mistake}")
        for item in self.misconceptions.values():
            if item.concept_id not in self.concepts:
                raise ValueError(f"{item.id} concept missing: {item.concept_id}")
        for traj in self.trajectories.values():
            for step in traj.steps:
                if step not in self.concepts:
                    raise ValueError(f"{traj.id} step missing: {step}")
        cycles = _find_cycles(self.concepts)
        if cycles:
            raise ValueError(f"knowledge graph has cycles: {cycles}")
        return self

    def prerequisites_of(self, concept_id: str) -> list[str]:
        return list(self.concepts[concept_id].prerequisites)


def knowledge_dir(root: Path | None = None) -> Path:
    return (root or repo_root()) / "knowledge_graph"


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a mapping")
    return data


_GRAPH: KnowledgeGraph | None = None


def load_knowledge_graph(root: Path | None = None) -> KnowledgeGraph:
    global _GRAPH
    if _GRAPH is not None and root is None:
        return _GRAPH
    base = knowledge_dir(root)
    concepts_raw = load_yaml_mapping(base / "concepts.yaml").get("concepts") or []
    mistakes_raw = load_yaml_mapping(base / "misconceptions.yaml").get("misconceptions") or []
    traj_raw = load_yaml_mapping(base / "trajectories.yaml").get("trajectories") or []
    concepts = {item["id"]: Concept.model_validate(item) for item in concepts_raw}
    misconceptions = {item["id"]: Misconception.model_validate(item) for item in mistakes_raw}
    trajectories = {item["id"]: Trajectory.model_validate(item) for item in traj_raw}
    graph = KnowledgeGraph(
        concepts=concepts,
        misconceptions=misconceptions,
        trajectories=trajectories,
    )
    if root is None:
        _GRAPH = graph
    return graph


def match_concept(graph: KnowledgeGraph, text: str) -> str | None:
    lowered = text.lower()
    best: tuple[int, str] | None = None
    for concept in graph.concepts.values():
        needles = [concept.name.lower(), *concept.keywords, concept.id.replace(".", " ")]
        hits = sum(1 for needle in needles if needle and needle in lowered)
        if hits and (best is None or hits > best[0]):
            best = (hits, concept.id)
    return None if best is None else best[1]


def _find_cycles(concepts: dict[str, Concept]) -> list[str]:
    visiting: set[str] = set()
    visited: set[str] = set()
    found: list[str] = []

    def walk(node: str, stack: list[str]) -> None:
        if node in visited or node in found:
            return
        if node in visiting:
            found.append(" -> ".join([*stack, node]))
            return
        visiting.add(node)
        for nxt in concepts[node].prerequisites:
            walk(nxt, [*stack, node])
        visiting.remove(node)
        visited.add(node)

    for concept_id in concepts:
        walk(concept_id, [])
    return found
