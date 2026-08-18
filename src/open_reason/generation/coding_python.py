"""Original Python coding tasks with executable tests.

Prompts are original. Algorithms may be standard, but statements are not copied
from HumanEval, MBPP, or LeetCode.
"""

from __future__ import annotations

from typing import Any

PyTask = dict[str, Any]


def T(
    slug: str,
    topic: str,
    prompt: str,
    code: str,
    tests: str,
    *,
    bug: str | None = None,
    bug_note: str | None = None,
    task_type: str = "code_generation",
    extra_files: dict[str, str] | None = None,
) -> PyTask:
    return {
        "slug": slug,
        "topic": topic,
        "prompt": prompt.strip(),
        "code": code.strip() + "\n",
        "tests": tests.strip() + "\n",
        "bug": (bug.strip() + "\n") if bug else None,
        "bug_note": bug_note,
        "task_type": task_type,
        "extra_files": extra_files or {},
    }


PYTHON_TASKS: list[PyTask] = [
    T(
        "nested_delimiter_scan",
        "algorithms",
        """Implement `delimiters_ok(text: str) -> bool`.

Return True if every round, square, and curly bracket in `text` is correctly
nested and matched. All other characters are ignored. Empty input is valid.""",
        '''
def delimiters_ok(text):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return not stack
''',
        '''
import unittest
from solution import delimiters_ok

class Test(unittest.TestCase):
    def test_mixed(self):
        self.assertTrue(delimiters_ok("fn(a[i], {x: 1})"))
    def test_crossed(self):
        self.assertFalse(delimiters_ok("([)]"))
    def test_extra_close(self):
        self.assertFalse(delimiters_ok("ok)"))
    def test_ignore_other(self):
        self.assertTrue(delimiters_ok(""))
''',
        bug='''
def delimiters_ok(text):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return True
''',
        bug_note="Ignores leftover unclosed openers.",
    ),
    T(
        "window_max_sum",
        "algorithms",
        """Implement `max_window_sum(values, k)` returning the maximum sum of any
contiguous subarray of length `k`. If `k` is larger than the list, raise ValueError.""",
        '''
def max_window_sum(values, k):
    if k <= 0 or k > len(values):
        raise ValueError("invalid window")
    current = sum(values[:k])
    best = current
    for i in range(k, len(values)):
        current += values[i] - values[i - k]
        if current > best:
            best = current
    return best
''',
        '''
import unittest
from solution import max_window_sum

class Test(unittest.TestCase):
    def test_example(self):
        self.assertEqual(max_window_sum([2, 1, 5, 1, 3, 2], 3), 9)
    def test_k_one(self):
        self.assertEqual(max_window_sum([-4, 8, -1], 1), 8)
    def test_bad(self):
        with self.assertRaises(ValueError):
            max_window_sum([1, 2], 3)
''',
        bug='''
def max_window_sum(values, k):
    if k <= 0 or k > len(values):
        raise ValueError("invalid window")
    current = sum(values[:k])
    best = current
    for i in range(k, len(values)):
        current += values[i]
        if current > best:
            best = current
    return best
''',
        bug_note="Forgets to subtract the value leaving the window.",
    ),
    T(
        "stable_group_by",
        "data_structures",
        """Implement `group_in_order(items, key_fn)` that groups consecutive items with
the same key, preserving first-seen group order for non-consecutive keys as well
(like an insertion-ordered map of lists). Return a list of (key, group_list) pairs.""",
        '''
def group_in_order(items, key_fn):
    order = []
    buckets = {}
    for item in items:
        key = key_fn(item)
        if key not in buckets:
            buckets[key] = []
            order.append(key)
        buckets[key].append(item)
    return [(key, buckets[key]) for key in order]
''',
        '''
import unittest
from solution import group_in_order

class Test(unittest.TestCase):
    def test_order(self):
        data = ["apple", "apricot", "banana", "avocado"]
        got = group_in_order(data, lambda s: s[0])
        self.assertEqual([k for k, _ in got], ["a", "b"])
        self.assertEqual(got[0][1], ["apple", "apricot", "avocado"])
''',
    ),
    T(
        "lru_cache_map",
        "data_structures",
        """Implement class `TinyLRU(capacity)` with `get(key)` (return None if missing)
and `put(key, value)`. Evict the least recently used entry when over capacity.
Both get and put count as use.""",
        '''
from collections import OrderedDict

class TinyLRU:
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity")
        self.capacity = capacity
        self._data = OrderedDict()

    def get(self, key):
        if key not in self._data:
            return None
        self._data.move_to_end(key)
        return self._data[key]

    def put(self, key, value):
        if key in self._data:
            self._data.move_to_end(key)
            self._data[key] = value
        else:
            self._data[key] = value
            if len(self._data) > self.capacity:
                self._data.popitem(last=False)
''',
        '''
import unittest
from solution import TinyLRU

class Test(unittest.TestCase):
    def test_evict(self):
        c = TinyLRU(2)
        c.put("a", 1)
        c.put("b", 2)
        c.get("a")
        c.put("c", 3)
        self.assertIsNone(c.get("b"))
        self.assertEqual(c.get("a"), 1)
        self.assertEqual(c.get("c"), 3)
''',
        bug='''
from collections import OrderedDict

class TinyLRU:
    def __init__(self, capacity):
        self.capacity = capacity
        self._data = OrderedDict()

    def get(self, key):
        return self._data.get(key)

    def put(self, key, value):
        self._data[key] = value
        if len(self._data) > self.capacity:
            self._data.popitem(last=False)
''',
        bug_note="get() does not refresh recency.",
    ),
    T(
        "binary_search_first",
        "algorithms",
        """Implement `first_ge(sorted_values, target)` returning the smallest index i
such that sorted_values[i] >= target, or len(sorted_values) if none exists.
The list is sorted non-decreasing.""",
        '''
def first_ge(sorted_values, target):
    lo, hi = 0, len(sorted_values)
    while lo < hi:
        mid = (lo + hi) // 2
        if sorted_values[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
''',
        '''
import unittest
from solution import first_ge

class Test(unittest.TestCase):
    def test_mid(self):
        self.assertEqual(first_ge([1, 3, 3, 7, 9], 3), 1)
    def test_end(self):
        self.assertEqual(first_ge([1, 2, 4], 5), 3)
    def test_first(self):
        self.assertEqual(first_ge([2, 4, 6], 0), 0)
''',
        bug='''
def first_ge(sorted_values, target):
    lo, hi = 0, len(sorted_values) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if sorted_values[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return lo
''',
        bug_note="Off-by-one on empty-range and first-equal cases.",
    ),
    T(
        "merge_intervals",
        "algorithms",
        """Implement `merge_ranges(ranges)` where each range is [start, end] with
start <= end. Return a new list of disjoint merged ranges sorted by start.""",
        '''
def merge_ranges(ranges):
    if not ranges:
        return []
    ordered = sorted(ranges, key=lambda r: r[0])
    out = [list(ordered[0])]
    for start, end in ordered[1:]:
        if start <= out[-1][1]:
            out[-1][1] = max(out[-1][1], end)
        else:
            out.append([start, end])
    return out
''',
        '''
import unittest
from solution import merge_ranges

class Test(unittest.TestCase):
    def test_overlap(self):
        self.assertEqual(merge_ranges([[1, 3], [2, 6], [8, 10]]), [[1, 6], [8, 10]])
    def test_touch(self):
        self.assertEqual(merge_ranges([[1, 2], [2, 3]]), [[1, 3]])
    def test_empty(self):
        self.assertEqual(merge_ranges([]), [])
''',
    ),
    T(
        "topo_order",
        "algorithms",
        """Implement `topo_sort(nodes, edges)` for a directed acyclic graph.
`nodes` is a list of hashable ids. `edges` is a list of (src, dst) meaning
src must come before dst. Return any valid topological order. Raise ValueError
if a cycle exists.""",
        '''
from collections import defaultdict, deque

def topo_sort(nodes, edges):
    incoming = {n: 0 for n in nodes}
    graph = defaultdict(list)
    for src, dst in edges:
        graph[src].append(dst)
        incoming[dst] = incoming.get(dst, 0) + 1
        incoming.setdefault(src, incoming.get(src, 0))
    ready = deque([n for n in nodes if incoming.get(n, 0) == 0])
    order = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for nxt in graph[node]:
            incoming[nxt] -= 1
            if incoming[nxt] == 0:
                ready.append(nxt)
    if len(order) != len(nodes):
        raise ValueError("cycle")
    return order
''',
        '''
import unittest
from solution import topo_sort

class Test(unittest.TestCase):
    def test_chain(self):
        order = topo_sort(["a", "b", "c"], [("a", "b"), ("b", "c")])
        self.assertEqual(order, ["a", "b", "c"])
    def test_cycle(self):
        with self.assertRaises(ValueError):
            topo_sort(["a", "b"], [("a", "b"), ("b", "a")])
''',
    ),
    T(
        "dijkstra_hops",
        "algorithms",
        """Implement `shortest_cost(graph, start, goal)` where graph maps node ->
list of (neighbor, weight) with non-negative weights. Return the minimum cost
or None if unreachable.""",
        '''
import heapq

def shortest_cost(graph, start, goal):
    best = {start: 0}
    heap = [(0, start)]
    while heap:
        cost, node = heapq.heappop(heap)
        if cost != best.get(node, None):
            continue
        if node == goal:
            return cost
        for nxt, weight in graph.get(node, []):
            cand = cost + weight
            if cand < best.get(nxt, float("inf")):
                best[nxt] = cand
                heapq.heappush(heap, (cand, nxt))
    return None
''',
        '''
import unittest
from solution import shortest_cost

class Test(unittest.TestCase):
    def test_path(self):
        g = {"s": [("a", 2), ("b", 5)], "a": [("g", 2)], "b": [("g", 1)], "g": []}
        self.assertEqual(shortest_cost(g, "s", "g"), 4)
    def test_missing(self):
        self.assertIsNone(shortest_cost({"s": []}, "s", "z"))
''',
    ),
    T(
        "heap_median",
        "data_structures",
        """Implement class `RunningMedian` with `add(x)` and `median()` (mean of the
two center values when the count is even). Values are numbers.""",
        '''
import heapq

class RunningMedian:
    def __init__(self):
        self.low = []
        self.high = []

    def add(self, x):
        if not self.low or x <= -self.low[0]:
            heapq.heappush(self.low, -x)
        else:
            heapq.heappush(self.high, x)
        if len(self.low) > len(self.high) + 1:
            heapq.heappush(self.high, -heapq.heappop(self.low))
        elif len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def median(self):
        if not self.low:
            raise ValueError("empty")
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2.0
''',
        '''
import unittest
from solution import RunningMedian

class Test(unittest.TestCase):
    def test_stream(self):
        r = RunningMedian()
        for x in [5, 2, 8, 1]:
            r.add(x)
        self.assertEqual(r.median(), 3.5)
''',
    ),
    T(
        "parse_kv_config",
        "configuration",
        """Implement `parse_kv(text)` for a tiny config language:
- ignore blank lines and lines starting with `#`
- remaining lines are `key = value` (value trimmed, may contain =)
- duplicate keys: last wins
Return a dict. Raise ValueError on lines without `=`.""",
        '''
def parse_kv(text):
    result = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(line)
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result
''',
        '''
import unittest
from solution import parse_kv

class Test(unittest.TestCase):
    def test_parse(self):
        text = "# c\\nport = 80\\nhost = a=b\\nport = 8080\\n"
        self.assertEqual(parse_kv(text), {"port": "8080", "host": "a=b"})
    def test_bad(self):
        with self.assertRaises(ValueError):
            parse_kv("oops")
''',
    ),
    T(
        "semver_core_cmp",
        "package_management",
        """Implement `cmp_semver(a, b)` comparing MAJOR.MINOR.PATCH strings (digits
only, no pre-release). Return -1, 0, or 1.""",
        '''
def cmp_semver(a, b):
    def parts(s):
        bits = s.split(".")
        if len(bits) != 3 or not all(p.isdigit() for p in bits):
            raise ValueError(s)
        return tuple(int(p) for p in bits)
    left, right = parts(a), parts(b)
    return (left > right) - (left < right)
''',
        '''
import unittest
from solution import cmp_semver

class Test(unittest.TestCase):
    def test_cmp(self):
        self.assertEqual(cmp_semver("1.2.0", "1.10.0"), -1)
        self.assertEqual(cmp_semver("2.0.0", "2.0.0"), 0)
        self.assertEqual(cmp_semver("1.0.1", "1.0.0"), 1)
''',
        bug='''
def cmp_semver(a, b):
    return (a > b) - (a < b)
''',
        bug_note="Compares as strings so 1.10.0 < 1.2.0.",
    ),
    T(
        "dep_resolution_pins",
        "dependency_resolution",
        """Implement `pins_ok(declared, locked)` where declared maps package ->
minimum inclusive version tuple (major, minor, patch) and locked maps package
-> installed version tuple. Every declared package must be present and
installed >= minimum. Extra locked packages are allowed.""",
        '''
def pins_ok(declared, locked):
    for name, minimum in declared.items():
        if name not in locked:
            return False
        if locked[name] < minimum:
            return False
    return True
''',
        '''
import unittest
from solution import pins_ok

class Test(unittest.TestCase):
    def test_ok(self):
        self.assertTrue(pins_ok({"a": (1, 2, 0)}, {"a": (1, 2, 3), "b": (0, 1, 0)}))
    def test_missing(self):
        self.assertFalse(pins_ok({"a": (1, 0, 0)}, {}))
    def test_old(self):
        self.assertFalse(pins_ok({"a": (2, 0, 0)}, {"a": (1, 9, 9)}))
''',
    ),
    T(
        "sql_ident_quote",
        "databases",
        """Implement `quote_ident(name)` for a conservative SQL identifier:
accept only `[A-Za-z_][A-Za-z0-9_]*` and wrap in double quotes with internal
quotes doubled. Raise ValueError otherwise. This is defensive quoting, not a
parser for arbitrary SQL.""",
        '''
import re

def quote_ident(name):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        raise ValueError("invalid identifier")
    return '"' + name.replace('"', '""') + '"'
''',
        '''
import unittest
from solution import quote_ident

class Test(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(quote_ident("user_id"), '"user_id"')
    def test_reject(self):
        with self.assertRaises(ValueError):
            quote_ident("user-id")
        with self.assertRaises(ValueError):
            quote_ident("1x")
''',
    ),
    T(
        "parameterized_filter",
        "defensive_security",
        """Implement `safe_select_by_id(conn, table, row_id)` using sqlite3.
`table` must match `[a-z_]+`. Execute a parameterized query
`SELECT * FROM {table} WHERE id = ?` and return the list of rows.
Never interpolate `row_id` into the SQL string.""",
        '''
import re

def safe_select_by_id(conn, table, row_id):
    if not re.fullmatch(r"[a-z_]+", table):
        raise ValueError("table")
    sql = f'SELECT * FROM "{table}" WHERE id = ?'
    return list(conn.execute(sql, (row_id,)))
''',
        '''
import sqlite3
import unittest
from solution import safe_select_by_id

class Test(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("CREATE TABLE items (id INTEGER, name TEXT)")
        self.conn.execute("INSERT INTO items VALUES (1, 'a'), (2, 'b')")

    def test_param(self):
        rows = safe_select_by_id(self.conn, "items", 2)
        self.assertEqual(rows, [(2, "b")])

    def test_injection_value(self):
        rows = safe_select_by_id(self.conn, "items", "2 OR 1=1")
        self.assertEqual(rows, [])

    def test_bad_table(self):
        with self.assertRaises(ValueError):
            safe_select_by_id(self.conn, "items;drop", 1)
''',
    ),
    T(
        "path_confine",
        "defensive_security",
        """Implement `resolve_under(root, relative)` that joins `relative` to `root`
and returns the resolved path only if it stays inside `root`. Reject `..`
escapes. Use pathlib. Raise ValueError on escape.""",
        '''
from pathlib import Path

def resolve_under(root, relative):
    base = Path(root).resolve()
    target = (base / relative).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise ValueError("escape") from exc
    return str(target)
''',
        '''
import tempfile
import unittest
from pathlib import Path
from solution import resolve_under

class Test(unittest.TestCase):
    def test_inside(self):
        with tempfile.TemporaryDirectory() as td:
            p = resolve_under(td, "a/b.txt")
            self.assertTrue(p.startswith(str(Path(td).resolve())))
    def test_escape(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                resolve_under(td, "../secret")
''',
    ),
    T(
        "cidr_contains",
        "networking",
        """Implement `ipv4_in_cidr(ip, cidr)` where ip is dotted IPv4 and cidr is
like `10.0.0.0/8`. Return True iff the address is in the prefix. No extra
libraries beyond stdlib.""",
        '''
import ipaddress

def ipv4_in_cidr(ip, cidr):
    return ipaddress.IPv4Address(ip) in ipaddress.IPv4Network(cidr, strict=False)
''',
        '''
import unittest
from solution import ipv4_in_cidr

class Test(unittest.TestCase):
    def test_in(self):
        self.assertTrue(ipv4_in_cidr("10.1.2.3", "10.0.0.0/8"))
    def test_out(self):
        self.assertFalse(ipv4_in_cidr("11.0.0.1", "10.0.0.0/8"))
    def test_exact(self):
        self.assertTrue(ipv4_in_cidr("192.0.2.1", "192.0.2.1/32"))
''',
    ),
    T(
        "fcfs_finish",
        "operating_systems",
        """Implement `fcfs_completion(jobs)` where each job is (arrival, burst) and
jobs are already ordered by arrival time (ties keep given order). Return a list
of completion times in the same order. The CPU is idle until the next arrival
if needed.""",
        '''
def fcfs_completion(jobs):
    time = 0
    done = []
    for arrival, burst in jobs:
        time = max(time, arrival) + burst
        done.append(time)
    return done
''',
        '''
import unittest
from solution import fcfs_completion

class Test(unittest.TestCase):
    def test_idle(self):
        self.assertEqual(fcfs_completion([(0, 3), (5, 2)]), [3, 7])
    def test_queue(self):
        self.assertEqual(fcfs_completion([(0, 2), (1, 2)]), [2, 4])
''',
    ),
    T(
        "round_robin_trace",
        "operating_systems",
        """Implement `rr_finish(bursts, quantum)` for processes all arriving at 0,
indexed 0..n-1, using a FIFO ready queue. Return completion times list.
Ignore context-switch cost.""",
        '''
from collections import deque

def rr_finish(bursts, quantum):
    remaining = list(bursts)
    finish = [None] * len(bursts)
    q = deque(range(len(bursts)))
    t = 0
    while q:
        i = q.popleft()
        run = min(quantum, remaining[i])
        remaining[i] -= run
        t += run
        if remaining[i] == 0:
            finish[i] = t
        else:
            q.append(i)
    return finish
''',
        '''
import unittest
from solution import rr_finish

class Test(unittest.TestCase):
    def test_rr(self):
        self.assertEqual(rr_finish([5, 3, 1], 2), [9, 8, 5])
''',
    ),
    T(
        "lru_page_faults",
        "operating_systems",
        """Implement `lru_faults(pages, frames)` counting page faults with LRU
replacement among `frames` slots. Empty frames fill first.""",
        '''
def lru_faults(pages, frames):
    slot = []
    used = []
    faults = 0
    for page in pages:
        if page in slot:
            used.remove(page)
            used.append(page)
            continue
        faults += 1
        if len(slot) < frames:
            slot.append(page)
        else:
            victim = used.pop(0)
            idx = slot.index(victim)
            slot[idx] = page
        used.append(page)
    return faults
''',
        '''
import unittest
from solution import lru_faults

class Test(unittest.TestCase):
    def test_classic(self):
        self.assertEqual(lru_faults([1, 2, 3, 1, 4, 2], 3), 5)
''',
    ),
    T(
        "banker_safe",
        "operating_systems",
        """Implement `is_safe(available, allocation, need)` for the Banker's algorithm
safety check. `available` is a list of resource counts. `allocation` and `need`
are lists of per-process lists. Return True iff a safe sequence exists.""",
        '''
def is_safe(available, allocation, need):
    work = list(available)
    finish = [False] * len(allocation)
    while True:
        progressed = False
        for i, done in enumerate(finish):
            if done:
                continue
            if all(need[i][j] <= work[j] for j in range(len(work))):
                for j in range(len(work)):
                    work[j] += allocation[i][j]
                finish[i] = True
                progressed = True
        if not progressed:
            break
    return all(finish)
''',
        '''
import unittest
from solution import is_safe

class Test(unittest.TestCase):
    def test_safe(self):
        self.assertTrue(is_safe([3], [[0], [1], [1]], [[1], [0], [2]]))
    def test_unsafe(self):
        self.assertFalse(is_safe([0], [[1], [1]], [[1], [1]]))
''',
    ),
    T(
        "token_bucket",
        "networking",
        """Implement class `TokenBucket(rate, burst)` with `allow(time, cost=1)`.
`rate` is tokens per time unit, `burst` is max tokens. Start full at t=0.
`time` is non-decreasing. Return True if the request is admitted.""",
        '''
class TokenBucket:
    def __init__(self, rate, burst):
        self.rate = rate
        self.burst = burst
        self.tokens = float(burst)
        self.t = 0.0

    def allow(self, time, cost=1):
        if time < self.t:
            raise ValueError("time")
        self.tokens = min(self.burst, self.tokens + (time - self.t) * self.rate)
        self.t = time
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False
''',
        '''
import unittest
from solution import TokenBucket

class Test(unittest.TestCase):
    def test_burst_then_refill(self):
        b = TokenBucket(1.0, 2)
        self.assertTrue(b.allow(0))
        self.assertTrue(b.allow(0))
        self.assertFalse(b.allow(0))
        self.assertTrue(b.allow(1.0))
''',
    ),
    T(
        "json_pointer_get",
        "api_usage",
        """Implement `json_get(doc, pointer)` for a subset of RFC 6901: pointer is
'' for the whole document, or `/seg/seg` with `~1` -> `/` and `~0` -> `~`.
Arrays are indexed by decimal strings. Raise KeyError on missing paths.""",
        '''
def json_get(doc, pointer):
    if pointer == "":
        return doc
    if not pointer.startswith("/"):
        raise ValueError("pointer")
    current = doc
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            idx = int(token)
            current = current[idx]
        else:
            if token not in current:
                raise KeyError(pointer)
            current = current[token]
    return current
''',
        '''
import unittest
from solution import json_get

class Test(unittest.TestCase):
    def test_nested(self):
        doc = {"a": [{"b": 3}]}
        self.assertEqual(json_get(doc, "/a/0/b"), 3)
    def test_escape(self):
        doc = {"~": {"x/y": 1}}
        self.assertEqual(json_get(doc, "/~0/~1"), 1)
''',
    ),
    T(
        "openapi_required",
        "api_design",
        """Implement `missing_required(schema, payload)` where schema is
`{"required": [...], "properties": {name: {"type": "string"|"number"|"boolean"}}}`.
Return sorted names that are missing or have the wrong JSON type.
Extra payload keys are ignored.""",
        '''
def missing_required(schema, payload):
    types = {"string": str, "number": (int, float), "boolean": bool}
    bad = []
    for name in schema.get("required", []):
        if name not in payload:
            bad.append(name)
            continue
        declared = schema["properties"][name]["type"]
        if declared == "number" and isinstance(payload[name], bool):
            bad.append(name)
            continue
        if not isinstance(payload[name], types[declared]):
            bad.append(name)
    return sorted(bad)
''',
        '''
import unittest
from solution import missing_required

class Test(unittest.TestCase):
    def test_types(self):
        schema = {
            "required": ["id", "ok"],
            "properties": {"id": {"type": "number"}, "ok": {"type": "boolean"}},
        }
        self.assertEqual(missing_required(schema, {"id": True, "ok": True}), ["id"])
        self.assertEqual(missing_required(schema, {"id": 1, "ok": True}), [])
''',
    ),
    T(
        "layer_ports",
        "architecture",
        """Implement `allowed_import(from_layer, to_layer, rules)` where layers are
strings and rules is a list of (src, dst) allowed edges. A module may always
import from its own layer. Return True iff the import is permitted.""",
        '''
def allowed_import(from_layer, to_layer, rules):
    if from_layer == to_layer:
        return True
    allowed = set(rules)
    return (from_layer, to_layer) in allowed
''',
        '''
import unittest
from solution import allowed_import

class Test(unittest.TestCase):
    def test_hex(self):
        rules = [("app", "domain"), ("infra", "domain")]
        self.assertTrue(allowed_import("app", "domain", rules))
        self.assertFalse(allowed_import("domain", "infra", rules))
        self.assertTrue(allowed_import("domain", "domain", rules))
''',
    ),
    T(
        "infix_rpn_eval",
        "interpreters",
        """Implement `eval_rpn(tokens)` for integers and + - * / (integer division
toward zero is NOT required: use Python `//` toward -inf). Tokens are strings.""",
        '''
def eval_rpn(tokens):
    stack = []
    ops = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: a // b,
    }
    for tok in tokens:
        if tok in ops:
            b = stack.pop()
            a = stack.pop()
            stack.append(ops[tok](a, b))
        else:
            stack.append(int(tok))
    if len(stack) != 1:
        raise ValueError("rpn")
    return stack[0]
''',
        '''
import unittest
from solution import eval_rpn

class Test(unittest.TestCase):
    def test_expr(self):
        self.assertEqual(eval_rpn(["2", "3", "4", "*", "+"]), 14)
    def test_div(self):
        self.assertEqual(eval_rpn(["7", "2", "/"]), 3)
''',
    ),
    T(
        "mini_typecheck_unify",
        "type_systems",
        """Implement `unify(a, b)` for a tiny type language: types are strings
('Int', 'Bool') or lists ['Fun', t1, t2]. Variables are strings starting with
`?`. Return a dict substitution or None on failure. Do not need occurs-check
beyond rejecting assigning a variable to a type that contains it as a nested list.""",
        '''
def occurs(var, typ):
    if typ == var:
        return True
    if isinstance(typ, list):
        return any(occurs(var, part) for part in typ[1:])
    return False

def apply_sub(sub, typ):
    if isinstance(typ, str):
        return sub.get(typ, typ)
    return [typ[0], *(apply_sub(sub, p) for p in typ[1:])]

def unify(a, b, sub=None):
    sub = dict(sub or {})
    a, b = apply_sub(sub, a), apply_sub(sub, b)
    if a == b:
        return sub
    if isinstance(a, str) and a.startswith("?"):
        if occurs(a, b):
            return None
        sub[a] = b
        return sub
    if isinstance(b, str) and b.startswith("?"):
        return unify(b, a, sub)
    if isinstance(a, list) and isinstance(b, list) and a[0] == b[0] and len(a) == len(b):
        for x, y in zip(a[1:], b[1:]):
            sub = unify(x, y, sub)
            if sub is None:
                return None
        return sub
    return None
''',
        '''
import unittest
from solution import unify

class Test(unittest.TestCase):
    def test_fun(self):
        s = unify(["Fun", "?a", "Int"], ["Fun", "Bool", "?b"])
        self.assertEqual(s["?a"], "Bool")
        self.assertEqual(s["?b"], "Int")
    def test_fail(self):
        self.assertIsNone(unify("Int", "Bool"))
''',
    ),
    T(
        "static_unused",
        "static_analysis",
        """Implement `unused_assigns(lines)` for a toy language: lines are
`x = ...` or `use x`. Names are `[a-z]+`. Return sorted names assigned at
least once and never used. Later use counts.""",
        '''
import re

def unused_assigns(lines):
    assigned = set()
    used = set()
    for line in lines:
        m = re.fullmatch(r"([a-z]+) = .*", line.strip())
        if m:
            assigned.add(m.group(1))
            continue
        m = re.fullmatch(r"use ([a-z]+)", line.strip())
        if m:
            used.add(m.group(1))
    return sorted(assigned - used)
''',
        '''
import unittest
from solution import unused_assigns

class Test(unittest.TestCase):
    def test_unused(self):
        self.assertEqual(unused_assigns(["a = 1", "b = 2", "use a"]), ["b"])
''',
    ),
    T(
        "doc_extract_params",
        "documentation",
        """Implement `google_args(docstring)` extracting Args from a Google-style
docstring. Return a list of (name, description) for lines indented like
`    name: desc`. Ignore other sections.""",
        '''
def google_args(docstring):
    lines = docstring.splitlines()
    out = []
    in_args = False
    for line in lines:
        if line.strip() == "Args:":
            in_args = True
            continue
        if in_args and line.strip().endswith(":") and not line.startswith(" "):
            break
        if in_args:
            stripped = line.strip()
            if ": " in stripped:
                name, desc = stripped.split(": ", 1)
                out.append((name, desc))
    return out
''',
        '''
import unittest
from solution import google_args

class Test(unittest.TestCase):
    def test_args(self):
        doc = """Do a thing.\\n\\nArgs:\\n    count: how many\\n    name: label\\n\\nReturns:\\n    none\\n"""
        self.assertEqual(google_args(doc), [("count", "how many"), ("name", "label")])
''',
    ),
    T(
        "migrate_rename_keys",
        "migration",
        """Implement `migrate_v1_to_v2(payload)` renaming keys `userName`->`username`
and `emailAddress`->`email`, leaving other keys. Missing keys stay missing.""",
        '''
def migrate_v1_to_v2(payload):
    mapping = {"userName": "username", "emailAddress": "email"}
    return {mapping.get(k, k): v for k, v in payload.items()}
''',
        '''
import unittest
from solution import migrate_v1_to_v2

class Test(unittest.TestCase):
    def test_rename(self):
        self.assertEqual(
            migrate_v1_to_v2({"userName": "a", "keep": 1}),
            {"username": "a", "keep": 1},
        )
''',
    ),
    T(
        "compat_flag",
        "compatibility",
        """Implement `api_supported(client, server)` where versions are (major, minor).
Compatible iff major matches and client.minor <= server.minor.""",
        '''
def api_supported(client, server):
    return client[0] == server[0] and client[1] <= server[1]
''',
        '''
import unittest
from solution import api_supported

class Test(unittest.TestCase):
    def test_ok(self):
        self.assertTrue(api_supported((1, 2), (1, 4)))
        self.assertFalse(api_supported((1, 5), (1, 4)))
        self.assertFalse(api_supported((2, 0), (1, 9)))
''',
    ),
    T(
        "dockerfile_user",
        "containers",
        """Implement `dockerfile_runs_as_root(text)` returning True if the last
USER instruction is missing or is `USER root` / `USER 0` (ignoring case on
root). Comment lines starting with # are ignored.""",
        '''
def dockerfile_runs_as_root(text):
    user = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts[0].upper() == "USER":
            user = parts[1] if len(parts) > 1 else ""
    if user is None:
        return True
    return user.lower() == "root" or user == "0"
''',
        '''
import unittest
from solution import dockerfile_runs_as_root

class Test(unittest.TestCase):
    def test_last_user(self):
        text = "FROM alpine\\nUSER root\\nUSER app\\n"
        self.assertFalse(dockerfile_runs_as_root(text))
        self.assertTrue(dockerfile_runs_as_root("FROM alpine\\n"))
''',
    ),
    T(
        "compose_depends",
        "distributed_systems",
        """Implement `startup_order(depends)` where depends maps service -> list of
services it needs first. Return a topological order. Raise ValueError on cycles.""",
        '''
from collections import defaultdict, deque

def startup_order(depends):
    nodes = set(depends)
    for deps in depends.values():
        nodes.update(deps)
    incoming = {n: 0 for n in nodes}
    graph = defaultdict(list)
    for svc, deps in depends.items():
        for dep in deps:
            graph[dep].append(svc)
            incoming[svc] += 1
    ready = deque([n for n in nodes if incoming[n] == 0])
    order = []
    while ready:
        n = ready.popleft()
        order.append(n)
        for m in graph[n]:
            incoming[m] -= 1
            if incoming[m] == 0:
                ready.append(m)
    if len(order) != len(nodes):
        raise ValueError("cycle")
    return order
''',
        '''
import unittest
from solution import startup_order

class Test(unittest.TestCase):
    def test_order(self):
        order = startup_order({"web": ["api"], "api": ["db"], "db": []})
        self.assertEqual(order[:1], ["db"])
        self.assertLess(order.index("api"), order.index("web"))
''',
    ),
    T(
        "async_gather_ok",
        "asynchronous_programming",
        """Implement `first_true(predicates)` where predicates is a list of zero-arg
callables. Return the index of the first that returns a truthy value, or -1.
Later predicates must not be called after success (short-circuit).""",
        '''
def first_true(predicates):
    for i, fn in enumerate(predicates):
        if fn():
            return i
    return -1
''',
        '''
import unittest
from solution import first_true

class Test(unittest.TestCase):
    def test_short(self):
        calls = []
        def a():
            calls.append("a")
            return False
        def b():
            calls.append("b")
            return True
        def c():
            calls.append("c")
            return True
        self.assertEqual(first_true([a, b, c]), 1)
        self.assertEqual(calls, ["a", "b"])
''',
    ),
    T(
        "mutex_counter",
        "concurrency",
        """Implement `threaded_increment(n_threads, n_each)` that starts n_threads
threads each adding n_each to a shared integer behind a threading.Lock.
Return the final count (must equal n_threads * n_each).""",
        '''
import threading

def threaded_increment(n_threads, n_each):
    lock = threading.Lock()
    value = {"n": 0}

    def worker():
        for _ in range(n_each):
            with lock:
                value["n"] += 1

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return value["n"]
''',
        '''
import unittest
from solution import threaded_increment

class Test(unittest.TestCase):
    def test_count(self):
        self.assertEqual(threaded_increment(4, 50), 200)
''',
    ),
    T(
        "two_sum_index",
        "algorithms",
        """Implement `pair_indices(nums, target)` returning a pair of distinct indices
i < j such that nums[i] + nums[j] == target, or None. Prefer the lexicographically
smallest (i, j).""",
        '''
def pair_indices(nums, target):
    seen = {}
    best = None
    for i, value in enumerate(nums):
        need = target - value
        if need in seen:
            cand = (seen[need], i)
            if best is None or cand < best:
                best = cand
        if value not in seen:
            seen[value] = i
    return best
''',
        '''
import unittest
from solution import pair_indices

class Test(unittest.TestCase):
    def test_pair(self):
        self.assertEqual(pair_indices([2, 7, 11, 15], 9), (0, 1))
    def test_none(self):
        self.assertIsNone(pair_indices([1, 2, 3], 100))
''',
    ),
    T(
        "edit_distance_k",
        "algorithms",
        """Implement `within_edit(a, b, k)` True iff Levenshtein distance(a, b) <= k.
You may use DP. Strings are short.""",
        '''
def within_edit(a, b, k):
    if abs(len(a) - len(b)) > k:
        return False
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        row = [i]
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            row.append(min(row[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost))
        prev = row
    return prev[-1] <= k
''',
        '''
import unittest
from solution import within_edit

class Test(unittest.TestCase):
    def test_k(self):
        self.assertTrue(within_edit("kitten", "sitting", 3))
        self.assertFalse(within_edit("kitten", "sitting", 2))
''',
    ),
    T(
        "cycle_list",
        "data_structures",
        """Represent a singly linked list as nodes `{"v": value, "n": next_or_None}`.
Implement `has_cycle(head)` using constant extra memory (Floyd).""",
        '''
def has_cycle(head):
    slow = head
    fast = head
    while fast and fast["n"]:
        slow = slow["n"]
        fast = fast["n"]["n"]
        if slow is fast:
            return True
    return False
''',
        '''
import unittest
from solution import has_cycle

class Test(unittest.TestCase):
    def test_cycle(self):
        a = {"v": 1, "n": None}
        b = {"v": 2, "n": None}
        c = {"v": 3, "n": None}
        a["n"], b["n"], c["n"] = b, c, b
        self.assertTrue(has_cycle(a))
        d = {"v": 1, "n": {"v": 2, "n": None}}
        self.assertFalse(has_cycle(d))
''',
    ),
    T(
        "bst_validate",
        "data_structures",
        """Nodes are `{"v": int, "l": node|None, "r": node|None}`. Implement
`is_bst(root)` with strict ordering (left < v < right) for the whole tree.""",
        '''
def is_bst(root, lo=None, hi=None):
    if root is None:
        return True
    v = root["v"]
    if lo is not None and v <= lo:
        return False
    if hi is not None and v >= hi:
        return False
    return is_bst(root["l"], lo, v) and is_bst(root["r"], v, hi)
''',
        '''
import unittest
from solution import is_bst

class Test(unittest.TestCase):
    def test_ok(self):
        tree = {"v": 2, "l": {"v": 1, "l": None, "r": None}, "r": {"v": 3, "l": None, "r": None}}
        self.assertTrue(is_bst(tree))
    def test_bad(self):
        tree = {"v": 1, "l": {"v": 2, "l": None, "r": None}, "r": None}
        self.assertFalse(is_bst(tree))
''',
    ),
    T(
        "cli_argv",
        "cli_development",
        """Implement `parse_flags(argv)` for a tiny CLI: flags `--name value` and
boolean `--verbose` present-or-not. Remaining tokens are positional.
Return `{"flags": dict, "args": list}`. `--verbose` maps to True.""",
        '''
def parse_flags(argv):
    flags = {}
    args = []
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok == "--verbose":
            flags["verbose"] = True
            i += 1
        elif tok.startswith("--"):
            name = tok[2:]
            if i + 1 >= len(argv):
                raise ValueError("missing")
            flags[name] = argv[i + 1]
            i += 2
        else:
            args.append(tok)
            i += 1
    return {"flags": flags, "args": args}
''',
        '''
import unittest
from solution import parse_flags

class Test(unittest.TestCase):
    def test_mix(self):
        got = parse_flags(["--name", "or", "file", "--verbose"])
        self.assertEqual(got["flags"]["name"], "or")
        self.assertTrue(got["flags"]["verbose"])
        self.assertEqual(got["args"], ["file"])
''',
    ),
    T(
        "makefile_targets",
        "build_systems",
        """Implement `make_targets(text)` extracting target names from lines matching
`target: deps` at column 0 (no leading whitespace). Skip `.PHONY` and comments.""",
        '''
def make_targets(text):
    names = []
    for raw in text.splitlines():
        if not raw or raw.startswith("\\t") or raw.startswith(" ") or raw.startswith("#"):
            continue
        if ":" not in raw:
            continue
        target = raw.split(":", 1)[0].strip()
        if target and target != ".PHONY":
            names.append(target)
    return names
''',
        '''
import unittest
from solution import make_targets

class Test(unittest.TestCase):
    def test_names(self):
        text = ".PHONY: all\\nall: build\\nbuild:\\n\\techo x\\n"
        self.assertEqual(make_targets(text), ["all", "build"])
''',
    ),
    T(
        "ci_junit_counts",
        "ci_cd",
        """Implement `junit_counts(xml)` for a tiny subset: count `failures=` and
`tests=` on the first `<testsuite ...>` tag using regex. Return
`{"tests": int, "failures": int}`.""",
        '''
import re

def junit_counts(xml):
    m = re.search(r"<testsuite\\b[^>]*>", xml)
    if not m:
        raise ValueError("no testsuite")
    tag = m.group(0)
    tests = int(re.search(r'tests="(\\d+)"', tag).group(1))
    failures = int(re.search(r'failures="(\\d+)"', tag).group(1))
    return {"tests": tests, "failures": failures}
''',
        '''
import unittest
from solution import junit_counts

class Test(unittest.TestCase):
    def test_parse(self):
        xml = '<testsuite tests="10" failures="2"></testsuite>'
        self.assertEqual(junit_counts(xml), {"tests": 10, "failures": 2})
''',
    ),
    T(
        "healthcheck_backoff",
        "devops",
        """Implement `backoff_delays(retries, base, cap)` returning a list of length
`retries` with delays min(cap, base * 2**i) for i=0..retries-1.""",
        '''
def backoff_delays(retries, base, cap):
    return [min(cap, base * (2 ** i)) for i in range(retries)]
''',
        '''
import unittest
from solution import backoff_delays

class Test(unittest.TestCase):
    def test_cap(self):
        self.assertEqual(backoff_delays(5, 1, 8), [1, 2, 4, 8, 8])
''',
    ),
    T(
        "hot_path_count",
        "performance_optimization",
        """Implement `majority_nlogn_forbidden(nums)` finding the element that
appears more than n/2 times. Use Boyer-Moore. Guarantee O(n) time, O(1) extra
memory aside from the input. The input is guaranteed to have a majority.""",
        '''
def majority(nums):
    vote = 0
    cand = None
    for x in nums:
        if vote == 0:
            cand = x
        vote += 1 if x == cand else -1
    return cand
''',
        '''
import unittest
from solution import majority

class Test(unittest.TestCase):
    def test_maj(self):
        self.assertEqual(majority([1, 2, 1, 1, 3, 1, 1]), 1)
''',
    ),
    T(
        "arena_bump",
        "memory_management",
        """Implement class `BumpArena(size)` with `alloc(n)` returning the start
offset of n contiguous bytes or None if it will not fit, and `reset()` to
free everything. No coalescing needed.""",
        '''
class BumpArena:
    def __init__(self, size):
        self.size = size
        self.offset = 0

    def alloc(self, n):
        if n < 0 or self.offset + n > self.size:
            return None
        start = self.offset
        self.offset += n
        return start

    def reset(self):
        self.offset = 0
''',
        '''
import unittest
from solution import BumpArena

class Test(unittest.TestCase):
    def test_alloc(self):
        a = BumpArena(10)
        self.assertEqual(a.alloc(4), 0)
        self.assertEqual(a.alloc(4), 4)
        self.assertIsNone(a.alloc(4))
        a.reset()
        self.assertEqual(a.alloc(10), 0)
''',
    ),
    T(
        "tokenize_c_idents",
        "compiler_development",
        """Implement `c_idents(source)` returning identifiers matching
`[A-Za-z_][A-Za-z0-9_]*` in order, skipping those inside double-quoted strings.
Do not handle escapes other than `\\\\` and `\\"`. Comments are not supported.""",
        '''
def c_idents(source):
    ident = []
    out = []
    i = 0
    n = len(source)
    while i < n:
        ch = source[i]
        if ch == '"':
            i += 1
            while i < n:
                if source[i] == "\\\\":
                    i += 2
                    continue
                if source[i] == '"':
                    i += 1
                    break
                i += 1
            continue
        if ch.isalnum() or ch == "_":
            j = i
            while j < n and (source[j].isalnum() or source[j] == "_"):
                j += 1
            token = source[i:j]
            if token[0].isalpha() or token[0] == "_":
                out.append(token)
            i = j
            continue
        i += 1
    return out
''',
        '''
import unittest
from solution import c_idents

class Test(unittest.TestCase):
    def test_skip_string(self):
        src = 'int x = "not_an_ident"; y = 1;'
        self.assertEqual(c_idents(src), ["int", "x", "y"])
''',
    ),
    T(
        "refcount_toy",
        "language_design",
        """Implement class `Rc` with `inc()`, `dec()`, and `alive()` for a toy
refcount. `dec` below zero raises ValueError. Start at 1.""",
        '''
class Rc:
    def __init__(self):
        self.count = 1

    def inc(self):
        self.count += 1

    def dec(self):
        if self.count <= 0:
            raise ValueError("underflow")
        self.count -= 1

    def alive(self):
        return self.count > 0
''',
        '''
import unittest
from solution import Rc

class Test(unittest.TestCase):
    def test_rc(self):
        r = Rc()
        r.inc()
        r.dec()
        self.assertTrue(r.alive())
        r.dec()
        self.assertFalse(r.alive())
''',
    ),
    T(
        "zip_longest_fill",
        "refactoring",
        """Implement `zip_fill(*seqs, fill=None)` equivalent to padding all sequences
to the longest length then zipping. Return a list of tuples.""",
        '''
def zip_fill(*seqs, fill=None):
    seqs = [list(s) for s in seqs]
    if not seqs:
        return []
    n = max(len(s) for s in seqs)
    out = []
    for i in range(n):
        out.append(tuple(s[i] if i < len(s) else fill for s in seqs))
    return out
''',
        '''
import unittest
from solution import zip_fill

class Test(unittest.TestCase):
    def test_pad(self):
        self.assertEqual(zip_fill([1, 2], ["a"], fill="?"), [(1, "a"), (2, "?")])
''',
    ),
    T(
        "coverage_uncovered",
        "test_generation",
        """Implement `uncovered(lines, hit)` where `lines` is a set of executable line
numbers and `hit` is a list of line numbers executed (with duplicates). Return
sorted executable lines that never appear in `hit`.""",
        '''
def uncovered(lines, hit):
    seen = set(hit)
    return sorted(n for n in lines if n not in seen)
''',
        '''
import unittest
from solution import uncovered

class Test(unittest.TestCase):
    def test_gap(self):
        self.assertEqual(uncovered({1, 2, 3, 4}, [1, 1, 3]), [2, 4])
''',
    ),
    T(
        "flake_rerun",
        "test_debugging",
        """Implement `classify_flaky(results)` where results is a list of bool pass/fail
for the same test. Return `pass` if all True, `fail` if all False, `flaky` otherwise.""",
        '''
def classify_flaky(results):
    if not results:
        raise ValueError("empty")
    if all(results):
        return "pass"
    if not any(results):
        return "fail"
    return "flaky"
''',
        '''
import unittest
from solution import classify_flaky

class Test(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(classify_flaky([True, True]), "pass")
        self.assertEqual(classify_flaky([False, False]), "fail")
        self.assertEqual(classify_flaky([True, False, True]), "flaky")
''',
    ),
    T(
        "review_complexity",
        "code_review",
        """Implement `nested_loop_depth(source)` counting the maximum nesting of
lines that strip-start with `for ` or `while ` based on leading indent (4 spaces).
This is a review heuristic, not a Python parser.""",
        '''
def nested_loop_depth(source):
    best = 0
    for raw in source.splitlines():
        if not raw.strip():
            continue
        indent = (len(raw) - len(raw.lstrip(" "))) // 4
        stripped = raw.strip()
        if stripped.startswith("for ") or stripped.startswith("while "):
            best = max(best, indent + 1)
    return best
''',
        '''
import unittest
from solution import nested_loop_depth

class Test(unittest.TestCase):
    def test_depth(self):
        src = "for a in x:\\n    for b in y:\\n        z()\\n"
        self.assertEqual(nested_loop_depth(src), 2)
''',
    ),
    T(
        "wasm_leb_u32",
        "language_design",
        """Implement `decode_uleb128(data: bytes)` decoding one unsigned LEB128
integer from the start of data and returning (value, bytes_consumed).""",
        '''
def decode_uleb128(data):
    result = 0
    shift = 0
    for i, byte in enumerate(data):
        result |= (byte & 0x7F) << shift
        if byte & 0x80 == 0:
            return result, i + 1
        shift += 7
        if shift > 35:
            raise ValueError("overflow")
    raise ValueError("truncated")
''',
        '''
import unittest
from solution import decode_uleb128

class Test(unittest.TestCase):
    def test_small(self):
        self.assertEqual(decode_uleb128(bytes([127])), (127, 1))
    def test_multi(self):
        self.assertEqual(decode_uleb128(bytes([0xE5, 0x8E, 0x26])), (624485, 3))
''',
    ),
]


def all_python_tasks() -> list[PyTask]:
    return list(PYTHON_TASKS)
