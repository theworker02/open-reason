"""Original Python tasks for the 1.4.0 coding split (sandbox-tested)."""

from __future__ import annotations

from open_reason.generation.coding_python import T, PyTask


def v140_python_tasks() -> list[PyTask]:
    return [
        T(
            "v140-hamming",
            "strings",
            """Implement `hamming(a: str, b: str) -> int`.

Equal-length strings. Count positions where characters differ. Raise
ValueError if lengths differ.""",
            '''
def hamming(a, b):
    if len(a) != len(b):
        raise ValueError("length")
    return sum(x != y for x, y in zip(a, b))
''',
            '''
import unittest
from solution import hamming

class Test(unittest.TestCase):
    def test_dist(self):
        self.assertEqual(hamming("karolin", "kathrin"), 3)
    def test_bad(self):
        with self.assertRaises(ValueError):
            hamming("ab", "a")
''',
        ),
        T(
            "v140-flatten-one",
            "lists",
            """Implement `flatten_one(xs: list) -> list`.

Flatten one level: nested lists are concatenated; non-lists stay as elements.""",
            '''
def flatten_one(xs):
    out = []
    for item in xs:
        if isinstance(item, list):
            out.extend(item)
        else:
            out.append(item)
    return out
''',
            '''
import unittest
from solution import flatten_one

class Test(unittest.TestCase):
    def test_mix(self):
        self.assertEqual(flatten_one([1, [2, 3], 4]), [1, 2, 3, 4])
    def test_no_deep(self):
        self.assertEqual(flatten_one([[1, [2]]]), [1, [2]])
''',
        ),
        T(
            "v140-lcp",
            "strings",
            """Implement `lcp(words: list[str]) -> str` longest common prefix.
Empty list → empty string.""",
            '''
def lcp(words):
    if not words:
        return ""
    prefix = words[0]
    for w in words[1:]:
        while not w.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix
''',
            '''
import unittest
from solution import lcp

class Test(unittest.TestCase):
    def test_common(self):
        self.assertEqual(lcp(["flower", "flow", "flight"]), "fl")
    def test_none(self):
        self.assertEqual(lcp(["a", "b"]), "")
    def test_empty(self):
        self.assertEqual(lcp([]), "")
''',
        ),
        T(
            "v140-merge-sorted",
            "arrays",
            """Implement `merge_sorted(a: list[int], b: list[int]) -> list[int]`
merging two already-sorted non-decreasing lists.""",
            '''
def merge_sorted(a, b):
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out
''',
            '''
import unittest
from solution import merge_sorted

class Test(unittest.TestCase):
    def test_merge(self):
        self.assertEqual(merge_sorted([1, 3], [2, 4]), [1, 2, 3, 4])
    def test_empty(self):
        self.assertEqual(merge_sorted([], [1]), [1])
''',
        ),
        T(
            "v140-binsearch",
            "arrays",
            """Implement `bsearch(xs: list[int], target: int) -> int`.

`xs` is sorted ascending. Return the leftmost index of target, or -1.""",
            '''
def bsearch(xs, target):
    lo, hi = 0, len(xs)
    found = -1
    while lo < hi:
        mid = (lo + hi) // 2
        if xs[mid] < target:
            lo = mid + 1
        elif xs[mid] > target:
            hi = mid
        else:
            found = mid
            hi = mid
    return found
''',
            '''
import unittest
from solution import bsearch

class Test(unittest.TestCase):
    def test_left(self):
        self.assertEqual(bsearch([1, 2, 2, 2, 5], 2), 1)
    def test_miss(self):
        self.assertEqual(bsearch([1, 3, 5], 4), -1)
''',
        ),
        T(
            "v140-snake",
            "strings",
            """Implement `to_snake(name: str) -> str`: split on spaces and `-`,
lowercase, join with `_`, drop empty pieces.""",
            '''
def to_snake(name):
    bits = [p for part in name.split() for p in part.split("-") if p]
    return "_".join(b.lower() for b in bits)
''',
            '''
import unittest
from solution import to_snake

class Test(unittest.TestCase):
    def test_mix(self):
        self.assertEqual(to_snake("Hello-World x"), "hello_world_x")
''',
        ),
        T(
            "v140-caesar",
            "crypto",
            """Implement `caesar(text: str, shift: int) -> str`.

Shift only A-Z/a-z by shift mod 26. Preserve case. Other characters unchanged.""",
            '''
def caesar(text, shift):
    shift %= 26
    out = []
    for ch in text:
        if "A" <= ch <= "Z":
            out.append(chr((ord(ch) - 65 + shift) % 26 + 65))
        elif "a" <= ch <= "z":
            out.append(chr((ord(ch) - 97 + shift) % 26 + 97))
        else:
            out.append(ch)
    return "".join(out)
''',
            '''
import unittest
from solution import caesar

class Test(unittest.TestCase):
    def test_wrap(self):
        self.assertEqual(caesar("xyz", 3), "abc")
    def test_keep(self):
        self.assertEqual(caesar("A-b", 1), "B-c")
''',
        ),
        T(
            "v140-transpose",
            "matrices",
            """Implement `transpose(m: list[list[int]]) -> list[list[int]]`.
Rectangular matrix. Empty → empty.""",
            '''
def transpose(m):
    if not m:
        return []
    return [list(row) for row in zip(*m)]
''',
            '''
import unittest
from solution import transpose

class Test(unittest.TestCase):
    def test_t(self):
        self.assertEqual(transpose([[1, 2, 3], [4, 5, 6]]), [[1, 4], [2, 5], [3, 6]])
    def test_empty(self):
        self.assertEqual(transpose([]), [])
''',
        ),
        T(
            "v140-islands",
            "graphs",
            """Implement `count_islands(grid: list[list[int]]) -> int`.

grid is 0/1. 4-connected 1's form an island. Mutating a copy is allowed.""",
            '''
def count_islands(grid):
    if not grid:
        return 0
    g = [row[:] for row in grid]
    h, w = len(g), len(g[0])

    def dfs(i, j):
        if i < 0 or j < 0 or i >= h or j >= w or g[i][j] != 1:
            return
        g[i][j] = 0
        dfs(i + 1, j)
        dfs(i - 1, j)
        dfs(i, j + 1)
        dfs(i, j - 1)

    n = 0
    for i in range(h):
        for j in range(w):
            if g[i][j] == 1:
                n += 1
                dfs(i, j)
    return n
''',
            '''
import unittest
from solution import count_islands

class Test(unittest.TestCase):
    def test_two(self):
        g = [[1, 1, 0], [0, 0, 1]]
        self.assertEqual(count_islands(g), 2)
    def test_none(self):
        self.assertEqual(count_islands([[0, 0]]), 0)
''',
        ),
        T(
            "v140-two-sum",
            "arrays",
            """Implement `two_sum(xs: list[int], target: int) -> tuple[int, int] | None`.

Return the smallest (i, j) with i < j and xs[i]+xs[j]==target, or None.""",
            '''
def two_sum(xs, target):
    seen = {}
    best = None
    for i, x in enumerate(xs):
        need = target - x
        if need in seen:
            pair = (seen[need], i)
            if best is None or pair < best:
                best = pair
        if x not in seen:
            seen[x] = i
    return best
''',
            '''
import unittest
from solution import two_sum

class Test(unittest.TestCase):
    def test_pair(self):
        self.assertEqual(two_sum([2, 7, 11, 15], 9), (0, 1))
    def test_none(self):
        self.assertIsNone(two_sum([1, 2], 8))
''',
        ),
        T(
            "v140-palindrome",
            "strings",
            """Implement `is_palindrome(text: str) -> bool`.

Ignore case and characters that are not alphanumeric.""",
            '''
def is_palindrome(text):
    chars = [c.lower() for c in text if c.isalnum()]
    return chars == chars[::-1]
''',
            '''
import unittest
from solution import is_palindrome

class Test(unittest.TestCase):
    def test_yes(self):
        self.assertTrue(is_palindrome("A man, a plan, a canal: Panama"))
    def test_no(self):
        self.assertFalse(is_palindrome("hello"))
''',
        ),
        T(
            "v140-sieve",
            "number-theory",
            """Implement `primes_upto(n: int) -> list[int]` primes in 2..n inclusive.
n < 2 → [].""",
            '''
def primes_upto(n):
    if n < 2:
        return []
    s = [True] * (n + 1)
    s[0] = s[1] = False
    p = 2
    while p * p <= n:
        if s[p]:
            for k in range(p * p, n + 1, p):
                s[k] = False
        p += 1
    return [i for i, ok in enumerate(s) if ok]
''',
            '''
import unittest
from solution import primes_upto

class Test(unittest.TestCase):
    def test_10(self):
        self.assertEqual(primes_upto(10), [2, 3, 5, 7])
    def test_small(self):
        self.assertEqual(primes_upto(1), [])
''',
        ),
        T(
            "v140-window-max",
            "arrays",
            """Implement `window_max(xs: list[int], k: int) -> list[int]`.

Max of each contiguous window of length k. k>=1. Empty if k > len(xs).""",
            '''
from collections import deque

def window_max(xs, k):
    if k <= 0:
        raise ValueError("k")
    n = len(xs)
    if k > n:
        return []
    q = deque()
    out = []
    for i, x in enumerate(xs):
        while q and q[0] <= i - k:
            q.popleft()
        while q and xs[q[-1]] <= x:
            q.pop()
        q.append(i)
        if i >= k - 1:
            out.append(xs[q[0]])
    return out
''',
            '''
import unittest
from solution import window_max

class Test(unittest.TestCase):
    def test_win(self):
        self.assertEqual(window_max([1, 3, 2, 5, 4], 3), [3, 5, 5])
    def test_too_big(self):
        self.assertEqual(window_max([1], 2), [])
''',
        ),
        T(
            "v140-overlap",
            "intervals",
            """Implement `overlaps(a: tuple[int, int], b: tuple[int, int]) -> bool`
for half-open intervals [start, end). Empty intervals (start>=end) overlap nothing.""",
            '''
def overlaps(a, b):
    a0, a1 = a
    b0, b1 = b
    if a0 >= a1 or b0 >= b1:
        return False
    return a0 < b1 and b0 < a1
''',
            '''
import unittest
from solution import overlaps

class Test(unittest.TestCase):
    def test_yes(self):
        self.assertTrue(overlaps((0, 3), (2, 5)))
    def test_touch(self):
        self.assertFalse(overlaps((0, 2), (2, 4)))
    def test_empty(self):
        self.assertFalse(overlaps((3, 3), (0, 10)))
''',
        ),
        T(
            "v140-min-stack",
            "datastructures",
            """Implement class `MinStack` with push(x), pop() -> int, min() -> int
in O(1) amortized. pop/min on empty raise IndexError.""",
            '''
class MinStack:
    def __init__(self):
        self._data = []
        self._mins = []

    def push(self, x):
        self._data.append(x)
        self._mins.append(x if not self._mins else min(x, self._mins[-1]))

    def pop(self):
        if not self._data:
            raise IndexError("empty")
        self._mins.pop()
        return self._data.pop()

    def min(self):
        if not self._mins:
            raise IndexError("empty")
        return self._mins[-1]
''',
            '''
import unittest
from solution import MinStack

class Test(unittest.TestCase):
    def test_min(self):
        s = MinStack()
        s.push(3)
        s.push(1)
        s.push(2)
        self.assertEqual(s.min(), 1)
        self.assertEqual(s.pop(), 2)
        self.assertEqual(s.min(), 1)
''',
        ),
        T(
            "v140-group-runs",
            "strings",
            """Implement `group_runs(text: str) -> list[tuple[str, int]]` of consecutive
character runs. "" → [].""",
            '''
def group_runs(text):
    if not text:
        return []
    out = []
    prev = text[0]
    n = 1
    for ch in text[1:]:
        if ch == prev:
            n += 1
        else:
            out.append((prev, n))
            prev, n = ch, 1
    out.append((prev, n))
    return out
''',
            '''
import unittest
from solution import group_runs

class Test(unittest.TestCase):
    def test_runs(self):
        self.assertEqual(group_runs("aaabbc"), [("a", 3), ("b", 2), ("c", 1)])
    def test_empty(self):
        self.assertEqual(group_runs(""), [])
''',
        ),
        T(
            "v140-ipv4",
            "parsing",
            """Implement `ipv4_ok(text: str) -> bool`.

Exactly four decimal octets 0-255, no leading zeros except the value 0 itself
(so "01" is invalid). No spaces.""",
            '''
def ipv4_ok(text):
    parts = text.split(".")
    if len(parts) != 4:
        return False
    for p in parts:
        if not p.isdigit():
            return False
        if len(p) > 1 and p[0] == "0":
            return False
        n = int(p)
        if n < 0 or n > 255:
            return False
    return True
''',
            '''
import unittest
from solution import ipv4_ok

class Test(unittest.TestCase):
    def test_ok(self):
        self.assertTrue(ipv4_ok("192.168.0.1"))
    def test_lead(self):
        self.assertFalse(ipv4_ok("192.168.00.1"))
    def test_range(self):
        self.assertFalse(ipv4_ok("256.0.0.1"))
''',
        ),
        T(
            "v140-kth-smallest",
            "arrays",
            """Implement `kth_smallest(xs: list[int], k: int) -> int`.

1-based k. Raise ValueError if k is out of range. Order statistics of a copy
is fine (sorting allowed).""",
            '''
def kth_smallest(xs, k):
    if k < 1 or k > len(xs):
        raise ValueError("k")
    return sorted(xs)[k - 1]
''',
            '''
import unittest
from solution import kth_smallest

class Test(unittest.TestCase):
    def test_k(self):
        self.assertEqual(kth_smallest([5, 1, 4, 2], 2), 2)
    def test_bad(self):
        with self.assertRaises(ValueError):
            kth_smallest([1], 2)
''',
        ),
    ]
