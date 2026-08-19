"""Original coding tasks inspired by permissive public GitHub repositories.

Implementations and tests are original Open Reason code. Rows record upstream
URL, SPDX, and commit. verbatim is false. GPL/AGPL/Reddit-derived material is
not used.
"""

from __future__ import annotations

from typing import Any

from open_reason.generation.coding_python import T, PyTask
from open_reason.models import Provenance, SourceType

# Pinned permissive snapshots inspected 2026-08-18 (attribution only).
GITHUB_SOURCES = {
    "requests": {
        "url": "https://github.com/psf/requests/blob/8f8b212de8c2129d7954c6cd373762880375620a/src/requests/utils.py",
        "license_spdx": "Apache-2.0",
        "commit": "8f8b212de8c2129d7954c6cd373762880375620a",
        "repo": "psf/requests",
    },
    "click": {
        "url": "https://github.com/pallets/click/blob/61b69e967e525bd502f5bf42def4d551e761fe0e/src/click/parser.py",
        "license_spdx": "BSD-3-Clause",
        "commit": "61b69e967e525bd502f5bf42def4d551e761fe0e",
        "repo": "pallets/click",
    },
    "httpx": {
        "url": "https://github.com/encode/httpx/blob/b5addb64f0161ff6bfe94c124ef76f6a1fba5254/httpx/_utils.py",
        "license_spdx": "BSD-3-Clause",
        "commit": "b5addb64f0161ff6bfe94c124ef76f6a1fba5254",
        "repo": "encode/httpx",
    },
    "jinja": {
        "url": "https://github.com/pallets/jinja/blob/5ef70112a1ff19c05324ff889dd30405b1002044/src/jinja2/filters.py",
        "license_spdx": "BSD-3-Clause",
        "commit": "5ef70112a1ff19c05324ff889dd30405b1002044",
        "repo": "pallets/jinja",
    },
}


def github_provenance(key: str) -> dict[str, Any]:
    meta = GITHUB_SOURCES[key]
    return Provenance(
        source_type=SourceType.OPEN_SOURCE,
        source="github_permissive",
        source_id=meta["repo"],
        source_url=meta["url"],
        license=meta["license_spdx"],
        license_spdx=meta["license_spdx"],
        commit=meta["commit"],
        derived=True,
        transformation="original_task_inspired_by_permissive_github; verbatim=false",
        trust_tier="tier5_implementation",
    ).model_dump(mode="json")


def _with_src(task: PyTask, key: str) -> PyTask:
    task = dict(task)
    task["provenance"] = github_provenance(key)
    task["metadata_extra"] = {
        "inspired_by": "github",
        "github_repo": GITHUB_SOURCES[key]["repo"],
        "verbatim": False,
    }
    return task


def github_python_tasks() -> list[PyTask]:
    return [
        _with_src(
            T(
                "gh-query-join",
                "http",
                """Implement `join_query(base: str, extra: dict[str, str]) -> str`.

`base` is a URL path plus optional `?a=1` query. Merge `extra` key/value pairs
(already encoded, no spaces) onto the query string. Preserve existing pairs.
If `base` has no `?`, add one when extra is non-empty. Do not add a trailing
`?` when extra is empty. Keys in extra override same keys in base.""",
                '''
def join_query(base, extra):
    if "?" in base:
        path, qs = base.split("?", 1)
        pairs = {}
        if qs:
            for part in qs.split("&"):
                if not part:
                    continue
                if "=" in part:
                    k, v = part.split("=", 1)
                    pairs[k] = v
                else:
                    pairs[part] = ""
        else:
            pairs = {}
    else:
        path, pairs = base, {}
    pairs.update(extra)
    if not pairs:
        return path
    joined = "&".join(f"{k}={v}" for k, v in pairs.items())
    return path + "?" + joined
''',
                '''
import unittest
from solution import join_query

class Test(unittest.TestCase):
    def test_merge(self):
        self.assertEqual(join_query("/x?a=1", {"b": "2"}), "/x?a=1&b=2")
    def test_override(self):
        self.assertEqual(join_query("/x?a=1", {"a": "9"}), "/x?a=9")
    def test_empty_extra(self):
        self.assertEqual(join_query("/x", {}), "/x")
    def test_add_q(self):
        self.assertEqual(join_query("/x", {"k": "v"}), "/x?k=v")
''',
            ),
            "requests",
        ),
        _with_src(
            T(
                "gh-retry-backoff",
                "http",
                """Implement `backoff_delays(retries: int, base: float = 0.5) -> list[float]`.

Return `retries` delays: base, 2*base, 4*base, ... (exponential). retries=0
returns []. Do not cap. Inspired by typical HTTP client retry spacing.""",
                '''
def backoff_delays(retries, base=0.5):
    return [base * (2 ** i) for i in range(retries)]
''',
                '''
import unittest
from solution import backoff_delays

class Test(unittest.TestCase):
    def test_three(self):
        self.assertEqual(backoff_delays(3, 0.5), [0.5, 1.0, 2.0])
    def test_zero(self):
        self.assertEqual(backoff_delays(0), [])
    def test_one(self):
        self.assertEqual(backoff_delays(1, 1.0), [1.0])
''',
            ),
            "httpx",
        ),
        _with_src(
            T(
                "gh-flag-parse",
                "cli",
                """Implement `parse_flags(argv: list[str]) -> dict`.

Treat tokens starting with `--` as flags. `--name value` stores value as str.
`--toggle` with no following non-flag token stores True. Positional tokens
(not after a flag) go to key `_`. Example: `['--n','2','file']` →
`{'n':'2', '_': ['file']}`.""",
                '''
def parse_flags(argv):
    out = {"_": []}
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok.startswith("--") and len(tok) > 2:
            name = tok[2:]
            if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                out[name] = argv[i + 1]
                i += 2
            else:
                out[name] = True
                i += 1
        else:
            out["_"].append(tok)
            i += 1
    return out
''',
                '''
import unittest
from solution import parse_flags

class Test(unittest.TestCase):
    def test_pair(self):
        self.assertEqual(parse_flags(["--n", "2", "file"]), {"n": "2", "_": ["file"]})
    def test_bool(self):
        self.assertEqual(parse_flags(["--verbose"]), {"verbose": True, "_": []})
    def test_pos_only(self):
        self.assertEqual(parse_flags(["a", "b"]), {"_": ["a", "b"]})
''',
            ),
            "click",
        ),
        _with_src(
            T(
                "gh-html-escape",
                "templates",
                """Implement `html_escape(text: str) -> str`.

Replace `&`, `<`, `>`, `"` and `'` with HTML entities `&amp;`, `&lt;`, `&gt;`,
`&quot;`, `&#39;`. Ampersand must be replaced first.""",
                '''
def html_escape(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )
''',
                '''
import unittest
from solution import html_escape

class Test(unittest.TestCase):
    def test_amp_first(self):
        self.assertEqual(html_escape("a&b<c"), "a&amp;b&lt;c")
    def test_quotes(self):
        self.assertEqual(html_escape("x\"y'z"), "x&quot;y&#39;z")
    def test_plain(self):
        self.assertEqual(html_escape("ok"), "ok")
''',
            ),
            "jinja",
        ),
        _with_src(
            T(
                "gh-header-merge",
                "http",
                """Implement `merge_headers(*maps: dict[str, str]) -> dict[str, str]`.

Later maps override earlier ones. Header names are compared case-insensitively
but the **last seen original casing** is kept as the key. Values are strings.""",
                '''
def merge_headers(*maps):
    order = []
    lower = {}
    for mapping in maps:
        for key, value in mapping.items():
            lk = key.lower()
            if lk in lower:
                order.remove(lower[lk][0])
            lower[lk] = (key, value)
            order.append(key)
    return {k: lower[k.lower()][1] for k in order}
''',
                '''
import unittest
from solution import merge_headers

class Test(unittest.TestCase):
    def test_override_case(self):
        got = merge_headers({"Accept": "a"}, {"accept": "b"})
        self.assertEqual(list(got.values()), ["b"])
        self.assertEqual(len(got), 1)
    def test_keep(self):
        got = merge_headers({"A": "1"}, {"B": "2"})
        self.assertEqual(got["A"], "1")
        self.assertEqual(got["B"], "2")
''',
            ),
            "httpx",
        ),
        _with_src(
            T(
                "gh-iter-chunks",
                "io",
                """Implement `iter_chunks(data: bytes, size: int) -> list[bytes]`.

Split `data` into consecutive chunks of at most `size` bytes. size must be > 0.
Empty data returns []. Last chunk may be shorter.""",
                '''
def iter_chunks(data, size):
    if size <= 0:
        raise ValueError("size")
    return [data[i:i + size] for i in range(0, len(data), size)]
''',
                '''
import unittest
from solution import iter_chunks

class Test(unittest.TestCase):
    def test_split(self):
        self.assertEqual(iter_chunks(b"abcdef", 2), [b"ab", b"cd", b"ef"])
    def test_short(self):
        self.assertEqual(iter_chunks(b"ab", 5), [b"ab"])
    def test_empty(self):
        self.assertEqual(iter_chunks(b"", 3), [])
''',
            ),
            "requests",
        ),
        _with_src(
            T(
                "gh-opt-env",
                "cli",
                """Implement `flag_or_env(flag: str | None, env: str | None, default: str) -> str`.

Precedence: non-empty flag, else non-empty env, else default. Whitespace-only
counts as empty.""",
                '''
def flag_or_env(flag, env, default):
    for item in (flag, env):
        if item is not None and item.strip():
            return item
    return default
''',
                '''
import unittest
from solution import flag_or_env

class Test(unittest.TestCase):
    def test_flag(self):
        self.assertEqual(flag_or_env("a", "b", "c"), "a")
    def test_env(self):
        self.assertEqual(flag_or_env("  ", "b", "c"), "b")
    def test_default(self):
        self.assertEqual(flag_or_env(None, None, "c"), "c")
''',
            ),
            "click",
        ),
        _with_src(
            T(
                "gh-safe-join",
                "paths",
                """Implement `safe_urljoin(base: str, path: str) -> str`.

If path is empty, return base without a trailing slash unless base is exactly
a scheme host like `https://ex`. If path starts with `/`, replace the path
portion of base. Otherwise append path to base, inserting `/` if needed.""",
                '''
def safe_urljoin(base, path):
    if not path:
        return base
    if path.startswith("/"):
        if "://" in base:
            scheme, rest = base.split("://", 1)
            host = rest.split("/", 1)[0]
            return f"{scheme}://{host}{path}"
        return path
    if base.endswith("/"):
        return base + path
    return base + "/" + path
''',
                '''
import unittest
from solution import safe_urljoin

class Test(unittest.TestCase):
    def test_rel(self):
        self.assertEqual(safe_urljoin("https://ex/a", "b"), "https://ex/a/b")
    def test_abs(self):
        self.assertEqual(safe_urljoin("https://ex/a/b", "/z"), "https://ex/z")
    def test_slash(self):
        self.assertEqual(safe_urljoin("https://ex/a/", "b"), "https://ex/a/b")
''',
            ),
            "requests",
        ),
    ]
