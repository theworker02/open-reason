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
        T(
            "so-round-half-even",
            "python",
            """Implement `bankers_cents(amount: float) -> int` converting a
dollar amount to integer cents with banker's rounding (round half to even)
on the cent. Example: 1.225 → 122 or 123 depending on the half-even rule
applied to tenths of a cent after multiplying by 100. Multiply by 100 then
use decimal ROUND_HALF_EVEN.""",
            '''
from decimal import Decimal, ROUND_HALF_EVEN

def bankers_cents(amount):
    d = Decimal(str(amount)) * Decimal("100")
    return int(d.quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))
''',
            '''
import unittest
from solution import bankers_cents

class Test(unittest.TestCase):
    def test_even(self):
        self.assertEqual(bankers_cents(1.0), 100)
    def test_half(self):
        self.assertEqual(bankers_cents(0.125), 12)
''',
        ),
        T(
            "so-json-strict",
            "python",
            """Implement `load_object(text: str) -> dict`.

Parse JSON with json.loads. Require a dict root. Raise ValueError otherwise.
Do not use eval.""",
            '''
import json

def load_object(text):
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("object")
    return data
''',
            '''
import unittest
from solution import load_object

class Test(unittest.TestCase):
    def test_obj(self):
        self.assertEqual(load_object('{"a": 1}'), {"a": 1})
    def test_list(self):
        with self.assertRaises(ValueError):
            load_object("[1]")
''',
        ),
        T(
            "so-tz-aware-diff",
            "python",
            """Implement `seconds_between(a, b) -> float` for timezone-aware
datetime objects. Return (b-a).total_seconds(). Raise TypeError if either is
naive (tzinfo is None).""",
            '''
def seconds_between(a, b):
    if a.tzinfo is None or b.tzinfo is None:
        raise TypeError("aware")
    return (b - a).total_seconds()
''',
            '''
import unittest
from datetime import datetime, timezone, timedelta
from solution import seconds_between

class Test(unittest.TestCase):
    def test_hour(self):
        a = datetime(2020, 1, 1, tzinfo=timezone.utc)
        b = a + timedelta(hours=1)
        self.assertEqual(seconds_between(a, b), 3600)
    def test_naive(self):
        with self.assertRaises(TypeError):
            seconds_between(datetime(2020, 1, 1), datetime(2020, 1, 2))
''',
        ),
        T(
            "so-context-cm",
            "python",
            """Implement class `TempValue` as a context manager: `__enter__`
returns the given value; `__exit__` swallows no exceptions (return False).""",
            '''
class TempValue:
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value

    def __exit__(self, exc_type, exc, tb):
        return False
''',
            '''
import unittest
from solution import TempValue

class Test(unittest.TestCase):
    def test_enter(self):
        with TempValue(3) as x:
            self.assertEqual(x, 3)
    def test_raise(self):
        with self.assertRaises(RuntimeError):
            with TempValue(1):
                raise RuntimeError("x")
''',
        ),
        T(
            "so-split-csv-line",
            "python",
            """Implement `split_simple_csv(line: str) -> list[str]`.

Split on commas that are not inside double quotes. Quotes are stripped from
quoted fields. No escaped quotes inside fields.""",
            '''
def split_simple_csv(line):
    out = []
    buf = []
    quoted = False
    for ch in line:
        if ch == '"':
            quoted = not quoted
            continue
        if ch == "," and not quoted:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    out.append("".join(buf))
    return out
''',
            '''
import unittest
from solution import split_simple_csv

class Test(unittest.TestCase):
    def test_q(self):
        self.assertEqual(split_simple_csv('a,"b,c",d'), ["a", "b,c", "d"])
    def test_plain(self):
        self.assertEqual(split_simple_csv("a,b"), ["a", "b"])
''',
        ),
        T(
            "so-retry-predicate",
            "python",
            """Implement `should_retry(status: int) -> bool`. True for 408, 425,
429, and 500-599 inclusive. False otherwise.""",
            '''
def should_retry(status):
    return status in {408, 425, 429} or 500 <= status <= 599
''',
            '''
import unittest
from solution import should_retry

class Test(unittest.TestCase):
    def test_yes(self):
        self.assertTrue(should_retry(503))
        self.assertTrue(should_retry(429))
    def test_no(self):
        self.assertFalse(should_retry(404))
        self.assertFalse(should_retry(200))
''',
        ),
        T(
            "so-path-suffix",
            "python",
            """Implement `with_suffix(path: str, suffix: str) -> str`.

Replace the final extension after the last `.` in the basename (after the
last `/`). If there is no `.` in the basename, append suffix. suffix includes
the dot, e.g. `.json`.""",
            '''
def with_suffix(path, suffix):
    if "/" in path:
        head, base = path.rsplit("/", 1)
        prefix = head + "/"
    else:
        prefix, base = "", path
    if "." in base:
        stem = base.rsplit(".", 1)[0]
        return prefix + stem + suffix
    return prefix + base + suffix
''',
            '''
import unittest
from solution import with_suffix

class Test(unittest.TestCase):
    def test_rep(self):
        self.assertEqual(with_suffix("a/b.txt", ".json"), "a/b.json")
    def test_add(self):
        self.assertEqual(with_suffix("readme", ".md"), "readme.md")
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
        (
            "utf8 vs latin1",
            "A file is UTF-8 bytes for é (C3 A9). If decoded as latin-1, do you get the single character é? yes or no.",
            "no",
            "Latin-1 maps each byte to a character, so two bytes become two characters, not U+00E9.",
            True,
        ),
        (
            "list multiply",
            "Does `[[0]]*3` create three independent inner lists in CPython? yes or no.",
            "no",
            "The inner list is aliased three times; mutating one row mutates all.",
            True,
        ),
        (
            "sql limit offset",
            "Is OFFSET 1000000 on a huge unordered table a cheap way to paginate in typical SQL engines? yes or no.",
            "no",
            "Large OFFSET still scans/skips prior rows. Keyset pagination is usually cheaper.",
            True,
        ),
        (
            "http put idempotent",
            "In HTTP semantics, is PUT to a known resource URL considered idempotent? yes or no.",
            "yes",
            "PUT replaces the resource at that URL; repeating it should leave the same stored state.",
            True,
        ),
        (
            "pytest fixture scope",
            "Does a function-scoped pytest fixture run once per test function that uses it (not once per module)? yes or no.",
            "yes",
            "Default fixture scope is function: setup/teardown around each test.",
            True,
        ),
        (
            "docker layer cache",
            "If you COPY requirements then RUN pip, then COPY source, does changing only source typically reuse the pip layer? yes or no.",
            "yes",
            "Docker caches layers; an unchanged COPY requirements + pip layer is reused when only later source changes.",
            True,
        ),
        (
            "css specificity",
            "Does an ID selector beat a class selector in CSS specificity (assuming equal importance)? yes or no.",
            "yes",
            "IDs outrank classes in the specificity tuple.",
            True,
        ),
        (
            "npm lockfile",
            "Should a library publish usually commit package-lock.json if the project is an application? yes or no.",
            "yes",
            "Applications pin the tree with a lockfile so installs reproduce. (Libraries may omit it; this question is about apps.)",
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
