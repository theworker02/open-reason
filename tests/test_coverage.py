from __future__ import annotations

from open_reason.coverage import analyze_coverage
from open_reason.generation.coverage_tasks import COVERAGE_SPECS, generate_coverage_tasks
from open_reason.generation.curriculum import TASKS
from open_reason.knowledge import load_knowledge_graph


def test_coverage_specs_are_unique_prompts() -> None:
    prompts = [spec["prompt"] for spec in COVERAGE_SPECS]
    assert len(prompts) == len(set(prompts))
    assert len(COVERAGE_SPECS) >= 80


def test_curriculum_banks_have_multiple_tasks() -> None:
    for source_id, tasks in TASKS.items():
        assert len(tasks) >= 2, source_id
        prompts = [item["prompt"] for item in tasks]
        assert len(prompts) == len(set(prompts)), source_id


def test_coverage_generation_emits_examples() -> None:
    examples = generate_coverage_tasks(seed=42)
    assert len(examples) >= 70
    assert all(ex.provenance.generator_version for ex in examples)


def test_education_coverage_not_thin_overall() -> None:
    from open_reason.generation import generate_education_release

    examples = generate_education_release(seed=42)
    report = analyze_coverage(examples)
    assert report["concepts_total"] == len(load_knowledge_graph().concepts)
    assert report["coverage_percent"] >= 80
    assert report["insufficient_coverage"] is False
    thin = report["thin_concepts"]
    assert len(thin) <= max(5, report["concepts_total"] // 5)
