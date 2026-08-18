from open_reason.contamination import scan_examples
from open_reason.generation.base import build_example, generated_quality
from open_reason.models import Domain
from open_reason.provenance import synthetic_provenance


def test_humaneval_needle() -> None:
    example = build_example(
        domain=Domain.CODING,
        task_type="code_generation",
        prompt="Implement has_close_elements as in HumanEval/0",
        answer="pass",
        solution="pass",
        provenance=synthetic_provenance(generator="tests", generator_version="0.1.0"),
        quality=generated_quality(),
        source_key="contam",
        context={"language": "python"},
    )
    report = scan_examples(
        [example],
        {"benchmarks": [{"name": "humaneval", "needles": ["has_close_elements"], "prompt_prefixes": []}]},
    )
    assert report.hit_count == 1
