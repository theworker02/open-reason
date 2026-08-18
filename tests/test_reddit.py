from open_reason.provenance.reddit import inspect_record, is_reddit_record
from open_reason.validation import validate_record


def test_reddit_url_rejected() -> None:
    record = {
        "id": "or-human-x-bbbbbbbbbbbb",
        "domain": "human",
        "task_type": "explanation",
        "difficulty": "beginner",
        "prompt": "See https://www.reddit.com/r/programming/comments/abc for context.",
        "answer": "no",
        "provenance": {
            "source_type": "synthetic",
            "generator": "tests",
            "generator_version": "0.1.0",
            "license_spdx": "CC-BY-4.0",
        },
        "quality": {"tier": "B", "verified": False},
    }
    assert is_reddit_record(record)
    _, result = validate_record(record)
    assert not result.ok
    assert any(i.code == "reddit" for i in result.issues)


def test_pushshift_source_rejected() -> None:
    hits = inspect_record(
        {
            "prompt": "hello world example prompt",
            "provenance": {"source": "pushshift comments dump", "source_type": "unknown"},
        }
    )
    assert hits
