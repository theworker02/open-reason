"""Stack Overflow as task seeds: original Open Reason prompts and solutions.

User-approved source. Not HTML scrapes, not Reddit mirrors, not verbatim dumps
of CC BY-SA posts. inspired_by=stackoverflow, verbatim=false. Votes never set
verified=true; coding rows still go through the sandbox.
"""

from __future__ import annotations

from open_reason.generation.base import build_example, reviewed_quality
from open_reason.generation.coding_python import T, PyTask
from open_reason.generation.reasoning import _emit
from open_reason.models import Domain, Example, Provenance, SourceType
from open_reason.constants import PIPELINE_VERSION


def so_provenance() -> Provenance:
    return Provenance(
        source_type=SourceType.COMMUNITY,
        source="stackoverflow",
        source_id="stackoverflow",
        license="Apache License 2.0",
        license_spdx="Apache-2.0",
        derived=True,
        transformation="original_rewrite_inspired_by_stackoverflow; verbatim=false",
        generator="open_reason.generation.stackoverflow_seeds",
        generator_version=PIPELINE_VERSION,
        trust_tier="tier4_community",
    )


def so_python_tasks() -> list[PyTask]:
    tasks = [
        T(
            "so-mutable-default",
            "python",
            """Implement `add_tag(tag: str, bucket: list[str] | None = None) -> list[str]`.

Append tag to a **new** list when bucket is None. Never use a shared mutable
default. Return the list.""",
            '''
def add_tag(tag, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(tag)
    return bucket
''',
            '''
import unittest
from solution import add_tag

class Test(unittest.TestCase):
    def test_independent(self):
        a = add_tag("x")
        b = add_tag("y")
        self.assertEqual(a, ["x"])
        self.assertEqual(b, ["y"])
    def test_reuse(self):
        acc = []
        add_tag("a", acc)
        add_tag("b", acc)
        self.assertEqual(acc, ["a", "b"])
''',
        ),
        T(
            "so-late-binding",
            "python",
            """Implement `make_multipliers(n: int) -> list`.

Return n functions f_i where f_i(x) == i * x for i in 0..n-1. Bind i at
definition time so later loop variables cannot change earlier closures.""",
            '''
def make_multipliers(n):
    return [lambda x, i=i: i * x for i in range(n)]
''',
            '''
import unittest
from solution import make_multipliers

class Test(unittest.TestCase):
    def test_bind(self):
        fns = make_multipliers(3)
        self.assertEqual([fn(2) for fn in fns], [0, 2, 4])
''',
        ),
        T(
            "so-is-vs-eq",
            "python",
            """Implement `same_object(a, b) -> bool` using identity, and
`same_value(a, b) -> bool` using equality. Do not use `is` for string/int value
comparisons inside same_value.""",
            '''
def same_object(a, b):
    return a is b

def same_value(a, b):
    return a == b
''',
            '''
import unittest
from solution import same_object, same_value

class Test(unittest.TestCase):
    def test_alias(self):
        x = []
        self.assertTrue(same_object(x, x))
        self.assertFalse(same_object([], []))
    def test_eq(self):
        self.assertTrue(same_value([1], [1]))
''',
        ),
        T(
            "so-copy-list",
            "python",
            """Implement `shallow_copy(xs: list) -> list` that is a new list with
the same elements (shallow). Mutating the copy's slots must not change the
original's length or slot identities for immutables.""",
            '''
def shallow_copy(xs):
    return list(xs)
''',
            '''
import unittest
from solution import shallow_copy

class Test(unittest.TestCase):
    def test_new(self):
        a = [1, 2]
        b = shallow_copy(a)
        b.append(3)
        self.assertEqual(a, [1, 2])
        self.assertEqual(b, [1, 2, 3])
''',
        ),
        T(
            "so-floor-div",
            "python",
            """Implement `chunks_needed(n: int, size: int) -> int`.

How many blocks of `size` are needed to cover n items? size > 0. Use
ceiling division without floating point.""",
            '''
def chunks_needed(n, size):
    if size <= 0:
        raise ValueError("size")
    return (n + size - 1) // size
''',
            '''
import unittest
from solution import chunks_needed

class Test(unittest.TestCase):
    def test_exact(self):
        self.assertEqual(chunks_needed(10, 5), 2)
    def test_ceil(self):
        self.assertEqual(chunks_needed(11, 5), 3)
    def test_zero(self):
        self.assertEqual(chunks_needed(0, 5), 0)
''',
        ),
        T(
            "so-utf8-len",
            "python",
            """Implement `utf8_nbytes(text: str) -> int`: number of bytes in the
UTF-8 encoding of text.""",
            '''
def utf8_nbytes(text):
    return len(text.encode("utf-8"))
''',
            '''
import unittest
from solution import utf8_nbytes

class Test(unittest.TestCase):
    def test_ascii(self):
        self.assertEqual(utf8_nbytes("ab"), 2)
    def test_emoji(self):
        self.assertGreater(utf8_nbytes("é"), 1)
''',
        ),
        T(
            "so-param-sql",
            "sql",
            """Implement `bind_where(column: str, value: str) -> tuple[str, tuple]`.

Return a parameterized fragment `col = ?` with a one-element tuple of value.
Allow only column names matching `[A-Za-z_][A-Za-z0-9_]*`. Raise ValueError
otherwise. Do not interpolate value into the SQL string.""",
            '''
import re

def bind_where(column, value):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", column):
        raise ValueError("column")
    return f"{column} = ?", (value,)
''',
            '''
import unittest
from solution import bind_where

class Test(unittest.TestCase):
    def test_ok(self):
        sql, params = bind_where("name", "O'Brien")
        self.assertEqual(sql, "name = ?")
        self.assertEqual(params, ("O'Brien",))
    def test_bad(self):
        with self.assertRaises(ValueError):
            bind_where("name;drop", "x")
''',
        ),
        T(
            "so-dict-last",
            "python",
            """Implement `last_wins(pairs: list[tuple[str, int]]) -> dict[str, int]`.

Build a dict; later pairs override earlier ones for the same key. Preserve
insertion order of first-seen keys (Python 3.7+).""",
            '''
def last_wins(pairs):
    out = {}
    for k, v in pairs:
        out[k] = v
    return out
''',
            '''
import unittest
from solution import last_wins

class Test(unittest.TestCase):
    def test_override(self):
        self.assertEqual(last_wins([("a", 1), ("b", 2), ("a", 9)]), {"a": 9, "b": 2})
''',
        ),
        T(
            "so-path-parts",
            "python",
            """Implement `join_posix(*parts: str) -> str` joining with `/`.
Collapse duplicate slashes except do not try to be a full URL parser. Empty
parts are skipped. Result must not start with `/` unless the first non-empty
part did.""",
            '''
def join_posix(*parts):
    nonempty = [p for p in parts if p]
    if not nonempty:
        return ""
    lead = nonempty[0].startswith("/")
    bits = [p.strip("/") for p in nonempty if p.strip("/")]
    body = "/".join(bits)
    if lead:
        return "/" + body if body else "/"
    return body
''',
            '''
import unittest
from solution import join_posix

class Test(unittest.TestCase):
    def test_rel(self):
        self.assertEqual(join_posix("a", "b"), "a/b")
    def test_abs(self):
        self.assertEqual(join_posix("/var", "log"), "/var/log")
    def test_skip_empty(self):
        self.assertEqual(join_posix("a", "", "c"), "a/c")
''',
        ),
        T(
            "so-unique-stable",
            "python",
            """Implement `unique_stable(items: list) -> list` keeping first
occurrences only, preserving order.""",
            '''
def unique_stable(items):
    seen = set()
    out = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out
''',
            '''
import unittest
from solution import unique_stable

class Test(unittest.TestCase):
    def test_order(self):
        self.assertEqual(unique_stable(["b", "a", "b", "c"]), ["b", "a", "c"])
''',
        ),
    ]
    for task in tasks:
        task["provenance"] = so_provenance().model_dump(mode="json")
        task["metadata_extra"] = {"inspired_by": "stackoverflow", "verbatim": False}
    return tasks


def extra_so_reasoning() -> list[Example]:
    """Constraint-checked original tasks inspired by common SO problem classes."""
    out: list[Example] = []
    specs = [
        (
            "off-by-one range",
            "You need inclusive integers from 3 through 7. In Python, what is "
            "list(range(3, 8)) length?",
            "5",
            "range(start, stop) excludes stop; 3,4,5,6,7 → 5 values.",
            True,
        ),
        (
            "timezone naive",
            "Two naive datetime values differ by 3600 seconds locally. Does that "
            "prove they are one UTC hour apart? Answer yes or no.",
            "no",
            "Naive datetimes have no zone; DST and offset make local deltas unreliable as UTC.",
            True,
        ),
        (
            "json vs eval",
            "Should untrusted text be turned into a Python object with eval? yes or no.",
            "no",
            "eval executes code. Use json.loads for JSON payloads.",
            True,
        ),
        (
            "floating money",
            "Is binary float a safe ledger type for USD cents? yes or no.",
            "no",
            "Use integer cents or decimal. Decimal/float rounding is not cash-safe.",
            True,
        ),
        (
            "hash mutate",
            "A dict key is a list. After insertion you mutate the list. Is lookup by the "
            "new list guaranteed? yes or no.",
            "no",
            "Mutable keys are invalid; lists are unhashable. If a custom mutable key were used, mutation would break the table.",
            True,
        ),
        (
            "gil threads",
            "Two Python threads each run a tight CPU loop of bytecode. Will they typically "
            "use two cores at full speed under CPython's GIL? yes or no.",
            "no",
            "CPython's GIL usually serializes bytecode execution on one core.",
            True,
        ),
        (
            "sql null",
            "In SQL, does `NULL = NULL` evaluate to TRUE? yes or no.",
            "no",
            "NULL comparisons yield UNKNOWN; use IS NULL.",
            True,
        ),
        (
            "git detached",
            "You checkout a raw commit SHA. Are new commits still on a named branch? yes or no.",
            "no",
            "Detached HEAD: commits are not on a branch until you create/move one.",
            True,
        ),
    ]
    for i, (topic, prompt, answer, solution, check) in enumerate(specs):
        example = _emit(
            task_type="troubleshooting",
            prompt=prompt,
            answer=answer,
            solution=solution,
            observations=[f"inspired_by=stackoverflow topic={topic}", "verbatim=false"],
            constraints=["Original wording", "Not a copied post"],
            assumptions=["CPython / common SQL / git unless stated"],
            plan=["Identify the common pitfall", "Answer the yes/no or count"],
            key=f"so-r-{i}-{topic.replace(' ', '-')}",
            check=check,
        )
        if example:
            example.provenance = so_provenance()
            example.metadata = {**example.metadata, "inspired_by": "stackoverflow", "verbatim": False}
            out.append(example)
    return out


def extra_so_concept_examples() -> list[Example]:
    """Non-sandbox coding concepts still original and unlabeled as copied posts."""
    rows = [
        (
            "so-concept-iter-skip",
            "Why can you not iterate a dict and delete keys from it in the same loop in CPython?",
            "RuntimeError: dictionary changed size during iteration. Copy keys first or build a new dict.",
        ),
        (
            "so-concept-except-bare",
            "Why is `except:` (bare) a bad default in library code?",
            "It catches SystemExit and KeyboardInterrupt as well as bugs. Prefer except Exception.",
        ),
    ]
    out: list[Example] = []
    for key, prompt, answer in rows:
        out.append(
            build_example(
                domain=Domain.CODING,
                task_type="concept_explanation",
                prompt=prompt,
                answer=answer,
                solution=answer,
                provenance=so_provenance(),
                quality=reviewed_quality(
                    ["original Stack Overflow-inspired concept; not executed"]
                ),
                source_key=key,
                verification=None,
                constraints=["Original text", "verbatim=false"],
                plan=["State the language rule"],
                metadata={"inspired_by": "stackoverflow", "verbatim": False},
            )
        )
    return out
