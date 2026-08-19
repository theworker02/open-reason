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
    "flask": {
        "url": "https://github.com/pallets/flask/blob/3.1.0/src/flask/helpers.py",
        "license_spdx": "BSD-3-Clause",
        "commit": "3.1.0",
        "repo": "pallets/flask",
    },
    "urllib3": {
        "url": "https://github.com/urllib3/urllib3/blob/2.3.0/src/urllib3/util/url.py",
        "license_spdx": "MIT",
        "commit": "2.3.0",
        "repo": "urllib3/urllib3",
    },
    "pydantic": {
        "url": "https://github.com/pydantic/pydantic/blob/2.10.4/pydantic/type_adapter.py",
        "license_spdx": "MIT",
        "commit": "2.10.4",
        "repo": "pydantic/pydantic",
    },
    "rich": {
        "url": "https://github.com/Textualize/rich/blob/v13.9.4/rich/text.py",
        "license_spdx": "MIT",
        "commit": "v13.9.4",
        "repo": "Textualize/rich",
    },
    "httpcore": {
        "url": "https://github.com/encode/httpcore/blob/1.0.7/httpcore/_utils.py",
        "license_spdx": "BSD-3-Clause",
        "commit": "1.0.7",
        "repo": "encode/httpcore",
    },
    "black": {
        "url": "https://github.com/psf/black/blob/24.10.0/src/black/strings.py",
        "license_spdx": "MIT",
        "commit": "24.10.0",
        "repo": "psf/black",
    },
    "werkzeug": {
        "url": "https://github.com/pallets/werkzeug/blob/3.1.3/src/werkzeug/urls.py",
        "license_spdx": "BSD-3-Clause",
        "commit": "3.1.3",
        "repo": "pallets/werkzeug",
    },
    "attrs": {
        "url": "https://github.com/python-attrs/attrs/blob/24.3.0/src/attr/_next_gen.py",
        "license_spdx": "MIT",
        "commit": "24.3.0",
        "repo": "python-attrs/attrs",
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
        _with_src(
            T(
                "gh-secure-filename",
                "http",
                """Implement `secure_filename(name: str) -> str`.

Keep ASCII letters, digits, `.`, `_`, and `-`. Replace other characters with
`_`. Collapse runs of `_`. Strip leading/trailing `_` and `.`. Empty after
cleaning → `file`.""",
                '''
import re

def secure_filename(name):
    out = []
    for ch in name:
        if ch.isalnum() or ch in "._-":
            out.append(ch)
        else:
            out.append("_")
    cleaned = re.sub(r"_+", "_", "".join(out)).strip("_.")
    return cleaned or "file"
''',
                '''
import unittest
from solution import secure_filename

class Test(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(secure_filename("My Report.pdf"), "My_Report.pdf")
    def test_empty(self):
        self.assertEqual(secure_filename("***"), "file")
''',
            ),
            "flask",
        ),
        _with_src(
            T(
                "gh-split-host",
                "http",
                """Implement `split_hostport(authority: str) -> tuple[str, int | None]`.

`host:port` → (host, int(port)). Host only → (host, None). IPv6 in brackets
`[::1]:443` → ('::1', 443). Raise ValueError on empty host or non-int port.""",
                '''
def split_hostport(authority):
    if authority.startswith("["):
        end = authority.find("]")
        if end < 0:
            raise ValueError("ipv6")
        host = authority[1:end]
        rest = authority[end + 1:]
        if rest == "":
            port = None
        elif rest.startswith(":"):
            port = int(rest[1:])
        else:
            raise ValueError("ipv6")
        if not host:
            raise ValueError("host")
        return host, port
    if ":" in authority:
        host, port_s = authority.rsplit(":", 1)
        if not host or not port_s.isdigit():
            raise ValueError("hostport")
        return host, int(port_s)
    if not authority:
        raise ValueError("host")
    return authority, None
''',
                '''
import unittest
from solution import split_hostport

class Test(unittest.TestCase):
    def test_port(self):
        self.assertEqual(split_hostport("ex.com:80"), ("ex.com", 80))
    def test_host(self):
        self.assertEqual(split_hostport("ex.com"), ("ex.com", None))
    def test_v6(self):
        self.assertEqual(split_hostport("[::1]:443"), ("::1", 443))
''',
            ),
            "urllib3",
        ),
        _with_src(
            T(
                "gh-coerce-bool",
                "validation",
                """Implement `as_bool(value: str | bool | int) -> bool`.

True: True, 1, "1", "true", "yes", "on" (case-insensitive, strip).
False: False, 0, "0", "false", "no", "off". Raise ValueError otherwise.""",
                '''
def as_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        key = value.strip().lower()
        if key in {"1", "true", "yes", "on"}:
            return True
        if key in {"0", "false", "no", "off"}:
            return False
    raise ValueError("bool")
''',
                '''
import unittest
from solution import as_bool

class Test(unittest.TestCase):
    def test_true(self):
        self.assertTrue(as_bool(" YES "))
    def test_false(self):
        self.assertFalse(as_bool("off"))
    def test_bad(self):
        with self.assertRaises(ValueError):
            as_bool("maybe")
''',
            ),
            "pydantic",
        ),
        _with_src(
            T(
                "gh-ansi-strip",
                "terminal",
                """Implement `strip_ansi(text: str) -> str` removing CSI sequences
`ESC [ ... letter` where the final byte is A-Za-z. ESC is `\\x1b`.""",
                '''
import re

def strip_ansi(text):
    return re.sub(chr(27) + "[[][0-9;?]*[A-Za-z]", "", text)
''',
                '''
import unittest
from solution import strip_ansi

class Test(unittest.TestCase):
    def test_color(self):
        self.assertEqual(strip_ansi("a" + chr(27) + "[31mb"), "ab")
    def test_plain(self):
        self.assertEqual(strip_ansi("ok"), "ok")
''',
            ),
            "rich",
        ),
        _with_src(
            T(
                "gh-deadline",
                "http",
                """Implement `remaining_timeout(deadline: float, now: float) -> float`.

Return max(0.0, deadline-now). Used as a remaining HTTP timeout budget.""",
                '''
def remaining_timeout(deadline, now):
    return max(0.0, deadline - now)
''',
                '''
import unittest
from solution import remaining_timeout

class Test(unittest.TestCase):
    def test_left(self):
        self.assertEqual(remaining_timeout(10.0, 3.0), 7.0)
    def test_past(self):
        self.assertEqual(remaining_timeout(1.0, 5.0), 0.0)
''',
            ),
            "httpcore",
        ),
        _with_src(
            T(
                "gh-normalize-quotes",
                "formatting",
                """Implement `normalize_quotes(text: str) -> str`.

Replace curly quotes “ ” ‘ ’ (U+201C U+201D U+2018 U+2019) with ASCII
`"` and `'`.""",
                '''
def normalize_quotes(text):
    return (
        text.replace("\\u201c", '"')
        .replace("\\u201d", '"')
        .replace("\\u2018", "'")
        .replace("\\u2019", "'")
    )
''',
                '''
import unittest
from solution import normalize_quotes

class Test(unittest.TestCase):
    def test_curly(self):
        self.assertEqual(normalize_quotes("\\u201chello\\u201d"), '"hello"')
''',
            ),
            "black",
        ),
        _with_src(
            T(
                "gh-iri-quote",
                "urls",
                """Implement `quote_path(segment: str) -> str`.

Percent-encode bytes UTF-8. Unreserved: ALPHA / DIGIT / "-" / "." / "_" / "~".
Use uppercase hex.""",
                '''
def quote_path(segment):
    safe = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~")
    out = []
    for b in segment.encode("utf-8"):
        ch = chr(b)
        if ch in safe:
            out.append(ch)
        else:
            out.append(f"%{b:02X}")
    return "".join(out)
''',
                '''
import unittest
from solution import quote_path

class Test(unittest.TestCase):
    def test_space(self):
        self.assertEqual(quote_path("a b"), "a%20b")
    def test_safe(self):
        self.assertEqual(quote_path("a-b_c"), "a-b_c")
''',
            ),
            "werkzeug",
        ),
        _with_src(
            T(
                "gh-evolve-defaults",
                "objects",
                """Implement `with_overrides(base: dict, changes: dict) -> dict`.

Shallow copy of base then update from changes. Nested dict values of `changes`
replace entirely (no deep merge). Do not mutate `base`.""",
                '''
def with_overrides(base, changes):
    out = dict(base)
    out.update(changes)
    return out
''',
                '''
import unittest
from solution import with_overrides

class Test(unittest.TestCase):
    def test_copy(self):
        base = {"a": 1, "b": 2}
        got = with_overrides(base, {"b": 9})
        self.assertEqual(got, {"a": 1, "b": 9})
        self.assertEqual(base, {"a": 1, "b": 2})
''',
            ),
            "attrs",
        ),
    ]
