"""Additional original Python tasks with executable tests (v1.0)."""

from __future__ import annotations

from open_reason.generation.coding_python import T, PyTask

V1_PYTHON_TASKS: list[PyTask] = [
    T(
        "rle_encode_runs",
        "algorithms",
        """Implement `rle_encode(text: str) -> str`.

Replace each maximal run of the same character with that character followed by
the run length in decimal. Empty input yields empty output. Example: `aaab` ->
`a3b1`.""",
        '''
def rle_encode(text):
    if not text:
        return ""
    out = []
    prev = text[0]
    count = 1
    for ch in text[1:]:
        if ch == prev:
            count += 1
        else:
            out.append(prev + str(count))
            prev = ch
            count = 1
    out.append(prev + str(count))
    return "".join(out)
''',
        '''
import unittest
from solution import rle_encode

class Test(unittest.TestCase):
    def test_runs(self):
        self.assertEqual(rle_encode("aaab"), "a3b1")
    def test_empty(self):
        self.assertEqual(rle_encode(""), "")
    def test_single(self):
        self.assertEqual(rle_encode("z"), "z1")
''',
    ),
    T(
        "interval_cover_count",
        "algorithms",
        """Implement `max_overlap(intervals) -> int`.

`intervals` is a list of half-open [start, end) pairs of ints with start < end.
Return the maximum number of intervals that cover any single integer point.
Empty input is 0.""",
        '''
def max_overlap(intervals):
    events = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))
    events.sort(key=lambda item: (item[0], item[1]))
    current = 0
    best = 0
    for _, delta in events:
        current += delta
        if current > best:
            best = current
    return best
''',
        '''
import unittest
from solution import max_overlap

class Test(unittest.TestCase):
    def test_overlap(self):
        self.assertEqual(max_overlap([(0, 2), (1, 3), (2, 4)]), 2)
    def test_empty(self):
        self.assertEqual(max_overlap([]), 0)
    def test_nested(self):
        self.assertEqual(max_overlap([(0, 10), (1, 2), (3, 4)]), 2)
''',
    ),
    T(
        "csv_row_split",
        "parsing",
        """Implement `split_csv_row(line: str) -> list[str]`.

Split a single CSV row on commas. Double-quoted fields may contain commas.
Quotes are escaped by doubling them. No newlines inside fields.""",
        '''
def split_csv_row(line):
    out = []
    field = []
    i = 0
    in_quotes = False
    while i < len(line):
        ch = line[i]
        if in_quotes:
            if ch == '"':
                if i + 1 < len(line) and line[i + 1] == '"':
                    field.append('"')
                    i += 1
                else:
                    in_quotes = False
            else:
                field.append(ch)
        else:
            if ch == '"':
                in_quotes = True
            elif ch == ",":
                out.append("".join(field))
                field = []
            else:
                field.append(ch)
        i += 1
    out.append("".join(field))
    return out
''',
        '''
import unittest
from solution import split_csv_row

class Test(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(split_csv_row("a,b,c"), ["a", "b", "c"])
    def test_quoted_comma(self):
        self.assertEqual(split_csv_row('a,"b,c",d'), ["a", "b,c", "d"])
    def test_escaped_quote(self):
        self.assertEqual(split_csv_row('"a""b"'), ['a"b'])
''',
    ),
    T(
        "topo_order_kahn",
        "graphs",
        """Implement `topo_order(nodes, edges) -> list`.

`nodes` is a list of unique hashable ids. `edges` is a list of (src, dst)
directed edges meaning src must come before dst. Return one valid topological
order. If the graph has a cycle, return None. Prefer the lexicographically
smallest node whenever several have indegree 0.""",
        '''
import heapq

def topo_order(nodes, edges):
    remaining = {node: 0 for node in nodes}
    adj = {node: [] for node in nodes}
    for src, dst in edges:
        adj[src].append(dst)
        remaining[dst] += 1
    heap = [node for node, deg in remaining.items() if deg == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        node = heapq.heappop(heap)
        order.append(node)
        for nxt in adj[node]:
            remaining[nxt] -= 1
            if remaining[nxt] == 0:
                heapq.heappush(heap, nxt)
    if len(order) != len(nodes):
        return None
    return order
''',
        '''
import unittest
from solution import topo_order

class Test(unittest.TestCase):
    def test_line(self):
        self.assertEqual(topo_order(["a", "b", "c"], [("a", "b"), ("b", "c")]), ["a", "b", "c"])
    def test_cycle(self):
        self.assertIsNone(topo_order(["a", "b"], [("a", "b"), ("b", "a")]))
    def test_lex(self):
        self.assertEqual(topo_order(["b", "a"], []), ["a", "b"])
''',
    ),
    T(
        "bitcount_bytes",
        "bit_twiddling",
        """Implement `popcount_bytes(data: bytes) -> int`.

Return the number of 1-bits in the byte string.""",
        '''
def popcount_bytes(data):
    return sum(bin(byte).count("1") for byte in data)
''',
        '''
import unittest
from solution import popcount_bytes

class Test(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(popcount_bytes(bytes([0, 0])), 0)
    def test_ff(self):
        self.assertEqual(popcount_bytes(bytes([255])), 8)
    def test_mixed(self):
        self.assertEqual(popcount_bytes(bytes([0x0F, 0xF0])), 8)
''',
    ),
    T(
        "json_pointer_get",
        "data",
        """Implement `pointer_get(doc, pointer: str)`.

`doc` is nested dict/list JSON-like data. `pointer` is a JSON Pointer
(RFC 6901) starting with `/` or empty for the whole document. Support `~0`
and `~1` escapes. Raise KeyError on missing keys or indexes.""",
        '''
def pointer_get(doc, pointer):
    if pointer == "":
        return doc
    if not pointer.startswith("/"):
        raise KeyError(pointer)
    current = doc
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(token)]
        else:
            if token not in current:
                raise KeyError(token)
            current = current[token]
    return current
''',
        '''
import unittest
from solution import pointer_get

class Test(unittest.TestCase):
    def test_root(self):
        self.assertEqual(pointer_get({"a": 1}, ""), {"a": 1})
    def test_nested(self):
        self.assertEqual(pointer_get({"a": {"b": 2}}, "/a/b"), 2)
    def test_escape(self):
        self.assertEqual(pointer_get({"a/b": 3}, "/a~1b"), 3)
''',
    ),
    T(
        "weekday_zeller",
        "dates",
        """Implement `weekday_name(year, month, day) -> str`.

Return the English weekday name (Monday..Sunday) for a Gregorian date in
the proleptic Gregorian calendar. Use datetime.date in the standard library.""",
        '''
import datetime

def weekday_name(year, month, day):
    names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return names[datetime.date(year, month, day).weekday()]
''',
        '''
import unittest
from solution import weekday_name

class Test(unittest.TestCase):
    def test_known(self):
        self.assertEqual(weekday_name(2026, 8, 18), "Tuesday")
    def test_unix(self):
        self.assertEqual(weekday_name(1970, 1, 1), "Thursday")
''',
    ),
    T(
        "stable_group_by",
        "data_structures",
        """Implement `group_by(items, key) -> list[tuple]`.

`key` is a function. Return a list of (key_value, group_list) in the order
keys first appear. Items in each group keep their original order.""",
        '''
def group_by(items, key):
    order = []
    groups = {}
    for item in items:
        k = key(item)
        if k not in groups:
            groups[k] = []
            order.append(k)
        groups[k].append(item)
    return [(k, groups[k]) for k in order]
''',
        '''
import unittest
from solution import group_by

class Test(unittest.TestCase):
    def test_order(self):
        rows = ["ax", "by", "az"]
        self.assertEqual(
            group_by(rows, lambda s: s[0]),
            [("a", ["ax", "az"]), ("b", ["by"])],
        )
    def test_empty(self):
        self.assertEqual(group_by([], lambda x: x), [])
''',
    ),
]


def v1_python_tasks() -> list[PyTask]:
    return list(V1_PYTHON_TASKS)
