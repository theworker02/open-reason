"""Detect and reject Reddit-derived material.

Open Reason does not use Reddit as a data source. These checks are conservative:
they flag obvious Reddit provenance so examples can be rejected, not so that
Reddit can be laundered through a secondary dataset.
"""

from __future__ import annotations

import re
from typing import Any

REDDIT_URL_RE = re.compile(
    r"(?i)(?:https?://)?(?:www\.)?(?:old\.|new\.|np\.)?(?:reddit\.com|redd\.it|redditmedia\.com|"
    r"redditstatic\.com|reddituploads\.com|pushshift\.io)\b"
)

REDDIT_TEXT_RE = re.compile(
    r"(?i)\b(?:r/[a-z0-9_]+|u/[a-z0-9_-]+|subreddit|redditor|upvote|downvote|"
    r"pushshift|the_donald|aita\b|amc?i\s+the\s+asshole)\b"
)

KNOWN_REDDIT_DATASETS = frozenset(
    {
        "pushshift",
        "reddit_tifu",
        "reddit-tifu",
        "writingprompts",
        "writing_prompts",
        "webis-tl-dr",
        "webis_tldr",
        "tldr_news_reddit",
        "reddit_comments",
        "reddit_submissions",
        "openwebtext",  # substantially Reddit-derived via outbound links / karma
        "openwebtext2",
        "elk_reddit",
        "psb_reddit",
        "convokit_reddit",
    }
)

REDDIT_SOURCE_RE = re.compile(
    r"(?i)\b(reddit|pushshift|subreddit|redd\.it)\b"
)


def reddit_hits(text: str | None) -> list[str]:
    if not text:
        return []
    hits: list[str] = []
    if REDDIT_URL_RE.search(text):
        hits.append("reddit_url")
    if REDDIT_TEXT_RE.search(text):
        hits.append("reddit_text")
    return hits


def inspect_record(record: dict[str, Any]) -> list[str]:
    """Return reasons the record appears Reddit-derived."""
    reasons: list[str] = []
    provenance = record.get("provenance") or {}
    if isinstance(provenance, dict):
        for key in ("source", "source_id", "source_url", "generator"):
            value = provenance.get(key)
            if isinstance(value, str):
                lowered = value.lower()
                if any(name in lowered.replace(" ", "_") for name in KNOWN_REDDIT_DATASETS):
                    reasons.append(f"known_reddit_dataset:{key}")
                if REDDIT_SOURCE_RE.search(value) or REDDIT_URL_RE.search(value):
                    reasons.append(f"reddit_provenance:{key}")
        extra = provenance.get("derived_from")
        if isinstance(extra, str) and REDDIT_SOURCE_RE.search(extra):
            reasons.append("reddit_derived_from")

    blobs: list[str] = []
    for key in ("prompt", "solution", "answer"):
        value = record.get(key)
        if isinstance(value, str):
            blobs.append(value)
    for key in ("observations", "constraints", "assumptions", "plan"):
        value = record.get(key)
        if isinstance(value, list):
            blobs.extend(str(item) for item in value)
    metadata = record.get("metadata") or {}
    if isinstance(metadata, dict):
        for value in metadata.values():
            if isinstance(value, str):
                blobs.append(value)

    for blob in blobs:
        reasons.extend(reddit_hits(blob))

    # de-duplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for reason in reasons:
        if reason not in seen:
            seen.add(reason)
            unique.append(reason)
    return unique


def is_reddit_record(record: dict[str, Any]) -> bool:
    return bool(inspect_record(record))
