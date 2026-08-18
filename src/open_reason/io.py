"""Streaming readers and writers for JSONL, Parquet, and Arrow."""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from open_reason.models import Example


def iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            try:
                yield json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from exc


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
            count += 1
    return count


def example_to_record(example: Example) -> dict[str, Any]:
    return example.model_dump(mode="json")


def record_to_example(record: dict[str, Any]) -> Example:
    return Example.model_validate(record)


def write_parquet(path: Path, records: Iterable[dict[str, Any]], *, chunk_size: int = 1024) -> int:
    """Write records to Parquet without requiring the full table in memory.

    Nested objects are stored as JSON strings so the on-disk schema stays
    stable across configurations. Optional columns are nullable strings so
    mixed domain batches cannot change Arrow types mid-file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    writer: pq.ParquetWriter | None = None
    batch: list[dict[str, Any]] = []
    count = 0

    def flush() -> None:
        nonlocal writer, batch, count
        if not batch:
            return
        table = pa.Table.from_pylist(
            [_flatten_record(item) for item in batch], schema=PARQUET_SCHEMA
        )
        if writer is None:
            writer = pq.ParquetWriter(path, PARQUET_SCHEMA, compression="zstd")
        writer.write_table(table)
        count += len(batch)
        batch = []

    try:
        for record in records:
            batch.append(record)
            if len(batch) >= chunk_size:
                flush()
        flush()
    finally:
        if writer is not None:
            writer.close()
    return count


def read_parquet_records(path: Path) -> Iterator[dict[str, Any]]:
    parquet_file = pq.ParquetFile(path)
    for batch in parquet_file.iter_batches(batch_size=1024):
        for row in batch.to_pylist():
            yield _unflatten_record(row)


JSON_OBJECT_FIELDS = (
    "context",
    "verification",
    "provenance",
    "quality",
    "metadata",
    "evidence",
    "temporal",
    "runtime",
)

JSON_LIST_FIELDS = (
    "observations",
    "constraints",
    "assumptions",
    "plan",
    "strategy",
    "transformation",
)

PARQUET_COLUMNS = (
    "id",
    "domain",
    "task_type",
    "difficulty",
    "prompt",
    "context",
    "observations",
    "constraints",
    "assumptions",
    "plan",
    "strategy",
    "solution",
    "answer",
    "verification",
    "provenance",
    "quality",
    "education_level",
    "concept_id",
    "evidence",
    "transformation",
    "temporal",
    "runtime",
    "natural_language",
    "translation_status",
    "metadata",
)

PARQUET_SCHEMA = pa.schema(
    [pa.field(name, pa.string(), nullable=True) for name in PARQUET_COLUMNS]
)


def _as_parquet_string(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _flatten_record(record: dict[str, Any]) -> dict[str, Any]:
    flat = dict(record)
    for field in JSON_OBJECT_FIELDS:
        value = flat.get(field)
        if value is not None and not isinstance(value, str):
            flat[field] = json.dumps(value, ensure_ascii=False, sort_keys=True)
    for field in JSON_LIST_FIELDS:
        value = flat.get(field)
        if value is not None and not isinstance(value, str):
            flat[field] = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return {name: _as_parquet_string(flat.get(name)) for name in PARQUET_COLUMNS}


def _unflatten_record(record: dict[str, Any]) -> dict[str, Any]:
    restored = dict(record)
    for field in (*JSON_OBJECT_FIELDS, *JSON_LIST_FIELDS):
        value = restored.get(field)
        if isinstance(value, str) and value[:1] in "[{":
            restored[field] = json.loads(value)
    return restored
