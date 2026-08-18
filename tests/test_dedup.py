from open_reason.deduplication import Deduplicator
from open_reason.generation.base import build_example, generated_quality
from open_reason.models import Domain
from open_reason.provenance import synthetic_provenance


def _ex(prompt: str, answer: str) -> object:
    return build_example(
        domain=Domain.MATHEMATICS,
        task_type="arithmetic",
        prompt=prompt,
        answer=answer,
        solution=answer,
        provenance=synthetic_provenance(generator="tests", generator_version="0.1.0"),
        quality=generated_quality(),
        source_key="dup",
    )


def test_exact_and_normalized_dup() -> None:
    a = _ex("Compute 2 + 2.", "4")
    b = _ex("Compute 2 + 2.", "4")
    c = _ex("Compute  2 + 2.", "4")
    d = _ex("Compute 3 + 3.", "6")
    dedup = Deduplicator(max_similarity=0.99)
    kept = dedup.filter([a, b, c, d])
    assert len(kept) == 2
    assert dedup.stats.exact_duplicates >= 1
