from open_reason.pii import pii_hits


def test_allows_example_email() -> None:
    assert pii_hits("contact user@example.com") == []


def test_flags_other_email() -> None:
    hits = pii_hits("write to alex@company.test please")
    assert any(h.startswith("email:") for h in hits)
