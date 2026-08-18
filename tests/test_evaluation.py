from __future__ import annotations

from pathlib import Path

from open_reason.evaluation import exact_match, numeric_match, score_predictions
from open_reason.training import prepare_sft_rows


def test_exact_and_numeric_match() -> None:
    assert exact_match(" 4 ", "4")
    assert numeric_match("16.0", "16")
    assert not exact_match("yes", "no")
    assert not numeric_match("abc", "1")


def test_score_predictions_fixture() -> None:
    gold = [{"id": "a", "answer": "7"}, {"id": "b", "answer": "16"}]
    preds = [{"id": "a", "prediction": "7"}, {"id": "missing", "prediction": "x"}]
    report = score_predictions(preds, gold)
    assert report["graded"] == 1
    assert report["exact_match"] == 1
    assert report["missing_ids"] == 1


def test_prepare_sft_rows_skips_empty() -> None:
    rows = [
        {"id": "1", "prompt": "Q?", "answer": "A", "quality": {"verified": True}, "domain": "mathematics"},
        {"id": "2", "prompt": "", "answer": "A"},
    ]
    prepared = prepare_sft_rows(rows)
    assert len(prepared) == 1
    assert prepared[0]["completion"] == "A"
