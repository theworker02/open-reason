"""Held-out evaluation helpers. Never train on benchmarks/."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from open_reason.config import repo_root
from open_reason.io import iter_jsonl


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return list(iter_jsonl(path))


def normalize_answer(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return " ".join(text.split()).lower()


def exact_match(prediction: Any, gold: Any) -> bool:
    return normalize_answer(prediction) == normalize_answer(gold)


def numeric_match(prediction: Any, gold: Any, *, rel_tol: float = 1e-6, abs_tol: float = 1e-8) -> bool:
    try:
        left = float(str(prediction).strip())
        right = float(str(gold).strip())
    except (TypeError, ValueError):
        return False
    return math.isclose(left, right, rel_tol=rel_tol, abs_tol=abs_tol)


def score_predictions(
    predictions: list[dict[str, Any]],
    gold: list[dict[str, Any]],
) -> dict[str, Any]:
    by_id = {row.get("id"): row for row in gold if row.get("id")}
    graded = 0
    exact = 0
    numeric = 0
    missing = 0
    for pred in predictions:
        example_id = pred.get("id")
        gold_row = by_id.get(example_id)
        if gold_row is None:
            missing += 1
            continue
        graded += 1
        guess = pred.get("prediction")
        if guess is None:
            guess = pred.get("answer")
        target = gold_row.get("answer")
        if exact_match(guess, target):
            exact += 1
        if numeric_match(guess, target):
            numeric += 1
    return {
        "predictions": len(predictions),
        "gold": len(gold),
        "graded": graded,
        "missing_ids": missing,
        "exact_match": exact,
        "exact_match_rate": None if not graded else round(exact / graded, 4),
        "numeric_match": numeric,
        "numeric_match_rate": None if not graded else round(numeric / graded, 4),
        "note": "Rates are only meaningful on holdout gold, not training JSONL.",
    }


def overlap_ids(train_path: Path, bench_path: Path) -> list[str]:
    train = {row.get("id") for row in iter_jsonl(train_path) if row.get("id")}
    bench = {row.get("id") for row in iter_jsonl(bench_path) if row.get("id")}
    return sorted(i for i in train & bench if i)


def evaluate_paths(
    *,
    predictions: Path,
    gold: Path | None = None,
    train: Path | None = None,
) -> dict[str, Any]:
    root = repo_root()
    gold = gold or (root / "benchmarks" / "items.jsonl")
    gold_rows = load_jsonl(gold)
    pred_rows = load_jsonl(predictions) if predictions.exists() else []
    report = score_predictions(pred_rows, gold_rows)
    report["gold_path"] = str(gold)
    report["predictions_path"] = str(predictions)
    if train and train.exists():
        hits = overlap_ids(train, gold)
        report["train_overlap"] = len(hits)
        report["train_overlap_ids"] = hits[:20]
        if hits:
            report["contaminated"] = True
        else:
            report["contaminated"] = False
    return report


def write_metrics(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
