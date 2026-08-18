from open_reason.ids import make_example_id


def test_ids_deterministic() -> None:
    payload = {"prompt": "x", "answer": "1"}
    a = make_example_id("mathematics", "synthetic", payload)
    b = make_example_id("mathematics", "synthetic", payload)
    assert a == b
    assert a.startswith("or-mathematics-synthetic-")
