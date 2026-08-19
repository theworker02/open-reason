"""Additional original Python tasks for the 1.3.8 train-sized coding split."""

from __future__ import annotations

from open_reason.generation.coding_python import T, PyTask


def v102_python_tasks() -> list[PyTask]:
    return [
        T(
            "v102-run-length",
            "strings",
            """Implement `rle(text: str) -> str` run-length encoding: groups of
repeated characters become `{char}{count}` with count always written, even if 1.
Empty string → empty string.""",
            '''
def rle(text):
    if not text:
        return ""
    out = []
    prev = text[0]
    n = 1
    for ch in text[1:]:
        if ch == prev:
            n += 1
        else:
            out.append(f"{prev}{n}")
            prev, n = ch, 1
    out.append(f"{prev}{n}")
    return "".join(out)
''',
            '''
import unittest
from solution import rle

class Test(unittest.TestCase):
    def test_runs(self):
        self.assertEqual(rle("aaabbc"), "a3b2c1")
    def test_empty(self):
        self.assertEqual(rle(""), "")
''',
        ),
        T(
            "v102-balanced-same",
            "strings",
            """Implement `same_multiset(a: str, b: str) -> bool`: True iff a and b
contain the same characters with the same frequencies (anagrams).""",
            '''
from collections import Counter

def same_multiset(a, b):
    return Counter(a) == Counter(b)
''',
            '''
import unittest
from solution import same_multiset

class Test(unittest.TestCase):
    def test_yes(self):
        self.assertTrue(same_multiset("abba", "baba"))
    def test_no(self):
        self.assertFalse(same_multiset("ab", "a"))
''',
        ),
        T(
            "v102-moving-avg",
            "arrays",
            """Implement `moving_avg(xs: list[float], k: int) -> list[float]`.
Return simple moving averages of window k (k>=1). Output length is
len(xs)-k+1, or [] if k > len(xs).""",
            '''
def moving_avg(xs, k):
    if k <= 0:
        raise ValueError("k")
    if k > len(xs):
        return []
    out = []
    s = sum(xs[:k])
    out.append(s / k)
    for i in range(k, len(xs)):
        s += xs[i] - xs[i - k]
        out.append(s / k)
    return out
''',
            '''
import unittest
from solution import moving_avg

class Test(unittest.TestCase):
    def test_win(self):
        self.assertEqual(moving_avg([1, 2, 3, 4], 2), [1.5, 2.5, 3.5])
    def test_too_big(self):
        self.assertEqual(moving_avg([1], 3), [])
''',
        ),
        T(
            "v102-clamp",
            "math",
            """Implement `clamp(x: int, lo: int, hi: int) -> int` with lo <= hi.""",
            '''
def clamp(x, lo, hi):
    if lo > hi:
        raise ValueError("range")
    return max(lo, min(hi, x))
''',
            '''
import unittest
from solution import clamp

class Test(unittest.TestCase):
    def test_mid(self):
        self.assertEqual(clamp(5, 0, 10), 5)
    def test_lo(self):
        self.assertEqual(clamp(-1, 0, 10), 0)
    def test_hi(self):
        self.assertEqual(clamp(99, 0, 10), 10)
''',
        ),
        T(
            "v102-rotate",
            "arrays",
            """Implement `rotate_left(xs: list, k: int) -> list` rotating a copy
left by k positions (k may be larger than len(xs); empty list stays empty).""",
            '''
def rotate_left(xs, k):
    n = len(xs)
    if n == 0:
        return []
    k = k % n
    return xs[k:] + xs[:k]
''',
            '''
import unittest
from solution import rotate_left

class Test(unittest.TestCase):
    def test_rot(self):
        self.assertEqual(rotate_left([1, 2, 3, 4], 1), [2, 3, 4, 1])
    def test_k_big(self):
        self.assertEqual(rotate_left([1, 2], 3), [2, 1])
    def test_empty(self):
        self.assertEqual(rotate_left([], 4), [])
''',
        ),
        T(
            "v102-depth-parens",
            "strings",
            """Implement `max_paren_depth(text: str) -> int` for `()` only.
Ignore other characters. Return -1 if the string is unbalanced.""",
            '''
def max_paren_depth(text):
    depth = 0
    best = 0
    for ch in text:
        if ch == "(":
            depth += 1
            best = max(best, depth)
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return -1
    return best if depth == 0 else -1
''',
            '''
import unittest
from solution import max_paren_depth

class Test(unittest.TestCase):
    def test_nested(self):
        self.assertEqual(max_paren_depth("(a(b))"), 2)
    def test_bad(self):
        self.assertEqual(max_paren_depth(")("), -1)
    def test_open(self):
        self.assertEqual(max_paren_depth("("), -1)
''',
        ),
        T(
            "v102-mode",
            "stats",
            """Implement `mode_int(xs: list[int]) -> int` returning the unique
smallest mode if several values share the top frequency.""",
            '''
from collections import Counter

def mode_int(xs):
    if not xs:
        raise ValueError("empty")
    counts = Counter(xs)
    best = max(counts.values())
    return min(v for v, c in counts.items() if c == best)
''',
            '''
import unittest
from solution import mode_int

class Test(unittest.TestCase):
    def test_mode(self):
        self.assertEqual(mode_int([1, 2, 2, 3]), 2)
    def test_tie(self):
        self.assertEqual(mode_int([1, 1, 2, 2]), 1)
''',
        ),
        T(
            "v102-prefix-sums",
            "arrays",
            """Implement `prefix_sums(xs: list[int]) -> list[int]` where
out[i] = xs[0]+...+xs[i].""",
            '''
def prefix_sums(xs):
    out = []
    s = 0
    for x in xs:
        s += x
        out.append(s)
    return out
''',
            '''
import unittest
from solution import prefix_sums

class Test(unittest.TestCase):
    def test_ps(self):
        self.assertEqual(prefix_sums([1, 2, 3]), [1, 3, 6])
    def test_empty(self):
        self.assertEqual(prefix_sums([]), [])
''',
        ),
        T(
            "v102-kebab",
            "strings",
            """Implement `to_kebab(name: str) -> str`: split on spaces and `_`,
lowercase, join with `-`, drop empty pieces.""",
            '''
def to_kebab(name):
    bits = [p for part in name.split() for p in part.split("_") if p]
    return "-".join(b.lower() for b in bits)
''',
            '''
import unittest
from solution import to_kebab

class Test(unittest.TestCase):
    def test_mix(self):
        self.assertEqual(to_kebab("Hello_World x"), "hello-world-x")
''',
        ),
        T(
            "v102-set-cover-greedy",
            "algorithms",
            """Implement `greedy_cover(universe: set[int], sets: list[set[int]]) -> list[int]`.

Return indices of sets chosen by greedy set cover (pick the set covering the
most remaining elements; ties → lowest index). Stop when universe is covered
or no set adds coverage.""",
            '''
def greedy_cover(universe, sets):
    remaining = set(universe)
    chosen = []
    used = set()
    while remaining:
        best_i = None
        best_gain = 0
        for i, s in enumerate(sets):
            if i in used:
                continue
            gain = len(remaining & s)
            if gain > best_gain or (gain == best_gain and best_i is not None and i < best_i and gain > 0):
                if gain > best_gain or (gain == best_gain and i < best_i):
                    best_gain = gain
                    best_i = i
            elif best_i is None and gain > 0:
                best_gain = gain
                best_i = i
        if best_i is None or best_gain == 0:
            break
        used.add(best_i)
        chosen.append(best_i)
        remaining -= sets[best_i]
    return chosen
''',
            '''
import unittest
from solution import greedy_cover

class Test(unittest.TestCase):
    def test_simple(self):
        u = {1, 2, 3}
        sets = [{1, 2}, {2, 3}, {3}]
        got = greedy_cover(u, sets)
        self.assertTrue(set().union(*(sets[i] for i in got)) >= u)
''',
        ),
        T(
            "v102-isbn-digit",
            "checksums",
            """Implement `isbn10_ok(code: str) -> bool`. `code` is 10 characters,
last may be X (value 10). Weighted sum d1*10+...+d10*1 must be 0 mod 11.
Ignore hyphens.""",
            '''
def isbn10_ok(code):
    compact = code.replace("-", "")
    if len(compact) != 10:
        return False
    total = 0
    for i, ch in enumerate(compact):
        if i < 9:
            if not ch.isdigit():
                return False
            total += int(ch) * (10 - i)
        else:
            if ch in "Xx":
                total += 10
            elif ch.isdigit():
                total += int(ch)
            else:
                return False
    return total % 11 == 0
''',
            '''
import unittest
from solution import isbn10_ok

class Test(unittest.TestCase):
    def test_known(self):
        self.assertTrue(isbn10_ok("0-306-40615-2"))
    def test_bad(self):
        self.assertFalse(isbn10_ok("0-306-40615-3"))
''',
        ),
        T(
            "v102-median",
            "stats",
            """Implement `median_int(xs: list[int]) -> float` for a non-empty list
(average the two middle values when length is even).""",
            '''
def median_int(xs):
    if not xs:
        raise ValueError("empty")
    ys = sorted(xs)
    n = len(ys)
    mid = n // 2
    if n % 2:
        return float(ys[mid])
    return (ys[mid - 1] + ys[mid]) / 2
''',
            '''
import unittest
from solution import median_int

class Test(unittest.TestCase):
    def test_odd(self):
        self.assertEqual(median_int([3, 1, 2]), 2.0)
    def test_even(self):
        self.assertEqual(median_int([1, 2, 3, 4]), 2.5)
''',
        ),
    ]
