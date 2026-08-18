from open_reason.generation.mathematics import generate_mathematics
from open_reason.verification import verify_math_answer


def test_sympy_equality() -> None:
    result = verify_math_answer("4", "2+2")
    assert result.passed is True


def test_math_generator_emits_verified() -> None:
    examples = generate_mathematics(seed=0)
    assert len(examples) >= 50
    assert all(ex.quality.verified for ex in examples)
    assert all(ex.verification and ex.verification.passed for ex in examples)
    assert all(ex.provenance.generator for ex in examples)
