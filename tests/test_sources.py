from pydantic import ValidationError

from open_reason.generation.education import generate_education
from open_reason.knowledge import load_knowledge_graph
from open_reason.models import Quality, QualityTier, SourceType
from open_reason.scoring import apply_evidence_score, evidence_components
from open_reason.sources import SourceAdmissionError, SourceRecord, assert_can_ingest, load_registry
from open_reason.validation import validate_record


def test_registry_loads_and_never_enables_reddit() -> None:
    registry = load_registry()
    assert registry.policy.reddit == "prohibited"
    assert registry.policy.auto_ingest_discovered is False
    enabled = {source.id for source in registry.enabled()}
    assert "reddit" not in enabled
    assert "quora" not in enabled
    assert "open-reason-authors" in enabled
    assert "open-reason-generators" in enabled
    assert all(source.verbatim is False for source in registry.sources)


def test_unreviewed_or_skipped_source_cannot_ingest() -> None:
    try:
        assert_can_ingest("wikipedia")
        raise AssertionError("expected SourceAdmissionError")
    except SourceAdmissionError as exc:
        assert "not enabled" in str(exc) or "forbids" in str(exc)


def test_stackoverflow_is_curriculum_only() -> None:
    record = assert_can_ingest("stackoverflow")
    assert record.enabled is True
    assert record.verbatim is False
    assert record.curriculum_use is True
    se = load_registry().by_id("stack_exchange")
    assert se.verbatim is False


def test_reddit_source_cannot_ingest() -> None:
    try:
        assert_can_ingest("reddit")
        raise AssertionError("expected SourceAdmissionError")
    except SourceAdmissionError as exc:
        assert "Reddit" in str(exc)


def test_reddit_allowed_true_is_invalid() -> None:
    try:
        SourceRecord(
            id="example",
            name="Example",
            category="test",
            status="approved",
            enabled=False,
            reddit_allowed=True,
        )
        raise AssertionError("expected validation error")
    except ValidationError:
        pass


def test_quora_provenance_rejected() -> None:
    record = {
        "id": "or-human-x-bbbbbbbbbbbb",
        "domain": "human",
        "task_type": "explanation",
        "difficulty": "beginner",
        "prompt": "Why is hashing used in dictionaries?",
        "answer": "Average-case constant-time lookup under uniform hashing.",
        "provenance": {
            "source_type": "community",
            "source": "quora",
            "source_url": "https://www.quora.com/example",
            "license_spdx": "CC-BY-4.0",
        },
        "quality": {"tier": "B", "verified": False},
    }
    _, result = validate_record(record)
    assert not result.ok
    assert any(issue.code == "quora" for issue in result.issues)


def test_community_votes_are_not_verification() -> None:
    record = {
        "id": "or-coding-x-cccccccccccc",
        "domain": "coding",
        "task_type": "debugging",
        "difficulty": "beginner",
        "prompt": "Why does this Python function fail the tests?",
        "answer": "The loop never terminates.",
        "context": {"language": "python"},
        "provenance": {
            "source_type": "community",
            "source": "stack_exchange",
            "license_spdx": "CC-BY-4.0",
        },
        "quality": {
            "tier": "A",
            "verified": True,
            "verification_method": "accepted_answer",
        },
        "verification": {"method": "accepted_answer", "passed": True},
    }
    _, result = validate_record(record)
    assert not result.ok
    assert any(issue.code == "community_not_verification" for issue in result.issues)


def test_knowledge_graph_prerequisites() -> None:
    graph = load_knowledge_graph()
    assert "python.variables" in graph.concepts
    assert graph.concepts["python.loops"].prerequisites == ["python.conditionals"]
    assert graph.prerequisites_of("math.calculus") == ["math.functions"]


def test_discovery_does_not_ingest_reddit() -> None:
    from open_reason.sources.discovery import score_candidate

    try:
        score_candidate(
            "reddit",
            authority=0.1,
            educational_quality=0.1,
            license_clarity=0.0,
            technical_relevance=0.1,
        )
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "Reddit" in str(exc)


def test_curriculum_examples_have_concept_and_level() -> None:
    examples = generate_education()
    assert examples
    for example in examples:
        assert example.concept_id
        assert example.education_level is not None
        assert example.provenance.source_type is SourceType.SYNTHETIC
        assert example.quality.evidence_confidence is not None


def test_evidence_confidence_does_not_verify_community() -> None:
    from open_reason.models import Domain, EducationLevel, Evidence, Example, Provenance

    example = Example(
        id="or-coding-test-dddddddddddd",
        domain=Domain.CODING,
        task_type="debugging",
        difficulty="beginner",
        prompt="Explain a failing loop in a unit test.",
        answer="The loop condition never becomes false.",
        context={"language": "python"},
        provenance=Provenance(
            source_type=SourceType.COMMUNITY,
            source="stack_exchange",
            license_spdx="CC-BY-4.0",
        ),
        quality=Quality(tier=QualityTier.A, verified=False),
        evidence=Evidence(community_evidence={"score": 400, "accepted": True}),
        education_level=EducationLevel.UNDERGRADUATE,
    )
    scored = apply_evidence_score(example)
    parts = evidence_components(scored)
    assert parts["community_score"] <= 0.5
    assert scored.quality.verified is False
    assert scored.quality.evidence_confidence is not None
    assert scored.quality.evidence_confidence < 0.9


def test_high_risk_cannot_be_s_without_authority() -> None:
    record = {
        "id": "or-science-x-eeeeeeeeeeee",
        "domain": "science",
        "task_type": "conceptual",
        "difficulty": "advanced",
        "prompt": "What is a typical adult resting heart-rate range taught in first aid courses?",
        "answer": "This item is a placeholder and must not be treated as medical advice.",
        "provenance": {
            "source_type": "community",
            "source": "forum",
            "license_spdx": "CC-BY-4.0",
        },
        "quality": {
            "tier": "S",
            "verified": True,
            "verification_method": "numeric",
        },
        "verification": {"method": "numeric", "passed": True},
        "metadata": {"high_risk_domain": "medicine"},
    }
    _, result = validate_record(record)
    assert not result.ok
    assert any(issue.code == "high_risk" for issue in result.issues)
