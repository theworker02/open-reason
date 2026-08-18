from open_reason.sources import SourceAdmissionError, assert_can_ingest, load_registry
from open_reason.sources.approve import auto_approve, evaluate_source


def test_auto_approve_never_enables_reddit_or_quora() -> None:
    decisions = {item.source_id: item for item in auto_approve(apply=False)}
    assert decisions["reddit"].enabled is False
    assert decisions["reddit"].action == "blocked"
    assert decisions["quora"].enabled is False
    assert decisions["quora"].action == "blocked"
    assert decisions["reddit"].verbatim is False


def test_auto_approve_khan_is_curriculum_not_verbatim() -> None:
    registry = load_registry()
    khan = evaluate_source(registry.by_id("khan-academy"))
    assert khan.action == "approve_curriculum"
    assert khan.enabled is True
    assert khan.curriculum_use is True
    assert khan.verbatim is False
    assert khan.status == "conditionally_approved"


def test_auto_approve_mit_ocw_not_verbatim() -> None:
    ocw = evaluate_source(load_registry().by_id("mit-ocw"))
    assert ocw.enabled is True
    assert ocw.verbatim is False
    assert "non-commercial" in ocw.reason.lower() or "curriculum" in ocw.reason.lower()


def test_stack_exchange_not_auto_enabled() -> None:
    se = evaluate_source(load_registry().by_id("stack-exchange"))
    assert se.enabled is False
    assert se.action == "metadata_only"
    assert se.verbatim is False


def test_python_docs_auto_approved_not_verbatim() -> None:
    docs = evaluate_source(load_registry().by_id("python-docs"))
    assert docs.enabled is True
    assert docs.curriculum_use is True
    assert docs.verbatim is False
    assert docs.action == "approve_curriculum"


def test_reddit_still_cannot_ingest() -> None:
    try:
        assert_can_ingest("reddit")
        raise AssertionError("expected SourceAdmissionError")
    except SourceAdmissionError as exc:
        assert "Reddit" in str(exc)
