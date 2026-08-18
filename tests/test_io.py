from __future__ import annotations

from pathlib import Path

import pyarrow as pa

from open_reason.io import (
    PARQUET_COLUMNS,
    PARQUET_SCHEMA,
    read_parquet_records,
    write_parquet,
)


def _record(
    *,
    idx: int,
    education_level: str | None,
    optional_nulls: bool,
) -> dict:
    return {
        "id": f"or-test-mixed-{idx:04d}-aaaaaaaa",
        "domain": "mathematics" if optional_nulls else "coding",
        "task_type": "algebra" if optional_nulls else "code_generation",
        "difficulty": "beginner",
        "prompt": f"Mixed-schema parquet row {idx} for chunked writes.",
        "solution": "1",
        "answer": "1",
        "education_level": education_level,
        "concept_id": None if optional_nulls else "python.functions",
        "evidence": None,
        "temporal": None,
        "runtime": None,
        "context": None if optional_nulls else {"k": idx},
        "verification": {"method": "unit", "passed": True} if optional_nulls else None,
        "provenance": {"source_type": "synthetic", "generator": "tests"},
        "quality": {"tier": "B", "verified": False},
        "observations": [],
        "constraints": ["x"],
        "natural_language": "en",
    }


def test_parquet_schema_is_nullable_strings() -> None:
    assert list(PARQUET_SCHEMA.names) == list(PARQUET_COLUMNS)
    for field in PARQUET_SCHEMA:
        assert field.nullable
        assert pa.types.is_string(field.type)


def test_mixed_schema_parquet_across_chunks(tmp_path: Path) -> None:
    records = [
        _record(idx=1, education_level=None, optional_nulls=True),
        _record(idx=2, education_level=None, optional_nulls=True),
        _record(idx=3, education_level="high_school", optional_nulls=False),
        _record(idx=4, education_level="undergraduate", optional_nulls=False),
        _record(idx=5, education_level=None, optional_nulls=True),
    ]
    path = tmp_path / "mixed.parquet"
    assert write_parquet(path, records, chunk_size=2) == 5
    rows = list(read_parquet_records(path))
    assert len(rows) == 5
    assert rows[0]["education_level"] is None
    assert rows[0]["concept_id"] is None
    assert rows[0]["verification"] == {"method": "unit", "passed": True}
    assert rows[2]["education_level"] == "high_school"
    assert rows[2]["concept_id"] == "python.functions"
    assert rows[2]["context"] == {"k": 3}
    assert rows[4]["education_level"] is None
