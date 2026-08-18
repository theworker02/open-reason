from open_reason.generation.difficulty import score_example
from open_reason.generation.base import build_example, generated_quality
from open_reason.models import Difficulty, Domain
from open_reason.provenance import synthetic_provenance


def test_difficulty_not_random() -> None:
    simple = build_example(
        domain=Domain.MATHEMATICS,
        task_type="arithmetic",
        prompt="Compute 1 + 1.",
        answer="2",
        solution="2",
        provenance=synthetic_provenance(generator="tests", generator_version="0.1.0"),
        quality=generated_quality(),
        source_key="easy",
    )
    hard = build_example(
        domain=Domain.CODING,
        task_type="compiler",
        prompt="Write a compiler frontend with a type system, concurrency analysis, and distributed lowering. " * 8,
        answer="see solution",
        solution="complex",
        constraints=["ssa", "occurs check", "np-hard register allocation"] * 3,
        plan=["lex", "parse", "typecheck", "lower", "schedule"] * 3,
        provenance=synthetic_provenance(generator="tests", generator_version="0.1.0"),
        quality=generated_quality(),
        source_key="hard",
        context={"language": "python", "repository": {"files": {"a.py": "print(1)\n" * 80}}},
    )
    d0, _ = score_example(simple)
    d1, _ = score_example(hard)
    assert d0 in Difficulty
    assert list(Difficulty).index(d1) > list(Difficulty).index(d0)
