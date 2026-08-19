"""Original Python tasks for v1.0.1: more languages of thought, not paraphrases.

Includes error-diagnosis items with explicit failing baselines. Sandbox tests
must pass for quality.verified.
"""

from __future__ import annotations

from open_reason.generation.coding_python import T, PyTask

V101_PYTHON_TASKS: list[PyTask] = [
    T(
        "bfs_hops",
        "graphs",
        """Implement `hops(graph, start, goal) -> int`.

`graph` maps a node to a list of neighbors (undirected: you still only follow
listed edges). Return the fewest edges from start to goal, or -1 if unreachable.
Nodes are hashable.""",
        '''
from collections import deque

def hops(graph, start, goal):
    if start == goal:
        return 0
    seen = {start}
    q = deque([(start, 0)])
    while q:
        node, dist = q.popleft()
        for nxt in graph.get(node, []):
            if nxt in seen:
                continue
            if nxt == goal:
                return dist + 1
            seen.add(nxt)
            q.append((nxt, dist + 1))
    return -1
''',
        '''
import unittest
from solution import hops

class Test(unittest.TestCase):
    def test_path(self):
        g = {"a": ["b"], "b": ["c"], "c": []}
        self.assertEqual(hops(g, "a", "c"), 2)
    def test_self(self):
        self.assertEqual(hops({"x": []}, "x", "x"), 0)
    def test_missing(self):
        self.assertEqual(hops({"a": ["b"], "b": []}, "a", "z"), -1)
''',
        bug='''
from collections import deque

def hops(graph, start, goal):
    seen = {start}
    q = deque([(start, 0)])
    while q:
        node, dist = q.popleft()
        for nxt in graph.get(node, []):
            if nxt in seen:
                continue
            seen.add(nxt)
            q.append((nxt, dist + 1))
    return -1
''',
        bug_note="Never returns when start equals goal and never checks the neighbor against goal.",
        task_type="algorithm_design",
    ),
    T(
        "topo_order_kahn",
        "graphs",
        """Implement `topo_sort(edges) -> list`.

`edges` is a list of (u, v) pairs meaning u must come before v. Nodes may appear
only as endpoints. Return one valid topological order as a list of nodes, using
Kahn's algorithm and breaking ties by sorting ready nodes lexicographically as
strings. Raise ValueError if the graph has a cycle.""",
        '''
from collections import defaultdict, deque

def topo_sort(edges):
    nodes = set()
    succ = defaultdict(list)
    indeg = defaultdict(int)
    for u, v in edges:
        nodes.add(u)
        nodes.add(v)
        succ[u].append(v)
        indeg[v] += 1
        indeg.setdefault(u, indeg.get(u, 0))
    for n in nodes:
        indeg.setdefault(n, 0)
    ready = deque(sorted([n for n in nodes if indeg[n] == 0], key=str))
    out = []
    while ready:
        n = ready.popleft()
        out.append(n)
        for m in succ[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                ready.append(m)
                ready = deque(sorted(ready, key=str))
        ready = deque(sorted(ready, key=str))
    if len(out) != len(nodes):
        raise ValueError("cycle")
    return out
''',
        '''
import unittest
from solution import topo_sort

class Test(unittest.TestCase):
    def test_chain(self):
        self.assertEqual(topo_sort([("a", "b"), ("b", "c")]), ["a", "b", "c"])
    def test_tie(self):
        self.assertEqual(topo_sort([("a", "c"), ("b", "c")]), ["a", "b", "c"])
    def test_cycle(self):
        with self.assertRaises(ValueError):
            topo_sort([("a", "b"), ("b", "a")])
''',
        bug='''
def topo_sort(edges):
    return [u for u, _ in edges]
''',
        bug_note="Returns only left endpoints, ignores indegree and cycles.",
        task_type="algorithm_design",
    ),
    T(
        "coin_change_count",
        "dynamic_programming",
        """Implement `ways(amount: int, coins: list[int]) -> int`.

Count unordered combinations of `coins` that sum to `amount`. Order of coins
does not matter. Coins may be reused. amount 0 is 1 way (empty combination).
Negative amount is 0.""",
        '''
def ways(amount, coins):
    if amount < 0:
        return 0
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        for x in range(c, amount + 1):
            dp[x] += dp[x - c]
    return dp[amount]
''',
        '''
import unittest
from solution import ways

class Test(unittest.TestCase):
    def test_classic(self):
        self.assertEqual(ways(4, [1, 2]), 3)
    def test_zero(self):
        self.assertEqual(ways(0, [5]), 1)
    def test_impossible(self):
        self.assertEqual(ways(3, [2]), 0)
''',
        bug='''
def ways(amount, coins):
    dp = [0] * (amount + 1)
    dp[0] = 1
    for x in range(1, amount + 1):
        for c in coins:
            if x >= c:
                dp[x] += dp[x - c]
    return dp[amount]
''',
        bug_note="Inner/outer loop swap counts permutations, not combinations.",
        task_type="algorithm_design",
    ),
    T(
        "stable_merge",
        "sorting",
        """Implement `stable_merge(left, right, key) -> list`.

Merge two lists already sorted by `key` into one sorted list. Equal keys must
keep all items from `left` before items from `right` (stable).""",
        '''
def stable_merge(left, right, key):
    i = j = 0
    out = []
    while i < len(left) and j < len(right):
        if key(right[j]) < key(left[i]):
            out.append(right[j])
            j += 1
        else:
            out.append(left[i])
            i += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out
''',
        '''
import unittest
from solution import stable_merge

class Test(unittest.TestCase):
    def test_stable(self):
        left = [("a", 1), ("c", 1)]
        right = [("b", 1)]
        merged = stable_merge(left, right, lambda p: p[1])
        self.assertEqual([p[0] for p in merged], ["a", "c", "b"])
    def test_order(self):
        self.assertEqual(stable_merge([1, 4], [2, 3], lambda x: x), [1, 2, 3, 4])
''',
        bug='''
def stable_merge(left, right, key):
    i = j = 0
    out = []
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            out.append(right[j])
            j += 1
        else:
            out.append(left[i])
            i += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out
''',
        bug_note="Takes from right on ties, breaking stability.",
        task_type="code_generation",
    ),
    T(
        "bst_insert_search",
        "data_structures",
        """Implement a tiny BST: `insert(root, value)` returning the new root, and
`contains(root, value) -> bool`. Nodes are dicts `{"v": int, "l": node|None, "r": node|None}`.
Duplicate inserts are no-ops. `root` may be None.""",
        '''
def insert(root, value):
    if root is None:
        return {"v": value, "l": None, "r": None}
    if value < root["v"]:
        root["l"] = insert(root["l"], value)
    elif value > root["v"]:
        root["r"] = insert(root["r"], value)
    return root

def contains(root, value):
    cur = root
    while cur is not None:
        if value == cur["v"]:
            return True
        cur = cur["l"] if value < cur["v"] else cur["r"]
    return False
''',
        '''
import unittest
from solution import insert, contains

class Test(unittest.TestCase):
    def test_roundtrip(self):
        root = None
        for x in [5, 3, 7, 3]:
            root = insert(root, x)
        self.assertTrue(contains(root, 3))
        self.assertTrue(contains(root, 7))
        self.assertFalse(contains(root, 4))
    def test_empty(self):
        self.assertFalse(contains(None, 1))
''',
        bug='''
def insert(root, value):
    if root is None:
        return {"v": value, "l": None, "r": None}
    root["r"] = insert(root["r"], value)
    return root

def contains(root, value):
    return root is not None and root["v"] == value
''',
        bug_note="Always inserts on the right and only checks the root.",
        task_type="code_generation",
    ),
    T(
        "lru_get_put",
        "data_structures",
        """Implement class `LRUCache(capacity)` with `get(key)` and `put(key, value)`.

Capacity is a positive int. `get` returns the value or None. `put` inserts or
updates; if the cache exceeds capacity, evict the least recently used key.
Both get and put count as use.""",
        '''
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.data = OrderedDict()

    def get(self, key):
        if key not in self.data:
            return None
        self.data.move_to_end(key)
        return self.data[key]

    def put(self, key, value):
        if key in self.data:
            self.data.move_to_end(key)
        self.data[key] = value
        if len(self.data) > self.cap:
            self.data.popitem(last=False)
''',
        '''
import unittest
from solution import LRUCache

class Test(unittest.TestCase):
    def test_evict(self):
        c = LRUCache(2)
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

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.data = OrderedDict()

    def get(self, key):
        return self.data.get(key)

    def put(self, key, value):
        self.data[key] = value
        if len(self.data) > self.cap:
            self.data.popitem(last=True)
''',
        bug_note="get does not refresh recency; evicts most recently inserted.",
        task_type="code_generation",
    ),
    T(
        "count_inversions",
        "algorithms",
        """Implement `inversions(xs: list[int]) -> int`.

Return the number of pairs i < j with xs[i] > xs[j]. Empty or sorted lists are 0.
n will be small enough for O(n^2).""",
        '''
def inversions(xs):
    n = len(xs)
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            if xs[i] > xs[j]:
                count += 1
    return count
''',
        '''
import unittest
from solution import inversions

class Test(unittest.TestCase):
    def test_rev(self):
        self.assertEqual(inversions([3, 2, 1]), 3)
    def test_sorted(self):
        self.assertEqual(inversions([1, 2, 3]), 0)
    def test_empty(self):
        self.assertEqual(inversions([]), 0)
''',
        bug='''
def inversions(xs):
    return sum(1 for a, b in zip(xs, xs[1:]) if a > b)
''',
        bug_note="Only counts adjacent inversions.",
        task_type="algorithm_design",
    ),
    T(
        "edit_distance_one",
        "algorithms",
        """Implement `one_edit(a: str, b: str) -> bool`.

True if a and b are equal, or differ by a single insert, delete, or substitute.
False otherwise.""",
        '''
def one_edit(a, b):
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
    i = j = 0
    skipped = False
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            i += 1
            j += 1
            continue
        if skipped:
            return False
        skipped = True
        j += 1
    return True
''',
        '''
import unittest
from solution import one_edit

class Test(unittest.TestCase):
    def test_sub(self):
        self.assertTrue(one_edit("cat", "cut"))
    def test_ins(self):
        self.assertTrue(one_edit("ca", "cat"))
    def test_two(self):
        self.assertFalse(one_edit("cat", "dog"))
    def test_same(self):
        self.assertTrue(one_edit("ab", "ab"))
''',
        bug='''
def one_edit(a, b):
    return abs(len(a) - len(b)) <= 1
''',
        bug_note="Only checks length, not actual edits.",
        task_type="code_generation",
    ),
    T(
        "cycle_detect",
        "data_structures",
        """Implement `has_cycle(head) -> bool`.

Linked list nodes are `{"v": any, "n": node|None}`. Detect a cycle using
constant extra memory (Floyd).""",
        '''
def has_cycle(head):
    slow = fast = head
    while fast is not None and fast["n"] is not None:
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
        a["n"] = b
        b["n"] = c
        c["n"] = b
        self.assertTrue(has_cycle(a))
    def test_none(self):
        self.assertFalse(has_cycle(None))
    def test_line(self):
        a = {"v": 1, "n": {"v": 2, "n": None}}
        self.assertFalse(has_cycle(a))
''',
        bug='''
def has_cycle(head):
    seen = []
    cur = head
    while cur is not None:
        if cur in seen:
            return True
        seen.append(cur["v"])
        cur = cur["n"]
    return False
''',
        bug_note="Tracks values, not node identity, so duplicate values look like cycles.",
        task_type="debugging",
    ),
    T(
        "prefix_unique",
        "strings",
        """Implement `shortest_unique_prefix(words: list[str]) -> list[str]`.

For each word, return the shortest prefix that uniquely identifies it among
`words`. If a word is a prefix of another, the unique prefix is the whole word.
Assume words are distinct and nonempty.""",
        '''
from collections import defaultdict

def shortest_unique_prefix(words):
    trie = {}
    counts = defaultdict(int)
    for w in words:
        node = trie
        for ch in w:
            node = node.setdefault(ch, {})
            counts[id(node)] += 1
        node["$"] = True
    out = []
    for w in words:
        node = trie
        pref = []
        for ch in w:
            node = node[ch]
            pref.append(ch)
            if counts[id(node)] == 1:
                break
        out.append("".join(pref))
    return out
''',
        '''
import unittest
from solution import shortest_unique_prefix

class Test(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(
            shortest_unique_prefix(["cat", "car", "dog"]),
            ["cat", "car", "d"],
        )
    def test_prefix_word(self):
        self.assertEqual(shortest_unique_prefix(["a", "ab"]), ["a", "ab"])
''',
        bug='''
def shortest_unique_prefix(words):
    return [w[:1] for w in words]
''',
        bug_note="Always returns a one-character prefix.",
        task_type="code_generation",
    ),
    T(
        "interval_merge",
        "algorithms",
        """Implement `merge_intervals(spans) -> list`.

`spans` is a list of [start, end] integer pairs with start <= end (closed).
Return merged disjoint intervals sorted by start.""",
        '''
def merge_intervals(spans):
    if not spans:
        return []
    items = sorted((s, e) for s, e in spans)
    out = [list(items[0])]
    for s, e in items[1:]:
        if s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out
''',
        '''
import unittest
from solution import merge_intervals

class Test(unittest.TestCase):
    def test_overlap(self):
        self.assertEqual(merge_intervals([[1, 3], [2, 6], [8, 10]]), [[1, 6], [8, 10]])
    def test_touch(self):
        self.assertEqual(merge_intervals([[1, 2], [2, 3]]), [[1, 3]])
    def test_empty(self):
        self.assertEqual(merge_intervals([]), [])
''',
        bug='''
def merge_intervals(spans):
    return sorted(spans)
''',
        bug_note="Sorts but never merges overlapping ranges.",
        task_type="code_generation",
    ),
    T(
        "knapsack_01",
        "dynamic_programming",
        """Implement `knapsack(weights, values, cap) -> int`.

0/1 knapsack: each item at most once. Return maximum total value with total
weight <= cap. lengths of weights and values match.""",
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
    def test_classic(self):
        self.assertEqual(knapsack([2, 3, 4], [3, 4, 5], 5), 7)
    def test_none(self):
        self.assertEqual(knapsack([5], [10], 4), 0)
''',
        bug='''
def knapsack(weights, values, cap):
    dp = [0] * (cap + 1)
    for w, v in zip(weights, values):
        for c in range(w, cap + 1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[cap]
''',
        bug_note="Forward loop allows reusing an item (unbounded knapsack).",
        task_type="algorithm_design",
    ),
    T(
        "json_flatten",
        "data_structures",
        """Implement `flatten(obj, prefix="") -> dict`.

Flatten nested dicts into dotted keys. Lists are not flattened: a list value
is stored as-is. Non-dict roots return {prefix or "": obj}.""",
        '''
def flatten(obj, prefix=""):
    if not isinstance(obj, dict):
        return {prefix: obj} if prefix else {"": obj}
    out = {}
    for k, v in obj.items():
        key = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            out.update(flatten(v, key))
        else:
            out[key] = v
    return out
''',
        '''
import unittest
from solution import flatten

class Test(unittest.TestCase):
    def test_nested(self):
        self.assertEqual(flatten({"a": {"b": 1}, "c": 2}), {"a.b": 1, "c": 2})
    def test_list(self):
        self.assertEqual(flatten({"x": [1, 2]}), {"x": [1, 2]})
''',
        bug='''
def flatten(obj, prefix=""):
    return obj if isinstance(obj, dict) else {prefix: obj}
''',
        bug_note="Does not recurse into nested dicts.",
        task_type="code_generation",
    ),
    T(
        "window_max",
        "algorithms",
        """Implement `max_windows(xs, k) -> list`.

For each contiguous window of length k, append the maximum. If k < 1 or
k > len(xs), return [].""",
        '''
from collections import deque

def max_windows(xs, k):
    n = len(xs)
    if k < 1 or k > n:
        return []
    dq = deque()
    out = []
    for i, val in enumerate(xs):
        while dq and dq[0] <= i - k:
            dq.popleft()
        while dq and xs[dq[-1]] <= val:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            out.append(xs[dq[0]])
    return out
''',
        '''
import unittest
from solution import max_windows

class Test(unittest.TestCase):
    def test_k2(self):
        self.assertEqual(max_windows([1, 3, 2, 5, 4], 2), [3, 3, 5, 5])
    def test_bad(self):
        self.assertEqual(max_windows([1, 2], 3), [])
''',
        bug='''
def max_windows(xs, k):
    return [max(xs)] * max(0, len(xs) - k + 1)
''',
        bug_note="Repeats the global max instead of each window max.",
        task_type="code_generation",
    ),
    T(
        "compare_counts",
        "performance_analysis",
        """Implement `nested_body_count(n: int) -> int`.

A loop i from 1..n inclusive, inner j from 1..i inclusive, each inner body
increments a counter once. Return that count. This is a checkable complexity
exercise, not a timing benchmark.""",
        '''
def nested_body_count(n):
    return n * (n + 1) // 2
''',
        '''
import unittest
from solution import nested_body_count

class Test(unittest.TestCase):
    def test_n4(self):
        self.assertEqual(nested_body_count(4), 10)
    def test_n1(self):
        self.assertEqual(nested_body_count(1), 1)
    def test_n0(self):
        self.assertEqual(nested_body_count(0), 0)
''',
        bug='''
def nested_body_count(n):
    return n * n
''',
        bug_note="Uses n^2 instead of triangular number.",
        task_type="performance_analysis",
    ),
    T(
        "refactor_normalize",
        "refactoring",
        """Refactor the inlined logic into `normalize_name(text: str) -> str`.

Trim, collapse internal whitespace to single spaces, and lowercase. Empty
after trim is "". Callers will import normalize_name.""",
        '''
def normalize_name(text):
    return " ".join(text.split()).lower()
''',
        '''
import unittest
from solution import normalize_name

class Test(unittest.TestCase):
    def test_spaces(self):
        self.assertEqual(normalize_name("  Ada   Lovelace "), "ada lovelace")
    def test_empty(self):
        self.assertEqual(normalize_name("   "), "")
''',
        bug='''
def normalize_name(text):
    return text.strip().lower()
''',
        bug_note="Does not collapse internal whitespace.",
        task_type="refactoring",
    ),
    T(
        "complete_binary_search",
        "code_completion",
        """Complete `bisect_left(xs, target) -> int` for a sorted list `xs`.

Return the insertion index of `target` (first position where all earlier
elements are strictly less). Empty list returns 0.""",
        '''
def bisect_left(xs, target):
    lo, hi = 0, len(xs)
    while lo < hi:
        mid = (lo + hi) // 2
        if xs[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
''',
        '''
import unittest
from solution import bisect_left

class Test(unittest.TestCase):
    def test_dup(self):
        self.assertEqual(bisect_left([1, 2, 2, 3], 2), 1)
    def test_end(self):
        self.assertEqual(bisect_left([1, 2], 5), 2)
    def test_empty(self):
        self.assertEqual(bisect_left([], 1), 0)
''',
        bug='''
def bisect_left(xs, target):
    try:
        return xs.index(target)
    except ValueError:
        return len(xs)
''',
        bug_note="index finds an occurrence, not the leftmost insertion point for missing values in the middle.",
        task_type="code_completion",
    ),
    T(
        "generate_tests_fizz",
        "test_generation",
        """Implement `fizzbuzz(n) -> list[str]` AND keep the unittest class so that
n=1..15 is fully specified: multiples of 15 are 'FizzBuzz', of 3 'Fizz', of 5
'Buzz', else the decimal string.""",
        '''
def fizzbuzz(n):
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            out.append("FizzBuzz")
        elif i % 3 == 0:
            out.append("Fizz")
        elif i % 5 == 0:
            out.append("Buzz")
        else:
            out.append(str(i))
    return out
''',
        '''
import unittest
from solution import fizzbuzz

class Test(unittest.TestCase):
    def test_15(self):
        got = fizzbuzz(15)
        self.assertEqual(got[2], "Fizz")
        self.assertEqual(got[4], "Buzz")
        self.assertEqual(got[14], "FizzBuzz")
        self.assertEqual(got[0], "1")
    def test_len(self):
        self.assertEqual(len(fizzbuzz(0)), 0)
''',
        bug='''
def fizzbuzz(n):
    return [str(i) for i in range(1, n + 1)]
''',
        bug_note="Never applies Fizz/Buzz rules.",
        task_type="test_generation",
    ),
    T(
        "diagnose_off_by_one_slice",
        "debugging",
        """The intended spec: `first_n(xs, n)` returns the first n items, or all of
xs if n >= len(xs). n < 0 raises ValueError. Fix the buggy body.""",
        '''
def first_n(xs, n):
    if n < 0:
        raise ValueError("n")
    return xs[:n]
''',
        '''
import unittest
from solution import first_n

class Test(unittest.TestCase):
    def test_short(self):
        self.assertEqual(first_n([1, 2, 3], 2), [1, 2])
    def test_over(self):
        self.assertEqual(first_n([1], 5), [1])
    def test_neg(self):
        with self.assertRaises(ValueError):
            first_n([1], -1)
''',
        bug='''
def first_n(xs, n):
    return xs[: n - 1]
''',
        bug_note="Uses n-1 as the slice end and ignores negative n.",
        task_type="debugging",
    ),
    T(
        "union_find_count",
        "data_structures",
        """Implement `components(n, edges) -> int`.

Nodes are 0..n-1. `edges` is a list of undirected pairs. Return the number of
connected components (isolated nodes count).""",
        '''
def components(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for a, b in edges:
        union(a, b)
    return len({find(i) for i in range(n)})
''',
        '''
import unittest
from solution import components

class Test(unittest.TestCase):
    def test_two(self):
        self.assertEqual(components(4, [(0, 1), (1, 0), (2, 3)]), 2)
    def test_isolated(self):
        self.assertEqual(components(3, []), 3)
''',
        bug='''
def components(n, edges):
    return n - len(edges)
''',
        bug_note="Treats every edge as merging two unique components.",
        task_type="algorithm_design",
    ),
    T(
        "heap_kth",
        "algorithms",
        """Implement `kth_smallest(xs, k) -> int`.

1-based k. Return the k-th smallest element of xs (distinctness not required).
Raise IndexError if k is out of range. You may sort.""",
        '''
def kth_smallest(xs, k):
    if k < 1 or k > len(xs):
        raise IndexError("k")
    return sorted(xs)[k - 1]
''',
        '''
import unittest
from solution import kth_smallest

class Test(unittest.TestCase):
    def test_k(self):
        self.assertEqual(kth_smallest([7, 1, 5, 3], 2), 3)
    def test_bad(self):
        with self.assertRaises(IndexError):
            kth_smallest([1], 2)
''',
        bug='''
def kth_smallest(xs, k):
    return xs[k]
''',
        bug_note="Uses unsorted 0-based indexing.",
        task_type="code_generation",
    ),
    T(
        "sha_length_independent",
        "hashing",
        """Implement `bucket(key: str, n: int) -> int`.

Return a bucket in 0..n-1 using Python's stable hash of the UTF-8 bytes via
hashlib.md5 (first 8 hex digits as int) so tests are deterministic across
processes. n > 0.""",
        '''
import hashlib

def bucket(key, n):
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % n
''',
        '''
import unittest
from solution import bucket

class Test(unittest.TestCase):
    def test_range(self):
        b = bucket("alpha", 10)
        self.assertGreaterEqual(b, 0)
        self.assertLess(b, 10)
    def test_stable(self):
        self.assertEqual(bucket("alpha", 10), bucket("alpha", 10))
    def test_known(self):
        import hashlib
        expected = int(hashlib.md5(b"alpha").hexdigest()[:8], 16) % 10
        self.assertEqual(bucket("alpha", 10), expected)
''',
        bug='''
def bucket(key, n):
    return len(key) % n
''',
        bug_note="Uses string length, so different keys collide by design.",
        task_type="code_generation",
    ),
    T(
        "iterator_tee_safe",
        "iterators",
        """Implement `second_pass(xs) -> tuple`.

Consume an iterable twice: return (list first pass, list second pass) with
equal contents even if `xs` is a one-shot iterator. Do not mutate a list
input in place.""",
        '''
def second_pass(xs):
    data = list(xs)
    return data, list(data)
''',
        '''
import unittest
from solution import second_pass

class Test(unittest.TestCase):
    def test_gen(self):
        a, b = second_pass(i for i in range(3))
        self.assertEqual(a, [0, 1, 2])
        self.assertEqual(b, [0, 1, 2])
    def test_list(self):
        src = [1, 2]
        a, b = second_pass(src)
        self.assertEqual(a, [1, 2])
        self.assertEqual(src, [1, 2])
''',
        bug='''
def second_pass(xs):
    return list(xs), list(xs)
''',
        bug_note="Second list(xs) on a generator is empty.",
        task_type="debugging",
    ),
    T(
        "context_tempfile_count",
        "file_io",
        """Implement `line_count(text: str) -> int` by writing `text` to a temp file
with UTF-8, reading it back, and counting splitlines(). Empty text is 0 lines
if it has no newline and no characters; a single newline is 1 empty line
(`splitlines` behaviour).""",
        '''
import tempfile
from pathlib import Path

def line_count(text):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as fh:
        fh.write(text)
        path = fh.name
    try:
        data = Path(path).read_text(encoding="utf-8")
        if data == "":
            return 0
        return len(data.splitlines())
    finally:
        Path(path).unlink(missing_ok=True)
''',
        '''
import unittest
from solution import line_count

class Test(unittest.TestCase):
    def test_two(self):
        self.assertEqual(line_count("a\\nb"), 2)
    def test_empty(self):
        self.assertEqual(line_count(""), 0)
''',
        bug='''
def line_count(text):
    return text.count("\\n")
''',
        bug_note="Counts newline characters, so 'a' is 0 instead of 1.",
        task_type="code_generation",
    ),
    T(
        "decorator_once",
        "functions",
        """Implement `once(fn)` returning a wrapper that calls `fn` at most once and
reuses the first return value. The wrapper must have a `.called` bool.""",
        '''
def once(fn):
    state = {"value": None, "done": False}

    def wrapper(*args, **kwargs):
        if not state["done"]:
            state["value"] = fn(*args, **kwargs)
            state["done"] = True
            wrapper.called = True
        return state["value"]

    wrapper.called = False
    return wrapper
''',
        '''
import unittest
from solution import once

class Test(unittest.TestCase):
    def test_once(self):
        n = {"c": 0}
        def f():
            n["c"] += 1
            return n["c"]
        g = once(f)
        self.assertFalse(g.called)
        self.assertEqual(g(), 1)
        self.assertEqual(g(), 1)
        self.assertTrue(g.called)
        self.assertEqual(n["c"], 1)
''',
        bug='''
def once(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    wrapper.called = False
    return wrapper
''',
        bug_note="Calls fn every time and never sets called.",
        task_type="code_generation",
    ),
    T(
        "matrix_multiply",
        "linear_algebra",
        """Implement `matmul(a, b)` for dense lists of lists of ints.

a is m×n, b is n×p. Return m×p. Raise ValueError on shape mismatch or empty
outer list.""",
        '''
def matmul(a, b):
    if not a or not b:
        raise ValueError("empty")
    n = len(a[0])
    if any(len(row) != n for row in a):
        raise ValueError("ragged a")
    p = len(b[0])
    if any(len(row) != p for row in b):
        raise ValueError("ragged b")
    if len(b) != n:
        raise ValueError("shape")
    out = []
    for i in range(len(a)):
        row = []
        for j in range(p):
            s = 0
            for k in range(n):
                s += a[i][k] * b[k][j]
            row.append(s)
        out.append(row)
    return out
''',
        '''
import unittest
from solution import matmul

class Test(unittest.TestCase):
    def test_2x2(self):
        self.assertEqual(matmul([[1, 2], [3, 4]], [[5, 6], [7, 8]]), [[19, 22], [43, 50]])
    def test_shape(self):
        with self.assertRaises(ValueError):
            matmul([[1, 2]], [[1], [2], [3]])
''',
        bug='''
def matmul(a, b):
    return a
''',
        bug_note="Returns the left matrix unchanged.",
        task_type="code_generation",
    ),
    T(
        "regex_emails",
        "strings",
        """Implement `local_parts(text: str) -> list[str]`.

Find emails of the form local@domain where local and domain are nonempty
runs of [A-Za-z0-9._-], domain contains at least one dot, and return unique
local parts in first-seen order.""",
        '''
import re

def local_parts(text):
    pat = re.compile(r"\\b([A-Za-z0-9._-]+)@([A-Za-z0-9._-]+\\.[A-Za-z0-9._-]+)\\b")
    seen = []
    found = set()
    for local, _dom in pat.findall(text):
        if local not in found:
            found.add(local)
            seen.append(local)
    return seen
''',
        '''
import unittest
from solution import local_parts

class Test(unittest.TestCase):
    def test_two(self):
        self.assertEqual(
            local_parts("mail ada@ex.org then ada@ex.org and bob@site.co.uk"),
            ["ada", "bob"],
        )
    def test_none(self):
        self.assertEqual(local_parts("no mail here"), [])
''',
        bug='''
def local_parts(text):
    return [p for p in text.split() if "@" in p]
''',
        bug_note="Returns whole tokens including the domain.",
        task_type="code_generation",
    ),
    T(
        "bit_popcount_parity",
        "algorithms",
        """Implement `odd_parity(n: int) -> bool`.

True if the binary representation of nonnegative n has an odd number of 1 bits.
n is a nonnegative int.""",
        '''
def odd_parity(n):
    if n < 0:
        raise ValueError("n")
    ones = 0
    while n:
        ones ^= n & 1
        n >>= 1
    return bool(ones)
''',
        '''
import unittest
from solution import odd_parity

class Test(unittest.TestCase):
    def test_five(self):
        self.assertTrue(odd_parity(5))
    def test_three(self):
        self.assertFalse(odd_parity(3))
    def test_zero(self):
        self.assertFalse(odd_parity(0))
''',
        bug='''
def odd_parity(n):
    return n % 2 == 1
''',
        bug_note="Confuses value parity with popcount parity (3 is odd but even popcount).",
        task_type="code_generation",
    ),
    T(
        "sqlish_select",
        "data_structures",
        """Implement `select(rows, pred, cols) -> list`.

`rows` is a list of dicts. `pred(row)` is a callable. `cols` is a list of keys.
Return dicts with only those keys, in input order, for rows where pred is true.""",
        '''
def select(rows, pred, cols):
    out = []
    for row in rows:
        if pred(row):
            out.append({c: row[c] for c in cols})
    return out
''',
        '''
import unittest
from solution import select

class Test(unittest.TestCase):
    def test_filter(self):
        rows = [{"n": "a", "v": 1}, {"n": "b", "v": 2}]
        got = select(rows, lambda r: r["v"] > 1, ["n"])
        self.assertEqual(got, [{"n": "b"}])
    def test_none(self):
        self.assertEqual(select([], lambda r: True, ["n"]), [])
''',
        bug='''
def select(rows, pred, cols):
    return rows
''',
        bug_note="Ignores predicate and column projection.",
        task_type="code_generation",
    ),
    T(
        "rate_limit_tokens",
        "systems",
        """Implement class `TokenBucket(rate, burst)` with `allow(now_s, cost=1) -> bool`.

`rate` tokens per second, `burst` max tokens. Start full. `now_s` is a
nondecreasing float clock. Fractional tokens are allowed. Deny if cost exceeds
available after refill.""",
        '''
class TokenBucket:
    def __init__(self, rate, burst):
        self.rate = rate
        self.burst = burst
        self.tokens = float(burst)
        self.t = None

    def allow(self, now_s, cost=1):
        if self.t is None:
            self.t = now_s
        else:
            dt = now_s - self.t
            self.tokens = min(self.burst, self.tokens + dt * self.rate)
            self.t = now_s
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False
''',
        '''
import unittest
from solution import TokenBucket

class Test(unittest.TestCase):
    def test_burst(self):
        b = TokenBucket(1, 2)
        self.assertTrue(b.allow(0))
        self.assertTrue(b.allow(0))
        self.assertFalse(b.allow(0))
        self.assertTrue(b.allow(1.0))
''',
        bug='''
class TokenBucket:
    def __init__(self, rate, burst):
        self.burst = burst
        self.n = 0

    def allow(self, now_s, cost=1):
        self.n += cost
        return self.n <= self.burst
''',
        bug_note="Never refills; only counts total allows against burst.",
        task_type="code_generation",
    ),
]


def v101_python_tasks() -> list[PyTask]:
    return list(V101_PYTHON_TASKS)
