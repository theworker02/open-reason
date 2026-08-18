"""Text and example normalization."""

from __future__ import annotations

import re
import unicodedata

from open_reason.models import Example

WHITESPACE_RE = re.compile(r"[ \t]+")
NEWLINE_RE = re.compile(r"\r\n|\r")


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = NEWLINE_RE.sub("\n", text)
    text = "\n".join(WHITESPACE_RE.sub(" ", line).rstrip() for line in text.split("\n"))
    return text.strip()


def normalize_prompt_key(text: str) -> str:
    """Aggressive key used for duplicate detection, not for stored text."""
    lowered = normalize_text(text).lower()
    lowered = re.sub(r"[^\w\s]", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def normalize_example(example: Example) -> Example:
    data = example.model_dump()
    data["prompt"] = normalize_text(example.prompt)
    if example.solution:
        data["solution"] = normalize_text(example.solution)
    if example.answer:
        data["answer"] = normalize_text(example.answer)
    for field in ("observations", "constraints", "assumptions", "plan"):
        data[field] = [normalize_text(item) for item in getattr(example, field) if item.strip()]
    data["task_type"] = example.task_type.strip().lower().replace(" ", "_")
    return Example.model_validate(data)
