"""Additional original Python tasks for coverage of remaining coding topics."""

from __future__ import annotations

from open_reason.generation.coding_python import T, PyTask

EXTRA_PYTHON_TASKS: list[PyTask] = [
    T(
        "glob_match_star",
        "shell",
        """Implement `glob_match(pat, name)` supporting only `*` (any sequence) and
literal characters. No character classes. Match the whole name.""",
        '''
def glob_match(pat, name):
    def rec(i, j):
        if i == len(pat):
            return j == len(name)
        if pat[i] == "*":
            return rec(i + 1, j) or (j < len(name) and rec(i, j + 1))
        if j < len(name) and pat[i] == name[j]:
            return rec(i + 1, j + 1)
        return False
    return rec(0, 0)
''',
        '''
import unittest
from solution import glob_match

class Test(unittest.TestCase):
    def test_star(self):
        self.assertTrue(glob_match("a*c", "abbbc"))
        self.assertFalse(glob_match("a*c", "abbbd"))
        self.assertTrue(glob_match("*", ""))
''',
    ),
    T(
        "env_expand",
        "configuration",
        """Implement `expand_vars(text, env)` replacing `$NAME` and `${NAME}` where NAME
is `[A-Z_][A-Z0-9_]*`. Unknown names become empty string. Do not expand inside
single quotes `'...'`.""",
        '''
import re

TOKEN = re.compile(r"\\$({)?([A-Z_][A-Z0-9_]*)(?(1)})")

def expand_vars(text, env):
    out = []
    i = 0
    in_single = False
    while i < len(text):
        ch = text[i]
        if ch == "'" :
            in_single = not in_single
            out.append(ch)
            i += 1
            continue
        if not in_single and ch == "$":
            m = TOKEN.match(text, i)
            if m:
                out.append(env.get(m.group(2), ""))
                i = m.end()
                continue
        out.append(ch)
        i += 1
    return "".join(out)
''',
        '''
import unittest
from solution import expand_vars

class Test(unittest.TestCase):
    def test_expand(self):
        env = {"HOME": "/u", "A": "x"}
        self.assertEqual(expand_vars("$HOME/${A}", env), "/u/x")
        self.assertEqual(expand_vars("'$HOME'", env), "'$HOME'")
''',
    ),
    T(
        "systemd_wanted",
        "deployment",
        """Implement `parse_wantedby(unit_text)` returning the WantedBy= value from an
`[Install]` section, or None. Last matching line wins. Ignore comments.""",
        '''
def parse_wantedby(unit_text):
    section = None
    wanted = None
    for raw in unit_text.splitlines():
        line = raw.split(";", 1)[0].split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            continue
        if section == "Install" and line.startswith("WantedBy="):
            wanted = line.split("=", 1)[1].strip()
    return wanted
''',
        '''
import unittest
from solution import parse_wantedby

class Test(unittest.TestCase):
    def test_install(self):
        text = "[Unit]\\n[Install]\\nWantedBy=multi-user.target\\n"
        self.assertEqual(parse_wantedby(text), "multi-user.target")
''',
    ),
    T(
        "k8s_resource_parse",
        "deployment",
        """Implement `parse_cpu(value)` converting Kubernetes CPU strings: `100m` -> 0.1,
`2` -> 2.0. Raise ValueError otherwise.""",
        '''
def parse_cpu(value):
    if value.endswith("m") and value[:-1].isdigit():
        return int(value[:-1]) / 1000.0
    if value.replace(".", "", 1).isdigit():
        return float(value)
    raise ValueError(value)
''',
        '''
import unittest
from solution import parse_cpu

class Test(unittest.TestCase):
    def test_cpu(self):
        self.assertEqual(parse_cpu("100m"), 0.1)
        self.assertEqual(parse_cpu("2"), 2.0)
''',
    ),
    T(
        "ring_buffer",
        "data_structures",
        """Implement `Ring(n)` with `push(x)` (overwrite oldest when full) and
`snapshot()` returning items oldest-to-newest.""",
        '''
class Ring:
    def __init__(self, n):
        if n < 1:
            raise ValueError("n")
        self.buf = [None] * n
        self.n = n
        self.i = 0
        self.size = 0

    def push(self, x):
        self.buf[self.i] = x
        self.i = (self.i + 1) % self.n
        self.size = min(self.size + 1, self.n)

    def snapshot(self):
        start = (self.i - self.size) % self.n
        return [self.buf[(start + k) % self.n] for k in range(self.size)]
''',
        '''
import unittest
from solution import Ring

class Test(unittest.TestCase):
    def test_wrap(self):
        r = Ring(3)
        for x in range(5):
            r.push(x)
        self.assertEqual(r.snapshot(), [2, 3, 4])
''',
    ),
    T(
        "union_find",
        "data_structures",
        """Implement `UnionFind(n)` with 0..n-1 elements, `find(i)`, `union(i,j)`
returning True if they were in different sets. Use path compression and union by rank.""",
        '''
class UnionFind:
    def __init__(self, n):
        self.p = list(range(n))
        self.r = [0] * n

    def find(self, i):
        while self.p[i] != i:
            self.p[i] = self.p[self.p[i]]
            i = self.p[i]
        return i

    def union(self, i, j):
        a, b = self.find(i), self.find(j)
        if a == b:
            return False
        if self.r[a] < self.r[b]:
            a, b = b, a
        self.p[b] = a
        if self.r[a] == self.r[b]:
            self.r[a] += 1
        return True
''',
        '''
import unittest
from solution import UnionFind

class Test(unittest.TestCase):
    def test_uf(self):
        u = UnionFind(4)
        self.assertTrue(u.union(0, 1))
        self.assertTrue(u.union(2, 3))
        self.assertFalse(u.union(0, 1))
        self.assertEqual(u.find(0), u.find(1))
        self.assertNotEqual(u.find(0), u.find(2))
''',
    ),
    T(
        "knapsack_01",
        "algorithms",
        """Implement `knapsack(weights, values, cap)` 0/1 knapsack maximum value.""",
        '''
def knapsack(weights, values, cap):
    dp = [0] * (cap + 1)
    for w, v in zip(weights, values):
        for c in range(cap, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[cap]
''',
        '''
import unittest
from solution import knapsack

class Test(unittest.TestCase):
    def test_ks(self):
        self.assertEqual(knapsack([2, 3, 4], [3, 4, 5], 5), 7)
''',
    ),
    T(
        "bfs_levels",
        "algorithms",
        """Implement `bfs_order(graph, start)` returning nodes in BFS order. graph maps
node -> iterable of neighbors. Skip missing neighbor keys.""",
        '''
from collections import deque

def bfs_order(graph, start):
    seen = {start}
    q = deque([start])
    order = []
    while q:
        node = q.popleft()
        order.append(node)
        for nxt in graph.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return order
''',
        '''
import unittest
from solution import bfs_order

class Test(unittest.TestCase):
    def test_bfs(self):
        g = {1: [2, 3], 2: [4], 3: [], 4: []}
        self.assertEqual(bfs_order(g, 1), [1, 2, 3, 4])
''',
    ),
    T(
        "interval_coverage",
        "algorithms",
        """Implement `covered_length(ranges)` total length covered by [start,end]
half-open intervals. Overlaps count once.""",
        '''
def covered_length(ranges):
    if not ranges:
        return 0
    ordered = sorted(ranges)
    total = 0
    cs, ce = ordered[0]
    for s, e in ordered[1:]:
        if s > ce:
            total += ce - cs
            cs, ce = s, e
        else:
            ce = max(ce, e)
    total += ce - cs
    return total
''',
        '''
import unittest
from solution import covered_length

class Test(unittest.TestCase):
    def test_cover(self):
        self.assertEqual(covered_length([(0, 3), (2, 5), (10, 12)]), 7)
''',
    ),
    T(
        "rate_limit_sliding",
        "networking",
        """Implement `SlidingWindow(limit, window)` with `allow(t)` where t is
non-decreasing time. At most `limit` events in (t-window, t].""",
        '''
from collections import deque

class SlidingWindow:
    def __init__(self, limit, window):
        self.limit = limit
        self.window = window
        self.q = deque()

    def allow(self, t):
        while self.q and self.q[0] <= t - self.window:
            self.q.popleft()
        if len(self.q) >= self.limit:
            return False
        self.q.append(t)
        return True
''',
        '''
import unittest
from solution import SlidingWindow

class Test(unittest.TestCase):
    def test_sw(self):
        s = SlidingWindow(2, 10)
        self.assertTrue(s.allow(0))
        self.assertTrue(s.allow(1))
        self.assertFalse(s.allow(2))
        self.assertTrue(s.allow(11))
''',
    ),
    T(
        "base64_pad",
        "api_usage",
        """Implement `b64_pad(s)` adding the correct `=` padding to a base64 string
without padding. Do not decode.""",
        '''
def b64_pad(s):
    m = len(s) % 4
    if m == 1:
        raise ValueError("invalid")
    if m:
        s += "=" * (4 - m)
    return s
''',
        '''
import unittest
from solution import b64_pad

class Test(unittest.TestCase):
    def test_pad(self):
        self.assertEqual(b64_pad("TQ"), "TQ==")
        self.assertEqual(b64_pad("TWE"), "TWE=")
''',
    ),
    T(
        "retry_predicate",
        "devops",
        """Implement `retry(fn, retries, retry_on)` calling fn until it returns without
raising an exception in retry_on, up to retries+1 attempts. Re-raise the last.""",
        '''
def retry(fn, retries, retry_on):
    last = None
    for _ in range(retries + 1):
        try:
            return fn()
        except retry_on as exc:
            last = exc
    raise last
''',
        '''
import unittest
from solution import retry

class Test(unittest.TestCase):
    def test_retry(self):
        n = {"c": 0}
        def f():
            n["c"] += 1
            if n["c"] < 3:
                raise ValueError("x")
            return 7
        self.assertEqual(retry(f, 5, ValueError), 7)
        self.assertEqual(n["c"], 3)
''',
    ),
    T(
        "ini_sections",
        "configuration",
        """Implement `parse_ini(text)` returning dict[str, dict[str, str]] for
`[section]` and `key=value` lines. Ignore blanks and `;` comments.""",
        '''
def parse_ini(text):
    data = {}
    section = None
    for raw in text.splitlines():
        line = raw.split(";", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            data.setdefault(section, {})
            continue
        if section is None or "=" not in line:
            raise ValueError(line)
        k, v = line.split("=", 1)
        data[section][k.strip()] = v.strip()
    return data
''',
        '''
import unittest
from solution import parse_ini

class Test(unittest.TestCase):
    def test_ini(self):
        text = "[db]\\nhost=localhost\\n; c\\nport=1\\n"
        self.assertEqual(parse_ini(text), {"db": {"host": "localhost", "port": "1"}})
''',
    ),
    T(
        "dag_longest",
        "algorithms",
        """Implement `longest_path_dag(nodes, edges, weight)` where edges are (u,v)
and weight[(u,v)] is a number. Graph is DAG. Return the maximum path weight
(possibly a single node path of weight 0).""",
        '''
from collections import defaultdict, deque

def longest_path_dag(nodes, edges, weight):
    graph = defaultdict(list)
    indeg = {n: 0 for n in nodes}
    for u, v in edges:
        graph[u].append(v)
        indeg[v] += 1
    dist = {n: 0 for n in nodes}
    q = deque([n for n in nodes if indeg[n] == 0])
    seen = 0
    while q:
        u = q.popleft()
        seen += 1
        for v in graph[u]:
            dist[v] = max(dist[v], dist[u] + weight[(u, v)])
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    if seen != len(nodes):
        raise ValueError("not a dag")
    return max(dist.values())
''',
        '''
import unittest
from solution import longest_path_dag

class Test(unittest.TestCase):
    def test_lp(self):
        w = {("a", "b"): 2, ("b", "c"): 3, ("a", "c"): 4}
        self.assertEqual(longest_path_dag(["a", "b", "c"], [("a", "b"), ("b", "c"), ("a", "c")], w), 5)
''',
    ),
    T(
        "min_heap_k",
        "data_structures",
        """Implement `k_smallest(nums, k)` returning the k smallest values sorted
ascending. k may be 0. If k > n, return all sorted.""",
        '''
import heapq

def k_smallest(nums, k):
    if k <= 0:
        return []
    return sorted(heapq.nsmallest(min(k, len(nums)), nums))
''',
        '''
import unittest
from solution import k_smallest

class Test(unittest.TestCase):
    def test_k(self):
        self.assertEqual(k_smallest([5, 1, 4, 2], 2), [1, 2])
        self.assertEqual(k_smallest([3], 5), [3])
''',
    ),
    T(
        "sha256_prefix",
        "defensive_security",
        """Implement `constant_eq(a, b)` comparing two strings in time that depends
only on the length of the longer input (iterate zip_longest). Return True iff equal.""",
        '''
from itertools import zip_longest

def constant_eq(a, b):
    diff = 0
    for x, y in zip_longest(a, b, fillvalue=None):
        diff |= (x != y)
    return not diff
''',
        '''
import unittest
from solution import constant_eq

class Test(unittest.TestCase):
    def test_eq(self):
        self.assertTrue(constant_eq("abc", "abc"))
        self.assertFalse(constant_eq("abc", "ab"))
        self.assertFalse(constant_eq("abc", "abd"))
''',
    ),
    T(
        "log_level_filter",
        "cli_development",
        """Implement `filter_logs(lines, min_level)` where each line starts with
DEBUG|INFO|WARN|ERROR. Levels increase in that order. Keep lines at or above min_level.""",
        '''
ORDER = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3}

def filter_logs(lines, min_level):
    threshold = ORDER[min_level]
    out = []
    for line in lines:
        lvl = line.split(" ", 1)[0]
        if ORDER.get(lvl, -1) >= threshold:
            out.append(line)
    return out
''',
        '''
import unittest
from solution import filter_logs

class Test(unittest.TestCase):
    def test_filter(self):
        lines = ["DEBUG x", "INFO y", "ERROR z"]
        self.assertEqual(filter_logs(lines, "INFO"), ["INFO y", "ERROR z"])
''',
    ),
    T(
        "matrix_mul",
        "algorithms",
        """Implement `matmul(a, b)` for lists of lists of numbers. Raise ValueError
on shape mismatch.""",
        '''
def matmul(a, b):
    if not a or not b or len(a[0]) != len(b):
        raise ValueError("shape")
    cols = len(b[0])
    out = []
    for row in a:
        out.append([sum(row[k] * b[k][j] for k in range(len(b))) for j in range(cols)])
    return out
''',
        '''
import unittest
from solution import matmul

class Test(unittest.TestCase):
    def test_mul(self):
        self.assertEqual(matmul([[1, 2], [3, 4]], [[5, 6], [7, 8]]), [[19, 22], [43, 50]])
''',
    ),
    T(
        "huffman_freq",
        "algorithms",
        """Implement `char_freq(text)` returning a dict of character -> count,
omitting zeros. Empty string yields {}.""",
        '''
def char_freq(text):
    out = {}
    for ch in text:
        out[ch] = out.get(ch, 0) + 1
    return out
''',
        '''
import unittest
from solution import char_freq

class Test(unittest.TestCase):
    def test_freq(self):
        self.assertEqual(char_freq("aba"), {"a": 2, "b": 1})
''',
    ),
    T(
        "iso8601_date",
        "api_usage",
        """Implement `parse_ymd(s)` parsing YYYY-MM-DD into (y,m,d) ints. Validate
month 1-12 and day 1-31 (do not validate month lengths).""",
        '''
import re

def parse_ymd(s):
    m = re.fullmatch(r"(\\d{4})-(\\d{2})-(\\d{2})", s)
    if not m:
        raise ValueError(s)
    y, mo, d = (int(m.group(i)) for i in range(1, 4))
    if not 1 <= mo <= 12 or not 1 <= d <= 31:
        raise ValueError(s)
    return y, mo, d
''',
        '''
import unittest
from solution import parse_ymd

class Test(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(parse_ymd("2026-08-18"), (2026, 8, 18))
    def test_bad(self):
        with self.assertRaises(ValueError):
            parse_ymd("2026-13-01")
''',
    ),
    T(
        "queue_ttl",
        "distributed_systems",
        """Implement `ExpiredQueue` with `push(t, item)` and `pop_ready(now)` returning
all items with t <= now in insertion order and removing them.""",
        '''
from collections import deque

class ExpiredQueue:
    def __init__(self):
        self.q = deque()

    def push(self, t, item):
        self.q.append((t, item))

    def pop_ready(self, now):
        out = []
        while self.q and self.q[0][0] <= now:
            out.append(self.q.popleft()[1])
        return out
''',
        '''
import unittest
from solution import ExpiredQueue

class Test(unittest.TestCase):
    def test_pop(self):
        q = ExpiredQueue()
        q.push(2, "a")
        q.push(5, "b")
        self.assertEqual(q.pop_ready(3), ["a"])
        self.assertEqual(q.pop_ready(4), [])
        self.assertEqual(q.pop_ready(5), ["b"])
''',
    ),
    T(
        "crc_like_sum",
        "networking",
        """Implement `wrapping_checksum(data: bytes)` as (sum of bytes) mod 256.""",
        '''
def wrapping_checksum(data):
    return sum(data) % 256
''',
        '''
import unittest
from solution import wrapping_checksum

class Test(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(wrapping_checksum(bytes([255, 2])), 1)
''',
    ),
    T(
        "indent_blocks",
        "compiler_development",
        """Implement `block_depth(lines)` using leading 2-space indents. Return a list
of depths per non-empty line. Raise ValueError if indent is not a multiple of 2.""",
        '''
def block_depth(lines):
    out = []
    for line in lines:
        if not line.strip():
            continue
        spaces = len(line) - len(line.lstrip(" "))
        if spaces % 2:
            raise ValueError("indent")
        out.append(spaces // 2)
    return out
''',
        '''
import unittest
from solution import block_depth

class Test(unittest.TestCase):
    def test_d(self):
        self.assertEqual(block_depth(["a", "  b", "    c"]), [0, 1, 2])
''',
    ),
    T(
        "ssa_rename",
        "compiler_development",
        """Implement `fresh_names(vars)` assigning x, x#1, x#2, ... in order of first
appearance counts: given a list of variable uses, return a list of renamed
occurrences where the k-th use of name `v` becomes `v` then `v#1` etc.""",
        '''
def fresh_names(vars):
    seen = {}
    out = []
    for name in vars:
        n = seen.get(name, 0)
        out.append(name if n == 0 else f"{name}#{n}")
        seen[name] = n + 1
    return out
''',
        '''
import unittest
from solution import fresh_names

class Test(unittest.TestCase):
    def test_ren(self):
        self.assertEqual(fresh_names(["x", "y", "x"]), ["x", "y", "x#1"])
''',
    ),
    T(
        "lockfile_pin",
        "package_management",
        """Implement `format_pin(name, version)` as `name==version` after validating
name `[a-z0-9][a-z0-9._-]*` and version `[0-9]+(\\.[0-9]+)*`.""",
        '''
import re

def format_pin(name, version):
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", name):
        raise ValueError("name")
    if not re.fullmatch(r"[0-9]+(\\.[0-9]+)*", version):
        raise ValueError("version")
    return f"{name}=={version}"
''',
        '''
import unittest
from solution import format_pin

class Test(unittest.TestCase):
    def test_pin(self):
        self.assertEqual(format_pin("foo.bar", "1.2.3"), "foo.bar==1.2.3")
        with self.assertRaises(ValueError):
            format_pin("Foo", "1")
''',
    ),
    T(
        "yaml_indent_check",
        "configuration",
        """Implement `tabs_in_indent(text)` returning True if any line uses a tab in
its leading whitespace.""",
        '''
def tabs_in_indent(text):
    for line in text.splitlines():
        i = 0
        while i < len(line) and line[i] in " \\t":
            if line[i] == "\\t":
                return True
            i += 1
    return False
''',
        '''
import unittest
from solution import tabs_in_indent

class Test(unittest.TestCase):
    def test_tab(self):
        self.assertTrue(tabs_in_indent("a\\n\\tb\\n"))
        self.assertFalse(tabs_in_indent("a\\n  b\\n"))
''',
    ),
    T(
        "health_aggregate",
        "devops",
        """Implement `overall_health(checks)` where each check is `ok` or `fail`.
Return `fail` if any fail, `ok` if all ok, `unknown` if empty.""",
        '''
def overall_health(checks):
    if not checks:
        return "unknown"
    return "fail" if any(c == "fail" for c in checks) else "ok"
''',
        '''
import unittest
from solution import overall_health

class Test(unittest.TestCase):
    def test_h(self):
        self.assertEqual(overall_health(["ok", "fail"]), "fail")
        self.assertEqual(overall_health([]), "unknown")
''',
    ),
    T(
        "chunked_read",
        "cli_development",
        """Implement `chunks(seq, n)` yielding successive lists of length n, last
possibly shorter. n must be >= 1.""",
        '''
def chunks(seq, n):
    if n < 1:
        raise ValueError("n")
    buf = []
    for item in seq:
        buf.append(item)
        if len(buf) == n:
            yield buf
            buf = []
    if buf:
        yield buf
''',
        '''
import unittest
from solution import chunks

class Test(unittest.TestCase):
    def test_c(self):
        self.assertEqual(list(chunks([1, 2, 3, 4, 5], 2)), [[1, 2], [3, 4], [5]])
''',
    ),
    T(
        "expr_simplify_double_neg",
        "language_design",
        """AST nodes are tuples: ('neg', node) or ('num', int). Implement `simplify(node)`
cancelling double negation.""",
        '''
def simplify(node):
    if node[0] == "num":
        return node
    inner = simplify(node[1])
    if inner[0] == "neg":
        return inner[1]
    return ("neg", inner)
''',
        '''
import unittest
from solution import simplify

class Test(unittest.TestCase):
    def test_s(self):
        self.assertEqual(simplify(("neg", ("neg", ("num", 3)))), ("num", 3))
''',
    ),
    T(
        "histogram_ascii",
        "documentation",
        """Implement `spark(nums)` mapping each value to a bar character from
` .:-=+*#%@` by min-max scaling. Constant arrays become all last char. Return a string.""",
        '''
CHARS = " .:-=+*#%@"

def spark(nums):
    if not nums:
        return ""
    lo, hi = min(nums), max(nums)
    if lo == hi:
        return CHARS[-1] * len(nums)
    out = []
    for x in nums:
        idx = int((x - lo) / (hi - lo) * (len(CHARS) - 1))
        out.append(CHARS[idx])
    return "".join(out)
''',
        '''
import unittest
from solution import spark

class Test(unittest.TestCase):
    def test_sp(self):
        self.assertEqual(len(spark([0, 5, 10])), 3)
        self.assertEqual(spark([3, 3, 3]), "@@@")
''',
    ),
]


def extra_python_tasks() -> list[PyTask]:
    return list(EXTRA_PYTHON_TASKS)
