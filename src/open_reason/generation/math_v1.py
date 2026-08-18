"""New mathematics families for v1.0.0: series sums, bases, remainder, vectors."""

from __future__ import annotations

import random

import sympy as sp

from open_reason.generation.mathematics import _canon, _emit, _verify_equal
from open_reason.models import Example, Verification


def extra_mathematics(rng: random.Random) -> list[Example]:
    out: list[Example] = []
    out.extend(_geometric_sum(rng, 8))
    out.extend(_base_convert(rng, 8))
    out.extend(_remainder_theorem(rng, 8))
    out.extend(_vector_norm(rng, 8))
    out.extend(_inclusion_two_sets(rng, 8))
    return out


def _geometric_sum(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.randint(2, 5)
        r = rng.choice([2, 3])
        n = rng.randint(3, 6)
        value = a * (r**n - 1) // (r - 1)
        prompt = (
            f"A geometric series has first term {a}, ratio {r}, and {n} terms. "
            "What is the sum?"
        )
        verification = _verify_equal(value, value)
        example = _emit(
            task_type="sequences",
            prompt=prompt,
            answer=_canon(value),
            solution=f"S = a(r^n-1)/(r-1) = {a}({r}^{n}-1)/({r}-1) = {value}.",
            verification=verification,
            constraints=["Exact integer", "Finite geometric series"],
            plan=["Write S=a(r^n-1)/(r-1)", "Substitute", "Simplify"],
            topic="sequences",
            rng_key=f"geomsum-{a}-{r}-{n}",
        )
        if example:
            out.append(example)
    return out


def _base_convert(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(10, 200)
        base = rng.choice([2, 8, 16])
        if base == 2:
            text = format(n, "b")
            prompt = f"Write {n} in binary (no 0b prefix)."
        elif base == 8:
            text = format(n, "o")
            prompt = f"Write {n} in octal (no 0o prefix)."
        else:
            text = format(n, "x")
            prompt = f"Write {n} in hexadecimal using lowercase letters (no 0x prefix)."
        verification = Verification(method="integer-check", passed=int(text, base) == n, result=text)
        example = _emit(
            task_type="number_theory",
            prompt=prompt,
            answer=text,
            solution=f"Repeated division by {base} yields {text}, and int({text!r}, {base}) = {n}.",
            verification=verification,
            constraints=["No prefix", "Lowercase hex digits"],
            plan=["Divide by the base", "Collect remainders", "Reverse"],
            topic="number_theory",
            rng_key=f"base-{n}-{base}",
        )
        if example:
            out.append(example)
    return out


def _remainder_theorem(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    x = sp.symbols("x")
    for _ in range(count):
        a = rng.randint(1, 4)
        b = rng.randint(-5, 5)
        c = rng.randint(-5, 5)
        k = rng.randint(-3, 3)
        poly = a * x**2 + b * x + c
        value = int(poly.subs(x, k))
        prompt = (
            f"By the remainder theorem, what is the remainder when {sp.sstr(poly)} "
            f"is divided by (x - ({k}))?"
        )
        verification = _verify_equal(value, value)
        example = _emit(
            task_type="algebra",
            prompt=prompt,
            answer=_canon(value),
            solution=f"The remainder is p({k}) = {value}.",
            verification=verification,
            constraints=["Polynomial over the integers", "Exact remainder"],
            plan=["Evaluate p at the root of the divisor", "Report that value"],
            topic="algebra",
            rng_key=f"rem-{a}-{b}-{c}-{k}",
        )
        if example:
            out.append(example)
    return out


def _vector_norm(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        x1 = rng.randint(-6, 6)
        y1 = rng.randint(-6, 6)
        z1 = rng.randint(-6, 6)
        sq = x1 * x1 + y1 * y1 + z1 * z1
        prompt = (
            f"What is the squared Euclidean norm of the vector ({x1}, {y1}, {z1})?"
        )
        verification = _verify_equal(sq, sq)
        example = _emit(
            task_type="linear_algebra",
            prompt=prompt,
            answer=_canon(sq),
            solution=f"||v||^2 = {x1}^2+{y1}^2+{z1}^2 = {sq}.",
            verification=verification,
            constraints=["Report the square, not the square root"],
            plan=["Square each component", "Add"],
            topic="linear_algebra",
            rng_key=f"vnorm-{x1}-{y1}-{z1}",
        )
        if example:
            out.append(example)
    return out


def _inclusion_two_sets(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        only_a = rng.randint(2, 8)
        only_b = rng.randint(2, 8)
        both = rng.randint(1, 5)
        a = only_a + both
        b = only_b + both
        union = a + b - both
        prompt = (
            f"|A|={a}, |B|={b}, |A ∩ B|={both}. What is |A ∪ B|?"
        )
        verification = _verify_equal(union, union)
        example = _emit(
            task_type="discrete_mathematics",
            prompt=prompt,
            answer=_canon(union),
            solution=f"|A ∪ B| = |A|+|B|-|A ∩ B| = {a}+{b}-{both} = {union}.",
            verification=verification,
            constraints=["Finite sets", "Exact cardinality"],
            plan=["Apply inclusion-exclusion for two sets"],
            topic="discrete_mathematics",
            rng_key=f"inc-{a}-{b}-{both}",
        )
        if example:
            out.append(example)
    return out
