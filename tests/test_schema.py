from open_reason.models import Domain, Example, Provenance, Quality, QualityTier, SourceType
from open_reason.validation import validate_record


def _base(**overrides):
    data = {
        "id": "or-mathematics-test-aaaaaaaaaaaa",
        "domain": "mathematics",
        "task_type": "algebra",
        "difficulty": "beginner",
        "prompt": "Solve for x: x + 1 = 2.",
        "answer": "1",
        "provenance": {
            "source_type": "synthetic",
            "source": "tests",
            "license": "CC-BY-4.0",
            "license_spdx": "CC-BY-4.0",
            "generator": "tests",
            "generator_version": "0.1.0",
            "generated_at": "2026-01-01T00:00:00Z",
        },
        "quality": {"tier": "B", "verified": False, "notes": []},
    }
    data.update(overrides)
    return data


def test_valid_record() -> None:
    example, result = validate_record(_base())
    assert result.ok
    assert isinstance(example, Example)
    assert example.domain is Domain.MATHEMATICS


def test_rejects_missing_outcome() -> None:
    data = _base()
    data.pop("answer")
    _, result = validate_record(data)
    assert not result.ok
    assert any(i.code == "schema" for i in result.issues)


def test_quality_s_requires_verified() -> None:
    try:
        Quality(tier=QualityTier.S, verified=False)
        assert False, "expected error"
    except Exception:
        pass


def test_unknown_provenance_requires_reason() -> None:
    try:
        Provenance(source_type=SourceType.UNKNOWN)
        assert False, "expected error"
    except Exception:
        pass
