"""Exact, normalized, and near-duplicate detection."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable
from dataclasses import dataclass, field

from open_reason.ids import canonical_json, sha256_hex
from open_reason.models import Example
from open_reason.normalization import normalize_prompt_key


def exact_hash(example: Example) -> str:
    return sha256_hex(canonical_json(example.content_fingerprint_payload()))


def normalized_hash(example: Example) -> str:
    payload = {
        "domain": example.domain.value,
        "task_type": example.task_type,
        "prompt": normalize_prompt_key(example.prompt),
        "answer": normalize_prompt_key(example.answer or ""),
        "solution": normalize_prompt_key(example.solution or ""),
    }
    return sha256_hex(canonical_json(payload))


def simhash64(text: str) -> int:
    """64-bit simhash over 3-grams for near-duplicate detection."""
    tokens = _shingles(text, 3)
    if not tokens:
        return 0
    vector = [0] * 64
    for token in tokens:
        digest = int(hashlib.sha1(token.encode("utf-8")).hexdigest()[:16], 16)
        for bit in range(64):
            if digest & (1 << bit):
                vector[bit] += 1
            else:
                vector[bit] -= 1
    value = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            value |= 1 << bit
    return value


def hamming64(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def similarity_from_hamming(distance: int) -> float:
    return 1.0 - (distance / 64.0)


def param_signature(text: str) -> tuple[str, ...]:
    """Numeric/token parameters that distinguish legitimate template instances."""
    return tuple(re.findall(r"-?\d+(?:\.\d+)?", text))


def _shingles(text: str, size: int) -> list[str]:
    compact = normalize_prompt_key(text)
    if len(compact) < size:
        return [compact] if compact else []
    return [compact[i : i + size] for i in range(len(compact) - size + 1)]


@dataclass
class DedupStats:
    input_count: int = 0
    kept: int = 0
    exact_duplicates: int = 0
    normalized_duplicates: int = 0
    near_duplicates: int = 0
    cross_config_duplicates: int = 0


@dataclass
class Deduplicator:
    max_similarity: float = 0.92
    seen_exact: set[str] = field(default_factory=set)
    seen_normalized: set[str] = field(default_factory=set)
    seen_simhash: list[tuple[int, tuple[str, ...], str]] = field(default_factory=list)
    stats: DedupStats = field(default_factory=DedupStats)

    def keep(self, example: Example) -> bool:
        self.stats.input_count += 1
        exact = exact_hash(example)
        if exact in self.seen_exact:
            self.stats.exact_duplicates += 1
            return False
        normalized = normalized_hash(example)
        if normalized in self.seen_normalized:
            self.stats.normalized_duplicates += 1
            return False
        fingerprint = simhash64(
            " ".join(
                [
                    example.prompt,
                    example.answer or "",
                    example.solution or "",
                ]
            )
        )
        params = param_signature(example.prompt + " " + (example.answer or ""))
        answer_key = normalize_prompt_key(example.answer or "")
        for previous, prev_params, prev_answer in self.seen_simhash:
            distance = hamming64(fingerprint, previous)
            if (
                similarity_from_hamming(distance) >= self.max_similarity
                and params == prev_params
                and answer_key == prev_answer
            ):
                self.stats.near_duplicates += 1
                return False
        self.seen_exact.add(exact)
        self.seen_normalized.add(normalized)
        self.seen_simhash.append((fingerprint, params, answer_key))
        self.stats.kept += 1
        return True

    def filter(self, examples: Iterable[Example]) -> list[Example]:
        kept: list[Example] = []
        for example in examples:
            if self.keep(example):
                kept.append(example)
        return kept

    def as_dict(self) -> dict[str, int]:
        return {
            "input_count": self.stats.input_count,
            "kept": self.stats.kept,
            "exact_duplicates": self.stats.exact_duplicates,
            "normalized_duplicates": self.stats.normalized_duplicates,
            "near_duplicates": self.stats.near_duplicates,
            "dropped": self.stats.input_count - self.stats.kept,
        }
