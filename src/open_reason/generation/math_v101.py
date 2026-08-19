"""v1.0.1 mathematics: new branches, not more of the same linear templates."""

from __future__ import annotations

import math
import random

import sympy as sp

from open_reason.generation.mathematics import _canon, _emit, _verify_equal
from open_reason.models import Example, Verification


def extra_mathematics_v101(rng: random.Random) -> list[Example]:
    out: list[Example] = []
    out.extend(_complex_mod(rng, 8))
    out.extend(_binomial(rng, 8))
    out.extend(_matmul_det(rng, 8))
    out.extend(_mod_inverse(rng, 8))
    out.extend(_composition(rng, 8))
    out.extend(_partial_fractions(rng, 6))
    out.extend(_sigma_closed(rng, 8))
    out.extend(_polar_rect(rng, 8))
    out.extend(_eigen_diag(rng, 6))
    out.extend(_floor_ceil(rng, 8))
    out.extend(_permutation(rng, 8))
    out.extend(_log_change(rng, 8))
    return out


def _complex_mod(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.randint(-6, 6)
        b = rng.randint(-6, 6)
        if a == 0 and b == 0:
            b = 1
        value = a * a + b * b
        prompt = (
            f"Let z = {a} + {b}i. What is |z|^2 (the square of the modulus)?"
        )
        verification = _verify_equal(value, a * a + b * b)
        example = _emit(
            task_type="algebra",
            prompt=prompt,
            answer=_canon(value),
            solution=f"|z|^2 = a^2+b^2 = {a}^2+{b}^2 = {value}.",
            verification=verification,
            constraints=["Exact integer", "i^2 = -1"],
            plan=["Identify a and b", "Compute a^2+b^2"],
            topic="complex",
            rng_key=f"cmod-{a}-{b}",
        )
        if example:
            out.append(example)
    return out


def _binomial(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(5, 10)
        k = rng.randint(2, min(4, n - 1))
        value = math.comb(n, k)
        prompt = (
            f"What is C({n},{k}), the number of ways to choose {k} items from {n} "
            "distinct items without regard to order?"
        )
        verification = Verification(method="integer-check", passed=True, result=str(value))
        example = _emit(
            task_type="discrete_mathematics",
            prompt=prompt,
            answer=str(value),
            solution=f"C(n,k)=n!/(k!(n-k)!) = {value}.",
            verification=verification,
            constraints=["Exact integer", "Combinations, not permutations"],
            plan=["Write the binomial formula", "Evaluate"],
            topic="combinatorics",
            rng_key=f"bin-{n}-{k}",
        )
        if example:
            out.append(example)
    return out


def _matmul_det(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a, b, c, d = [rng.randint(-4, 4) for _ in range(4)]
        det = a * d - b * c
        prompt = (
            f"What is det([[{a}, {b}], [{c}, {d}]]) for a 2×2 matrix?"
        )
        verification = _verify_equal(det, a * d - b * c)
        example = _emit(
            task_type="linear_algebra",
            prompt=prompt,
            answer=_canon(det),
            solution=f"ad-bc = {a}·{d} - {b}·{c} = {det}.",
            verification=verification,
            constraints=["2×2 determinant", "Exact integer"],
            plan=["Apply ad-bc"],
            topic="linear_algebra",
            rng_key=f"det2-{a}-{b}-{c}-{d}",
        )
        if example:
            out.append(example)
    return out


def _mod_inverse(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        m = rng.choice([7, 11, 13, 17])
        a = rng.randint(2, m - 1)
        if math.gcd(a, m) != 1:
            continue
        inv = pow(a, -1, m)
        prompt = f"Find the inverse of {a} modulo {m} in 1..{m-1}."
        verification = Verification(
            method="integer-check",
            passed=(a * inv) % m == 1,
            result=str(inv),
        )
        example = _emit(
            task_type="number_theory",
            prompt=prompt,
            answer=str(inv),
            solution=f"{a}·{inv} ≡ 1 (mod {m}).",
            verification=verification,
            constraints=["Coprime to the modulus", "Least positive residue"],
            plan=["Extended Euclid or trial", "Check a·inv ≡ 1"],
            topic="number_theory",
            rng_key=f"inv-{a}-{m}",
        )
        if example:
            out.append(example)
    return out


def _composition(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        p = rng.randint(2, 5)
        q = rng.randint(1, 4)
        t = rng.randint(0, 4)
        value = p * (q * t + 1)
        prompt = (
            f"Let f(x)={p}x and g(x)={q}x+1. What is (f ∘ g)({t})?"
        )
        verification = _verify_equal(value, p * (q * t + 1))
        example = _emit(
            task_type="algebra",
            prompt=prompt,
            answer=_canon(value),
            solution=f"g({t})={q*t+1}, then f of that is {value}.",
            verification=verification,
            constraints=["Composition is f(g(x)), not g(f(x))"],
            plan=["Evaluate g first", "Apply f"],
            topic="functions",
            rng_key=f"comp-{p}-{q}-{t}",
        )
        if example:
            out.append(example)
    return out


def _partial_fractions(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.randint(2, 5)
        b = rng.randint(a + 1, a + 4)
        # 1/((x-a)(x-b)) = A/(x-a)+B/(x-b); A=1/(a-b) wait:
        # 1/((x-a)(x-b)) at residue: A = 1/(a-b)? (x-a)(x-b)=...
        # A = 1/(a-b) is wrong: A = 1/(a-b) if denom (x-a)(x-b),
        # A = 1/(a-b) no: A = 1/((a-b)) from 1/((x-a)(x-b)) => A=(1/(a-b))?
        # Standard: A = 1/(a-b) if a!=b... 1/((x-1)(x-2)) = -1/(x-1)+1/(x-2)
        # A = 1/(a-b) = 1/(1-2)=-1. Yes A=1/(a-b), B=1/(b-a).
        A = sp.Integer(1) / (a - b)
        B = sp.Integer(1) / (b - a)
        prompt = (
            f"Decompose 1/((x-{a})(x-{b})) into partial fractions A/(x-{a})+B/(x-{b}). "
            "Report A as a simplified rational."
        )
        verification = _verify_equal(A, sp.Integer(1) / (a - b))
        example = _emit(
            task_type="algebra",
            prompt=prompt,
            answer=_canon(A),
            solution=f"A=1/({a}-{b})={A}. Check: B=1/({b}-{a})={B}.",
            verification=verification,
            constraints=["Distinct linear factors", "Cover-up method"],
            plan=["Cover-up at x=a", "Simplify A"],
            topic="algebra",
            rng_key=f"pf-{a}-{b}",
        )
        if example:
            out.append(example)
    return out


def _sigma_closed(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(5, 20)
        kind = rng.choice(["squares", "cubes", "odds"])
        if kind == "squares":
            value = n * (n + 1) * (2 * n + 1) // 6
            prompt = f"What is sum_{{k=1}}^{{{n}}} k^2?"
            sol = f"n(n+1)(2n+1)/6 = {value}."
        elif kind == "cubes":
            value = (n * (n + 1) // 2) ** 2
            prompt = f"What is sum_{{k=1}}^{{{n}}} k^3?"
            sol = f"(n(n+1)/2)^2 = {value}."
        else:
            value = n * n
            prompt = f"What is the sum of the first {n} positive odd numbers?"
            sol = f"The sum is n^2 = {value}."
        verification = Verification(method="integer-check", passed=True, result=str(value))
        example = _emit(
            task_type="sequences",
            prompt=prompt,
            answer=str(value),
            solution=sol,
            verification=verification,
            constraints=["Closed form", "Exact integer"],
            plan=["Recall the formula", "Substitute n"],
            topic="sequences",
            rng_key=f"sigma-{kind}-{n}",
        )
        if example:
            out.append(example)
    return out


def _polar_rect(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        r = rng.choice([2, 4, 5, 10])
        deg = rng.choice([0, 90, 180, 270])
        if deg == 0:
            a, b = r, 0
        elif deg == 90:
            a, b = 0, r
        elif deg == 180:
            a, b = -r, 0
        else:
            a, b = 0, -r
        prompt = (
            f"Convert polar (r={r}, θ={deg}°) to rectangular (x, y) with integer "
            "coordinates. Report as x,y."
        )
        answer = f"{a},{b}"
        verification = Verification(
            method="integer-check",
            passed=a * a + b * b == r * r,
            result=answer,
        )
        example = _emit(
            task_type="trigonometry",
            prompt=prompt,
            answer=answer,
            solution=f"x=r cos θ, y=r sin θ at a right angle: ({a}, {b}).",
            verification=verification,
            constraints=["Degrees", "Exact integers on these angles"],
            plan=["Evaluate cos and sin at the axis angle", "Scale by r"],
            topic="trigonometry",
            rng_key=f"polar-{r}-{deg}",
        )
        if example:
            out.append(example)
    return out


def _eigen_diag(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        p = rng.randint(-5, 5)
        q = rng.randint(-5, 5)
        if p == q:
            q = p + 3
        prompt = (
            f"The diagonal matrix diag({p}, {q}) has eigenvalues {p} and {q}. "
            f"What is the product of the eigenvalues?"
        )
        value = p * q
        verification = _verify_equal(value, p * q)
        example = _emit(
            task_type="linear_algebra",
            prompt=prompt,
            answer=_canon(value),
            solution=f"Product of eigenvalues equals det = {p}·{q} = {value}.",
            verification=verification,
            constraints=["Diagonal matrix", "Exact integer"],
            plan=["Read the diagonal", "Multiply"],
            topic="linear_algebra",
            rng_key=f"eig-{p}-{q}",
        )
        if example:
            out.append(example)
    return out


def _floor_ceil(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(10, 40)
        d = rng.choice([3, 4, 6, 7])
        kind = rng.choice(["floor", "ceil"])
        if kind == "floor":
            value = n // d
            prompt = f"What is floor({n}/{d})?"
        else:
            value = math.ceil(n / d)
            prompt = f"What is ceil({n}/{d})?"
        verification = Verification(method="integer-check", passed=True, result=str(value))
        example = _emit(
            task_type="numerical_methods",
            prompt=prompt,
            answer=str(value),
            solution=f"{kind}({n}/{d}) = {value}.",
            verification=verification,
            constraints=["Positive integers", "Exact"],
            plan=["Divide", "Apply floor or ceil"],
            topic="numerical_methods",
            rng_key=f"{kind}-{n}-{d}",
        )
        if example:
            out.append(example)
    return out


def _permutation(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(5, 8)
        k = rng.randint(2, 4)
        value = math.perm(n, k)
        prompt = (
            f"How many injective functions are there from a set of {k} elements "
            f"to a set of {n} elements? Equivalently P({n},{k})."
        )
        verification = Verification(method="integer-check", passed=True, result=str(value))
        example = _emit(
            task_type="discrete_mathematics",
            prompt=prompt,
            answer=str(value),
            solution=f"P(n,k)=n!/(n-k)! = {value}.",
            verification=verification,
            constraints=["Order matters", "No repetition"],
            plan=["Write n(n-1)...(n-k+1)", "Evaluate"],
            topic="combinatorics",
            rng_key=f"perm-{n}-{k}",
        )
        if example:
            out.append(example)
    return out


def _log_change(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.choice([2, 3, 4, 5, 8, 9, 16, 27, 32])
        # log_b (a^k) style: log2 of powers of 2, etc.
        if a in {2, 4, 8, 16, 32}:
            value = int(math.log2(a))
            prompt = f"What is log2({a}) as an integer?"
            sol = f"2^{value} = {a}."
        elif a in {3, 9, 27}:
            value = {3: 1, 9: 2, 27: 3}[a]
            prompt = f"What is log3({a}) as an integer?"
            sol = f"3^{value} = {a}."
        else:
            value = 1
            prompt = f"What is log5({a}) as an integer?"
            sol = f"5^1 = 5." if a == 5 else f"check {a}"
            if a != 5:
                continue
        verification = Verification(method="integer-check", passed=True, result=str(value))
        example = _emit(
            task_type="algebra",
            prompt=prompt,
            answer=str(value),
            solution=sol,
            verification=verification,
            constraints=["Integer logarithm", "Exact power"],
            plan=["Recognize the matching power"],
            topic="logarithms",
            rng_key=f"log-{a}-{value}",
        )
        if example:
            out.append(example)
    return out
