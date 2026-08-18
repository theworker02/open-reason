from open_reason.coverage import analyze_coverage
from open_reason.generation.base import build_example, reviewed_quality, verified_quality
from open_reason.models import Domain, Verification
from open_reason.policy import evaluate_policy, load_source_policy
from open_reason.provenance import synthetic_provenance
from open_reason.sources import load_registry
from open_reason.sources.discovery import discover_candidates, score_candidate
from open_reason.validation import validate_record


def test_policy_reddit_is_prohibited() -> None:
    policy = load_source_policy()
    assert policy["reddit"] == "prohibited"
    reddit = evaluate_policy(load_registry().by_id("reddit"))
    assert reddit.decision == "AUTO_REJECTED"
    assert reddit.enabled is False


def test_policy_python_docs_auto_approved() -> None:
    verdict = evaluate_policy(load_registry().by_id("python_docs"))
    assert verdict.decision == "AUTO_APPROVED"
    assert verdict.verbatim is False
    assert verdict.enabled is True


def test_policy_stackoverflow_not_ingested() -> None:
    verdict = evaluate_policy(load_registry().by_id("stackoverflow"))
    assert verdict.decision == "METADATA_ONLY"
    assert verdict.enabled is False


def test_discovery_rejects_reddit() -> None:
    try:
        score_candidate("reddit-dump", authority=1, educational_quality=1, license_clarity=1, technical_relevance=1)
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "Reddit" in str(exc)


def test_discover_candidates_omit_reddit() -> None:
    rows = discover_candidates()
    assert rows
    assert all("reddit" not in row["source_id"].lower() for row in rows)


def test_coverage_reports_insufficient_when_empty() -> None:
    report = analyze_coverage([])
    assert report["concepts_total"] > 0
    assert report["insufficient_coverage"] is True
    assert report["coverage_percent"] == 0.0
    assert report["missing_concepts"]


def test_verified_without_passed_is_rejected() -> None:
    example = build_example(
        domain=Domain.MATHEMATICS,
        task_type="algebra",
        prompt="Solve a tiny original equation x = 1.",
        answer="1",
        solution="x=1",
        provenance=synthetic_provenance(generator="tests", generator_version="1.0.0"),
        quality=verified_quality("sympy"),
        source_key="test-false-verified",
        verification=Verification(method="sympy", passed=False, result="no"),
    )
    record = example.model_dump(mode="json")
    _, result = validate_record(record)
    assert not result.ok
    assert any(i.code == "verification" for i in result.issues)
