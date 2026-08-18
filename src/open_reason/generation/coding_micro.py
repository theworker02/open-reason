"""Additional unique, executable micro-tasks.

Each item is a distinct specification (different function, different tests),
not a paraphrased clone of another row.
"""

from __future__ import annotations

from typing import Any, Callable

from open_reason.generation.coding_python import T, PyTask

Transform = tuple[str, str, str, list[Any]]


def _eval_body(fn: str, body: str, samples: list[Any]) -> list[tuple[Any, Any]]:
    ns: dict[str, Any] = {}
    exec(body, ns)
    func: Callable = ns[fn]
    n = func.__code__.co_argcount
    out: list[tuple[Any, Any]] = []
    for sample in samples:
        if n == 1:
            arg = sample[0] if isinstance(sample, tuple) and len(sample) == 1 else sample
            out.append((arg, func(arg)))
        else:
            out.append((sample, func(*sample)))
    return out


def _assert_lines_from_eval(fn: str, evaluated: list[tuple[Any, Any]]) -> str:
    lines = [
        "import unittest",
        f"from solution import {fn}",
        "class Test(unittest.TestCase):",
    ]
    for i, (args, expected) in enumerate(evaluated):
        if isinstance(args, tuple) and func_n(evaluated, i) != 1:
            arg_list = ", ".join(repr(a) for a in args)
        else:
            arg_list = repr(args)
        lines.append(
            f"    def test_{i}(self):\n        self.assertEqual({fn}({arg_list}), {expected!r})"
        )
    return "\n".join(lines) + "\n"


def func_n(evaluated: list[tuple[Any, Any]], i: int) -> int:
    args = evaluated[i][0]
    if isinstance(args, tuple):
        return len(args)
    return 1


INT_TASKS: list[tuple[str, str, str, list[Any]]] = [
    ("tripleneg", "Return n*3 if n<0 else n+3.", "def tripleneg(n):\n    return n*3 if n<0 else n+3\n", list(range(-4, 6))),
    ("clamp8", "Clamp n into [0, 8].", "def clamp8(n):\n    return 0 if n<0 else 8 if n>8 else n\n", list(range(-2, 12))),
    ("ones_mod", "Return n % 9, with 0 mapping to 0 (digital-root step).", "def ones_mod(n):\n    return n % 9\n", list(range(0, 20))),
    ("is_sq", "Return True iff n is a perfect square (n>=0).", "def is_sq(n):\n    if n<0:\n        return False\n    r=int(n**0.5)\n    return r*r==n\n", list(range(-1, 18))),
    ("next_even", "Smallest even integer >= n.", "def next_even(n):\n    return n if n%2==0 else n+1\n", list(range(-3, 8))),
    ("collatz_step", "One Collatz step: n/2 if even else 3n+1, for positive n.", "def collatz_step(n):\n    return n//2 if n%2==0 else 3*n+1\n", list(range(1, 16))),
    ("popcount", "Number of 1-bits in the absolute value of n.", "def popcount(n):\n    return bin(abs(n)).count('1')\n", list(range(-8, 17))),
    ("rev_digits", "Integer obtained by reversing decimal digits of |n|, keeping sign.", "def rev_digits(n):\n    s=int(str(abs(n))[::-1])\n    return -s if n<0 else s\n", [-120, -10, 0, 7, 100, 1234, 900]),
    ("sum_digits", "Sum of decimal digits of |n|.", "def sum_digits(n):\n    return sum(int(c) for c in str(abs(n)))\n", [0, 10, 99, 123, 1001, -58]),
    ("mid3", "Median of three integers a,b,c.", "def mid3(a,b,c):\n    return sorted([a,b,c])[1]\n", [(1,2,3),(9,1,5),(0,0,1),(-4,-1,-3),(8,8,2)]),
    ("gcd3", "gcd of three integers.", "import math\ndef gcd3(a,b,c):\n    return math.gcd(math.gcd(a,b),c)\n", [(12,18,30),(7,9,11),(0,5,10),(21,14,7)]),
    ("powmod", "Compute pow(a,b,m) for m>0, b>=0.", "def powmod(a,b,m):\n    return pow(a,b,m)\n", [(2,10,1000),(3,5,7),(5,0,9),(7,3,5)]),
    ("ceil_div", "Ceiling of a/b for positive b.", "def ceil_div(a,b):\n    return -(-a//b)\n", [(10,3),(9,3),(1,5),(-7,3),(0,4)]),
    ("bit_rev8", "Reverse the low 8 bits of n (ignore higher bits).", "def bit_rev8(n):\n    x=n & 255\n    y=0\n    for _ in range(8):\n        y=(y<<1)|(x&1)\n        x>>=1\n    return y\n", [0, 1, 2, 16, 128, 170, 255]),
    ("sgn", "Return -1, 0, or 1 as the sign of n.", "def sgn(n):\n    return (n>0)-(n<0)\n", list(range(-3, 4))),
]

STR_TASKS: list[tuple[str, str, str, list[Any]]] = [
    ("vowels", "Count vowels aeiou in s, case-insensitive.", "def vowels(s):\n    return sum(ch.lower() in 'aeiou' for ch in s)\n", ["", "xyz", "AEIOU", "Open Reason", "queue"]),
    ("snake", "Convert CamelCase or spaces to snake_case keeping alphanumerics.", "import re\ndef snake(s):\n    s=re.sub(r'([a-z])([A-Z])', r'\\1_\\2', s)\n    s=re.sub(r'[^A-Za-z0-9]+', '_', s)\n    return re.sub(r'_+', '_', s).strip('_').lower()\n", ["OpenReason", "already_snake", "Hello World", "A"]),
    ("runlen", "Run-length encode a string as list of (char, count) pairs.", "def runlen(s):\n    if not s:\n        return []\n    out=[]; last=s[0]; n=1\n    for ch in s[1:]:\n        if ch==last:\n            n+=1\n        else:\n            out.append((last,n)); last=ch; n=1\n    out.append((last,n))\n    return out\n", ["", "aaa", "abba", "aabbaa"]),
    ("is_anagram", "True iff a and b are anagrams ignoring spaces and case.", "def is_anagram(a,b):\n    def n(x): return sorted(ch.lower() for ch in x if not ch.isspace())\n    return n(a)==n(b)\n", [("listen","silent"),("a","b"),("Dormitory","dirty room"),("","")]),
    ("titlecase_min", "Title-case words, leaving words of length 1-2 lower except the first.", "def titlecase_min(s):\n    parts=s.split(' ')\n    out=[]\n    for i,w in enumerate(parts):\n        if not w:\n            out.append(w); continue\n        if i>0 and len(w)<=2:\n            out.append(w.lower())\n        else:\n            out.append(w[:1].upper()+w[1:].lower())\n    return ' '.join(out)\n", ["open reason dataset", "a b cde", "SQL"]),
    ("strip_html", "Remove <...> tags; do not parse attributes specially.", "def strip_html(s):\n    out=[]; i=0\n    while i<len(s):\n        if s[i]=='<':\n            j=s.find('>', i)\n            if j==-1:\n                break\n            i=j+1\n        else:\n            out.append(s[i]); i+=1\n    return ''.join(out)\n", ["<b>x</b>", "plain", "<a href='t'>z</a>y"]),
    ("csv_escape", "Escape a field for CSV: wrap in quotes if it contains comma, quote, or newline; double quotes.", "def csv_escape(s):\n    if any(ch in s for ch in ',\\n\"'):\n        return '\"'+s.replace('\"','\"\"')+'\"'\n    return s\n", ["plain", "a,b", 'say "hi"', "ok"]),
    ("prefix_fun", "Longest common prefix of a list of strings; '' if empty list.", "def prefix_fun(xs):\n    if not xs:\n        return ''\n    p=xs[0]\n    for s in xs[1:]:\n        i=0\n        while i<len(p) and i<len(s) and p[i]==s[i]:\n            i+=1\n        p=p[:i]\n        if not p:\n            return ''\n    return p\n", [(["flower","flow","flight"],), (["a","b"],), ([],), (["same","same"],)]),
    ("wrap_at", "Word-wrap s at width w without breaking words; words longer than w stay on their own line.", "def wrap_at(s,w):\n    words=s.split()\n    lines=[]; cur=''\n    for word in words:\n        if not cur:\n            cur=word\n        elif len(cur)+1+len(word)<=w:\n            cur+=' '+word\n        else:\n            lines.append(cur); cur=word\n    if cur:\n        lines.append(cur)\n    return lines\n", [("one two three", 5), ("abcdefgh", 3), ("a b c", 10)]),
    ("kebab", "Lowercase kebab-case from a phrase.", "import re\ndef kebab(s):\n    s=re.sub(r'[^A-Za-z0-9]+','-',s)\n    return s.strip('-').lower()\n", ["Open Reason", "already-kebab", "X"]),
]

LIST_TASKS: list[tuple[str, str, str, list[Any]]] = [
    ("moving_avg", "Simple moving average of window k; skip if k<1. Return list of floats.", "def moving_avg(xs,k):\n    if k<1:\n        raise ValueError('k')\n    return [sum(xs[i:i+k])/k for i in range(0, len(xs)-k+1)]\n", [([1,2,3,4],2), ([5],1), ([2,2,2,2],3)]),
    ("dedupe_keep", "Dedupe a list keeping first occurrence.", "def dedupe_keep(xs):\n    seen=set(); out=[]\n    for x in xs:\n        if x in seen:\n            continue\n        seen.add(x); out.append(x)\n    return out\n", [([1,1,2,1,3],), ([],), (["a","b","a"],)]),
    ("chunk2", "Pairs of consecutive items; drop a trailing leftover.", "def chunk2(xs):\n    return [(xs[i],xs[i+1]) for i in range(0,len(xs)-1,2)]\n", [([1,2,3,4],), ([1],), ([1,2,3],)]),
    ("argmin", "Index of the first minimum, or -1 if empty.", "def argmin(xs):\n    if not xs:\n        return -1\n    m=min(xs)\n    return xs.index(m)\n", [([3,1,1],), ([],), ([5],), ([-2,0,-2],)]),
    ("prefix_sums", "Inclusive prefix sums.", "def prefix_sums(xs):\n    out=[]; t=0\n    for x in xs:\n        t+=x; out.append(t)\n    return out\n", [([1,2,3],), ([],), ([-1,1],)]),
    ("rotate_left", "Rotate list xs left by k (k may exceed len).", "def rotate_left(xs,k):\n    if not xs:\n        return []\n    k%=len(xs)\n    return xs[k:]+xs[:k]\n", [([1,2,3,4],1), ([1,2],0), ([7],3), ([1,2,3],5)]),
    ("matrix_trace", "Trace of a square list-of-lists; raise ValueError if not square.", "def matrix_trace(m):\n    n=len(m)\n    if any(len(row)!=n for row in m):\n        raise ValueError('shape')\n    return sum(m[i][i] for i in range(n))\n", [([[1,2],[3,4]],), ([[5]],), ([[0,1,2],[3,4,5],[6,7,8]],)]),
    ("flatten1", "Flatten one level of lists.", "def flatten1(xs):\n    out=[]\n    for x in xs:\n        if isinstance(x,list):\n            out.extend(x)\n        else:\n            out.append(x)\n    return out\n", [([1,[2,3],4],), ([],), ([[],1],)]),
    ("count_ranges", "Count how many numbers in xs lie in [lo, hi] inclusive.", "def count_ranges(xs,lo,hi):\n    return sum(lo<=x<=hi for x in xs)\n", [([1,2,3,10],2,9), ([],0,1), ([-5,0,5],0,5)]),
    ("is_sorted", "Non-decreasing check.", "def is_sorted(xs):\n    return all(xs[i]<=xs[i+1] for i in range(len(xs)-1))\n", [([1,2,2,3],), ([3,1],), ([],), ([1],)]),
]

MORE_TASKS: list[tuple[str, str, str, list[Any]]] = [
    ("fib", "nth Fibonacci with F(0)=0, F(1)=1.", "def fib(n):\n    a,b=0,1\n    for _ in range(n):\n        a,b=b,a+b\n    return a\n", list(range(0, 12))),
    ("fact", "n! for n>=0.", "def fact(n):\n    r=1\n    for i in range(2,n+1):\n        r*=i\n    return r\n", list(range(0, 9))),
    ("is_prime", "True iff n is prime.", "def is_prime(n):\n    if n<2: return False\n    d=2\n    while d*d<=n:\n        if n%d==0: return False\n        d+=1\n    return True\n", list(range(0, 20))),
    ("n_primes", "Count primes in 1..n inclusive.", "def n_primes(n):\n    def p(x):\n        if x<2: return False\n        d=2\n        while d*d<=x:\n            if x%d==0: return False\n            d+=1\n        return True\n    return sum(p(i) for i in range(1,n+1))\n", [0,1,2,10,20,30]),
    ("base_conv", "Convert non-negative int n to base b (2..16) as a lowercase string without prefix.", "def base_conv(n,b):\n    digits='0123456789abcdef'\n    if n==0: return '0'\n    out=[]\n    while n:\n        out.append(digits[n%b]); n//=b\n    return ''.join(reversed(out))\n", [(0,2),(5,2),(255,16),(10,10),(8,8)]),
    ("parse_int_base", "Parse s in base b (2..16).", "def parse_int_base(s,b):\n    return int(s,b)\n", [("1010",2),("ff",16),("17",8),("0",10)]),
    ("hamming", "Hamming distance of two equal-length strings; ValueError if lengths differ.", "def hamming(a,b):\n    if len(a)!=len(b): raise ValueError('len')\n    return sum(x!=y for x,y in zip(a,b))\n", [("karolin","kathrin"),("000","111"),("a","a")]),
    ("lev_one", "True iff Levenshtein distance of a,b is at most 1.", "def lev_one(a,b):\n    if abs(len(a)-len(b))>1: return False\n    if len(a)==len(b):\n        return sum(x!=y for x,y in zip(a,b))<=1\n    if len(a)>len(b): a,b=b,a\n    i=j=diff=0\n    while i<len(a) and j<len(b):\n        if a[i]==b[j]:\n            i+=1; j+=1\n        else:\n            diff+=1; j+=1\n            if diff>1: return False\n    return True\n", [("cat","cut"),("cat","cats"),("cat","dog"),("a","a"),("ab","a")]),
    ("balanced_html", "True iff every <tag> is closed by </tag> with a stack, tags [a-z]+ only, no attributes.", "import re\ndef balanced_html(s):\n    stack=[]; i=0\n    while i<len(s):\n        if s.startswith('</',i):\n            m=re.match(r'</([a-z]+)>', s[i:])\n            if not m or not stack or stack[-1]!=m.group(1): return False\n            stack.pop(); i+=m.end()\n        elif s[i]=='<':\n            m=re.match(r'<([a-z]+)>', s[i:])\n            if not m: return False\n            stack.append(m.group(1)); i+=m.end()\n        else:\n            i+=1\n    return not stack\n", ["<b>x</b>", "<b><i></i></b>", "<b></i>", "plain", "<b><b></b>"]),
    ("path_join", "Join POSIX-like fragments, collapsing duplicate slashes but not resolving '..' .", "def path_join(parts):\n    s='/'.join(parts)\n    while '//' in s:\n        s=s.replace('//','/')\n    return s\n", [(["a","b"],), (["/a/","/b"],), (["a","","b"],)]),
    ("ext_of", "File extension including the dot, or '' if none. Basename only.", "def ext_of(name):\n    i=name.rfind('.')\n    if i<=0: return ''\n    return name[i:]\n", ["a.py", "a", ".gitignore", "a.b.c", "Makefile"]),
    ("relpath_dots", "Count leading '../' segments in a relative path string.", "def relpath_dots(p):\n    n=0\n    while p.startswith('../'):\n        n+=1; p=p[3:]\n    return n\n", ["../a", "../../x", "a/b", "../../../"]),
    ("semver_major", "Integer major version from 'X.Y.Z' (digits).", "def semver_major(s):\n    return int(s.split('.')[0])\n", ["1.2.3", "0.1.0", "10.0.0"]),
    ("iso_week_simple", "Map YYYY-MM-DD to (year, month, day) ints without validation.", "def iso_week_simple(s):\n    y,m,d=s.split('-')\n    return int(y),int(m),int(d)\n", ["2026-08-18", "1999-01-02"]),
    ("bytes_human", "Format n bytes as integer unit: B, KiB, MiB, GiB using 1024, one decimal if unit!=B.", "def bytes_human(n):\n    units=['B','KiB','MiB','GiB']\n    f=float(n); i=0\n    while f>=1024 and i<len(units)-1:\n        f/=1024; i+=1\n    if i==0: return f'{int(f)}B'\n    return f'{f:.1f}{units[i]}'\n", [0, 500, 1024, 1536, 1048576]),
    ("slug_n", "Keep [a-z0-9]+ lowercase tokens joined by hyphen.", "import re\ndef slug_n(s):\n    toks=re.findall(r'[a-z0-9]+', s.lower())\n    return '-'.join(toks)\n", ["Open Reason 1", "Hello!!!", "already-ok"]),
    ("mask_email", "Replace local part of an email with first char + '***' + domain; if no @ return s.", "def mask_email(s):\n    if '@' not in s: return s\n    local,dom=s.split('@',1)\n    if not local: return s\n    return local[0]+'***@'+dom\n", ["a@b.com", "user@example.com", "nope"]),
    ("score_bowling_frame", "Score one bowling frame given two rolls 0-10; if first is 10 ignore second and return 10.", "def score_bowling_frame(a,b):\n    if a==10: return 10\n    return a+b\n", [(10,0),(7,2),(0,0),(9,1)]),
    ("grade_pct", "Letter from percent: A>=90, B>=80, C>=70, D>=60 else F.", "def grade_pct(p):\n    if p>=90: return 'A'\n    if p>=80: return 'B'\n    if p>=70: return 'C'\n    if p>=60: return 'D'\n    return 'F'\n", [100,90,89,70,60,59,0]),
    ("rle_decode", "Decode list of (char,count) to string.", "def rle_decode(pairs):\n    return ''.join(ch*n for ch,n in pairs)\n", [([('a',3),('b',1)],), ([],), ([('x',1)],)]),
    ("set_bits_below", "Value with the lowest n bits set, n in 0..16.", "def set_bits_below(n):\n    return (1<<n)-1\n", list(range(0, 9))),
    ("align_up", "Smallest multiple of `align` >= n, align>0.", "def align_up(n,align):\n    return n if n%align==0 else n+(align-n%align)\n", [(0,8),(1,8),(8,8),(15,4)]),
    ("gray_encode", "Binary-reflected Gray code of n: n xor (n>>1).", "def gray_encode(n):\n    return n ^ (n>>1)\n", list(range(0, 12))),
    ("is_pow2", "True iff n is a power of two (n>0).", "def is_pow2(n):\n    return n>0 and (n & (n-1))==0\n", list(range(-1, 17))),
    ("clamp_list", "Clamp each value of xs into [lo,hi].", "def clamp_list(xs,lo,hi):\n    return [lo if x<lo else hi if x>hi else x for x in xs]\n", [([0,5,10],1,8), ([],0,1), ([-3],0,1)]),
    ("dot", "Dot product of equal-length lists; ValueError otherwise.", "def dot(a,b):\n    if len(a)!=len(b): raise ValueError('len')\n    return sum(x*y for x,y in zip(a,b))\n", [([1,2,3],[4,5,6]), ([],[]), ([2],[3])]),
    ("softmax_argmax", "Index of max in xs (first on ties); -1 if empty. (No actual softmax.)", "def softmax_argmax(xs):\n    if not xs: return -1\n    return max(range(len(xs)), key=lambda i: xs[i])\n", [([0.1,0.7,0.2],), ([],), ([1,1],)]),
    ("tokenize_ws", "Split on whitespace and drop empties.", "def tokenize_ws(s):\n    return s.split()\n", ["a  b\\tc", "", "  x"]),
    ("camel_from_snake", "snake_case to camelCase (first token lower).", "def camel_from_snake(s):\n    parts=[p for p in s.split('_') if p]\n    if not parts: return ''\n    return parts[0].lower()+''.join(p[:1].upper()+p[1:] for p in parts[1:])\n", ["open_reason", "a", "already", ""]),
    ("unique_sorted", "Sorted unique values of xs.", "def unique_sorted(xs):\n    return sorted(set(xs))\n", [([3,1,2,1],), ([],), ([0,0],)]),
    ("window_product", "Maximum product of any contiguous pair; None if len<2.", "def window_product(xs):\n    if len(xs)<2: return None\n    return max(xs[i]*xs[i+1] for i in range(len(xs)-1))\n", [([1,5,2],), ([2],), ([-3,-2,4],)]),
    ("binsearch_exists", "True iff target is in sorted xs (binary search).", "def binsearch_exists(xs,target):\n    lo,hi=0,len(xs)-1\n    while lo<=hi:\n        mid=(lo+hi)//2\n        if xs[mid]==target: return True\n        if xs[mid]<target: lo=mid+1\n        else: hi=mid-1\n    return False\n", [([1,3,5,7],5), ([1,3,5],2), ([],1), ([4],4)]),
    ("queue_ttl_ready", "From list of (t,item) already sorted by t, return items with t<=now.", "def queue_ttl_ready(events,now):\n    return [item for t,item in events if t<=now]\n", [([(1,'a'),(5,'b')],3), ([],0), ([(0,'x')],0)]),
    ("majority_vote", "Return the unique mode if it appears > n/2 else None.", "def majority_vote(xs):\n    if not xs: return None\n    cand=None; v=0\n    for x in xs:\n        if v==0: cand=x\n        v += 1 if x==cand else -1\n    if xs.count(cand)>len(xs)//2: return cand\n    return None\n", [([1,1,2],), ([1,2,3],), ([],), ([7,7,7,1],)]),
    ("polygon_area", "Shoelace area of a simple polygon listed as (x,y) pairs, nonnegative.", "def polygon_area(pts):\n    n=len(pts); s=0\n    for i in range(n):\n        x1,y1=pts[i]; x2,y2=pts[(i+1)%n]\n        s+=x1*y2-x2*y1\n    return abs(s)/2\n", [([(0,0),(1,0),(0,1)],), ([(0,0),(2,0),(2,2),(0,2)],)]),
]


def _tasks_from(spec: tuple[str, str, str, list[Any]], kind: str) -> PyTask:
    fn, prompt, body, samples = spec
    ns: dict[str, Any] = {}
    exec(body, ns)
    func: Callable = ns[fn]
    n = func.__code__.co_argcount
    evaluated = _eval_body(fn, body, samples)
    tests = _assert_from_eval(fn, evaluated, n)
    return T(
        f"micro_{fn}",
        kind,
        f"Implement `{fn}`: {prompt} Use only the Python standard library.",
        body,
        tests,
        task_type="code_generation",
    )


def _assert_from_eval(fn: str, evaluated: list[tuple[Any, Any]], n: int) -> str:
    lines = [
        "import unittest",
        f"from solution import {fn}",
        "class Test(unittest.TestCase):",
    ]
    for i, (args, expected) in enumerate(evaluated):
        if n == 1:
            arg_list = repr(args)
        else:
            arg_list = ", ".join(repr(a) for a in args)
        lines.append(
            f"    def test_{i}(self):\n        self.assertEqual({fn}({arg_list}), {expected!r})"
        )
    return "\n".join(lines) + "\n"


def micro_python_tasks() -> list[PyTask]:
    out: list[PyTask] = []
    for spec in INT_TASKS:
        out.append(_tasks_from(spec, "algorithms"))
    for spec in STR_TASKS:
        out.append(_tasks_from(spec, "algorithms"))
    for spec in LIST_TASKS:
        out.append(_tasks_from(spec, "data_structures"))
    for spec in MORE_TASKS:
        out.append(_tasks_from(spec, "algorithms"))
    return out
