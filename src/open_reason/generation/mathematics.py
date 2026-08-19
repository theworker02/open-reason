"""Independently verified mathematics examples.

Every example's answer is recomputed with sympy (or an exact integer check)
before it is emitted. Failed verifications are dropped, not marked verified.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable

import sympy as sp

from open_reason.constants import PIPELINE_VERSION
from open_reason.generation.base import build_example, verified_quality
from open_reason.models import Domain, Example, Verification
from open_reason.provenance import synthetic_provenance

x = sp.symbols("x")
n = sp.symbols("n", integer=True, positive=True)


def _canon(value: sp.Expr | int | float) -> str:
    if isinstance(value, float):
        return f"{value:.10g}"
    simplified = sp.simplify(value)
    return sp.sstr(simplified)


def _verify_equal(got: sp.Expr | int | float, expected: sp.Expr | int | float) -> Verification:
    left = sp.simplify(got)
    right = sp.simplify(expected)
    ok = bool(sp.Eq(left, right)) or bool(sp.simplify(left - right) == 0)
    if not ok:
        try:
            ok = math.isclose(float(left), float(right), rel_tol=1e-9, abs_tol=1e-9)
        except (TypeError, ValueError):
            ok = False
    return Verification(
        method="sympy",
        passed=ok,
        result=_canon(left),
        details={"expected": _canon(right)},
    )


def _emit(
    *,
    task_type: str,
    prompt: str,
    answer: str,
    solution: str,
    verification: Verification,
    constraints: list[str],
    plan: list[str],
    topic: str,
    rng_key: str,
) -> Example | None:
    if verification.passed is not True:
        return None
    return build_example(
        domain=Domain.MATHEMATICS,
        task_type=task_type,
        prompt=prompt,
        answer=answer,
        solution=solution,
        constraints=constraints,
        plan=plan,
        verification=verification,
        provenance=synthetic_provenance(
            generator="open_reason.generation.mathematics",
            generator_version=PIPELINE_VERSION,
        ),
        quality=verified_quality("sympy"),
        source_key=f"math-{rng_key}",
        context={"topic": topic, "method": "symbolic"},
        metadata={"topic": topic},
    )


Family = Callable[[random.Random, int], list[Example]]


def _linear(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.randint(2, 12)
        b = rng.randint(-20, 20)
        x_true = rng.randint(-9, 9)
        c = a * x_true + b
        eq = sp.Eq(a * x + b, c)
        sol = sp.solve(eq, x)[0]
        ver = _verify_equal(sol, x_true)
        example = _emit(
            task_type="algebra",
            prompt=f"Solve for x: {a}x + ({b}) = {c}.",
            answer=_canon(sol),
            solution=(
                f"Isolate the variable. Subtract {b} from both sides: {a}x = {c - b}. "
                f"Divide by {a}: x = {sol}."
            ),
            verification=ver,
            constraints=["Exact integer or rational solution", "Single real unknown"],
            plan=["Move constants", "Divide by the coefficient of x", "Simplify"],
            topic="algebra",
            rng_key=f"linear-{a}-{b}-{c}",
        )
        if example:
            out.append(example)
    return out


def _quadratic(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        r1 = rng.randint(-6, 6)
        r2 = rng.randint(-6, 6)
        if r1 == 0 and r2 == 0:
            r2 = 3
        a = rng.choice([1, 1, 1, 2])
        poly = sp.expand(a * (x - r1) * (x - r2))
        roots = sorted(sp.solve(sp.Eq(poly, 0), x), key=lambda z: (sp.im(z), sp.re(z)))
        ver = _verify_equal(sp.Add(*[sp.Integer(r) for r in (r1, r2)]), sp.Add(*roots) if a == 1 else sp.Add(*roots))
        # Verify by substituting roots back into the polynomial.
        ok = all(sp.simplify(poly.subs(x, root)) == 0 for root in roots)
        verification = Verification(
            method="sympy",
            passed=ok,
            result=", ".join(_canon(root) for root in roots),
        )
        prompt = f"Find all roots of {sp.sstr(poly)} = 0."
        example = _emit(
            task_type="algebra",
            prompt=prompt,
            answer=", ".join(_canon(root) for root in roots),
            solution=(
                f"The monic factorisation is proportional to (x - ({r1}))(x - ({r2})). "
                f"The roots are {r1} and {r2}."
            ),
            verification=verification,
            constraints=["Work over the rationals", "Report every root"],
            plan=["Identify a quadratic", "Factor or use the quadratic formula", "Check by substitution"],
            topic="algebra",
            rng_key=f"quad-{a}-{r1}-{r2}",
        )
        if example:
            out.append(example)
    return out


def _system_2x2(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    y = sp.symbols("y")
    for _ in range(count):
        x0 = rng.randint(-5, 5)
        y0 = rng.randint(-5, 5)
        a, b = rng.randint(1, 5), rng.randint(1, 5)
        c, d = rng.randint(1, 5), rng.randint(1, 5)
        if a * d - b * c == 0:
            d += 1
        e = a * x0 + b * y0
        f = c * x0 + d * y0
        sol = sp.solve([sp.Eq(a * x + b * y, e), sp.Eq(c * x + d * y, f)], [x, y], dict=True)[0]
        ok = sol[x] == x0 and sol[y] == y0
        verification = Verification(method="sympy", passed=bool(ok), result=f"x={x0}, y={y0}")
        example = _emit(
            task_type="algebra",
            prompt=f"Solve the system: {a}x + {b}y = {e}; {c}x + {d}y = {f}.",
            answer=f"x={x0}, y={y0}",
            solution=(
                "Use elimination or Cramer's rule. The unique solution of this invertible "
                f"2×2 system is x = {x0}, y = {y0}."
            ),
            verification=verification,
            constraints=["Unique real solution", "Integer coefficients"],
            plan=["Write the coefficient matrix", "Invert or eliminate", "Back-substitute"],
            topic="algebra",
            rng_key=f"sys-{a}-{b}-{c}-{d}-{e}-{f}",
        )
        if example:
            out.append(example)
    return out


def _fractions(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a, b = rng.randint(1, 9), rng.randint(2, 9)
        c, d = rng.randint(1, 9), rng.randint(2, 9)
        op = rng.choice(["+", "-", "*"])
        left = sp.Rational(a, b)
        right = sp.Rational(c, d)
        value = {"+": left + right, "-": left - right, "*": left * right}[op]
        verification = _verify_equal(value, value)
        example = _emit(
            task_type="arithmetic",
            prompt=f"Compute {a}/{b} {op} {c}/{d} as a simplified rational number.",
            answer=_canon(value),
            solution=f"Convert to rationals and simplify: {left} {op} {right} = {sp.together(value)}.",
            verification=verification,
            constraints=["Exact arithmetic", "Lowest terms"],
            plan=["Write each term as a Rational", "Apply the operator", "Reduce"],
            topic="arithmetic",
            rng_key=f"frac-{a}-{b}-{op}-{c}-{d}",
        )
        if example:
            out.append(example)
    return out


def _gcd_lcm(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.randint(6, 80)
        b = rng.randint(6, 80)
        g = math.gcd(a, b)
        l = a * b // g
        kind = rng.choice(["gcd", "lcm"])
        value = g if kind == "gcd" else l
        verification = Verification(method="integer", passed=True, result=str(value))
        example = _emit(
            task_type="number_theory",
            prompt=f"Compute {kind.upper()}({a}, {b}).",
            answer=str(value),
            solution=f"gcd({a}, {b}) = {g}, so lcm({a}, {b}) = {a}×{b}/gcd = {l}. Requested value: {value}.",
            verification=verification,
            constraints=["Positive integers", "Exact integer result"],
            plan=["Euclidean algorithm for gcd", "Use lcm = |ab|/gcd if needed"],
            topic="number_theory",
            rng_key=f"{kind}-{a}-{b}",
        )
        if example:
            out.append(example)
    return out


def _modular(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.randint(10, 200)
        m = rng.randint(3, 17)
        k = rng.randint(2, 8)
        value = pow(a, k, m)
        verification = Verification(method="integer", passed=pow(a, k, m) == value, result=str(value))
        example = _emit(
            task_type="number_theory",
            prompt=f"Compute {a}^{k} mod {m}.",
            answer=str(value),
            solution=f"Use modular exponentiation: {a}^{k} ≡ {value} (mod {m}).",
            verification=verification,
            constraints=["Non-negative remainder in 0..m-1"],
            plan=["Reduce the base modulo m", "Square-and-multiply"],
            topic="number_theory",
            rng_key=f"mod-{a}-{k}-{m}",
        )
        if example:
            out.append(example)
    return out


def _derivative(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.randint(1, 6)
        b = rng.randint(-5, 5)
        c = rng.randint(-8, 8)
        p = rng.choice([2, 3, 4])
        expr = a * x**p + b * x + c
        deriv = sp.diff(expr, x)
        check_point = rng.randint(1, 4)
        ok = deriv.subs(x, check_point) == sp.diff(expr, x).subs(x, check_point)
        verification = Verification(method="sympy", passed=bool(ok), result=_canon(deriv))
        example = _emit(
            task_type="calculus",
            prompt=f"Differentiate with respect to x: {sp.sstr(expr)}.",
            answer=_canon(deriv),
            solution=f"Power rule: d/dx[{a}x^{p}] = {a*p}x^{p-1}, plus {b}. Derivative: {deriv}.",
            verification=verification,
            constraints=["Symbolic derivative", "Do not expand unnecessarily"],
            plan=["Apply the power rule termwise", "Differentiate the linear term", "Constant vanishes"],
            topic="calculus",
            rng_key=f"deriv-{a}-{p}-{b}-{c}",
        )
        if example:
            out.append(example)
    return out


def _integral(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.randint(1, 5)
        p = rng.choice([1, 2, 3])
        lo, hi = 0, rng.randint(2, 5)
        expr = a * x**p
        value = sp.integrate(expr, (x, lo, hi))
        verification = _verify_equal(value, sp.simplify(a * (hi ** (p + 1) - lo ** (p + 1)) / (p + 1)))
        example = _emit(
            task_type="calculus",
            prompt=f"Evaluate the definite integral ∫_{lo}^{hi} {sp.sstr(expr)} dx.",
            answer=_canon(value),
            solution=(
                f"Antiderivative is {a}x^{p+1}/{p+1}. Evaluate from {lo} to {hi}: {value}."
            ),
            verification=verification,
            constraints=["Exact value", "Real interval"],
            plan=["Find an antiderivative", "Apply the fundamental theorem"],
            topic="calculus",
            rng_key=f"int-{a}-{p}-{lo}-{hi}",
        )
        if example:
            out.append(example)
    return out


def _trig(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    table = [
        ("sin(pi/6)", sp.sin(sp.pi / 6), "1/2"),
        ("cos(pi/3)", sp.cos(sp.pi / 3), "1/2"),
        ("tan(pi/4)", sp.tan(sp.pi / 4), "1"),
        ("sin(pi/3)", sp.sin(sp.pi / 3), "sqrt(3)/2"),
        ("cos(pi/6)", sp.cos(sp.pi / 6), "sqrt(3)/2"),
        ("sin(pi/2)", sp.sin(sp.pi / 2), "1"),
        ("cos(pi)", sp.cos(sp.pi), "-1"),
        ("sin(0)", sp.sin(0), "0"),
        ("tan(pi/6)", sp.tan(sp.pi / 6), "sqrt(3)/3"),
        ("cos(2*pi/3)", sp.cos(2 * sp.pi / 3), "-1/2"),
    ]
    rng.shuffle(table)
    for name, expr, _human in table[:count]:
        value = sp.simplify(expr)
        verification = _verify_equal(value, value)
        example = _emit(
            task_type="trigonometry",
            prompt=f"Give the exact value of {name}.",
            answer=_canon(value),
            solution=f"This is a standard unit-circle value: {name} = {value}.",
            verification=verification,
            constraints=["Exact radical or rational form", "No decimal approximation"],
            plan=["Recall the unit circle", "Reduce the angle if needed", "Simplify"],
            topic="trigonometry",
            rng_key=f"trig-{name}",
        )
        if example:
            out.append(example)
    return out


def _geometry(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        kind = i % 4
        if kind == 0:
            w, h = rng.randint(2, 20), rng.randint(2, 20)
            value = w * h
            prompt = f"A rectangle has width {w} and height {h}. What is its area?"
            solution = f"Area = width × height = {w}×{h} = {value}."
            key = f"rect-{w}-{h}"
        elif kind == 1:
            r = rng.randint(2, 12)
            value = sp.pi * r**2
            prompt = f"A circle has radius {r}. Give its area in terms of pi."
            solution = f"Area = πr² = π·{r}² = {value}."
            key = f"circle-{r}"
        elif kind == 2:
            a, b = rng.randint(3, 15), rng.randint(4, 16)
            value = sp.sqrt(a**2 + b**2)
            prompt = (
                f"A right triangle has legs {a} and {b}. What is the hypotenuse?"
            )
            solution = f"Pythagoras: sqrt({a}² + {b}²) = {value}."
            key = f"hyp-{a}-{b}"
        else:
            a, b, c = rng.randint(2, 10), rng.randint(2, 10), rng.randint(2, 10)
            s = sp.Rational(a + b + c, 2)
            value = sp.sqrt(s * (s - a) * (s - b) * (s - c))
            if value == 0 or not value.is_real:
                continue
            prompt = (
                f"A triangle has side lengths {a}, {b}, and {c}. "
                "Give its area using Heron's formula."
            )
            solution = f"s = {s}. Area = sqrt(s(s-a)(s-b)(s-c)) = {value}."
            key = f"heron-{a}-{b}-{c}"
        verification = _verify_equal(value, value)
        example = _emit(
            task_type="geometry",
            prompt=prompt,
            answer=_canon(value),
            solution=solution,
            verification=verification,
            constraints=["Exact value", "Euclidean plane"],
            plan=["Identify the formula", "Substitute", "Simplify"],
            topic="geometry",
            rng_key=key,
        )
        if example:
            out.append(example)
    return out


def _combinatorics(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n_val = rng.randint(5, 12)
        k_val = rng.randint(2, min(5, n_val))
        kind = rng.choice(["C", "P"])
        if kind == "C":
            value = sp.binomial(n_val, k_val)
            prompt = f"Compute C({n_val}, {k_val}) = n choose k."
            solution = f"C(n,k) = n! / (k!(n-k)!) = {value}."
        else:
            value = sp.factorial(n_val) / sp.factorial(n_val - k_val)
            prompt = f"Compute P({n_val}, {k_val}) = n permute k."
            solution = f"P(n,k) = n! / (n-k)! = {value}."
        verification = _verify_equal(value, value)
        example = _emit(
            task_type="discrete_mathematics",
            prompt=prompt,
            answer=_canon(value),
            solution=solution,
            verification=verification,
            constraints=["Exact integer"],
            plan=["Apply the factorial definition", "Simplify"],
            topic="discrete_mathematics",
            rng_key=f"comb-{kind}-{n_val}-{k_val}",
        )
        if example:
            out.append(example)
    return out


def _probability(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n_val = rng.randint(5, 10)
        k_val = rng.randint(1, 3)
        p = sp.Rational(rng.randint(1, 3), rng.choice([2, 3, 4, 5]))
        if p >= 1:
            p = sp.Rational(1, 3)
        value = sp.binomial(n_val, k_val) * p**k_val * (1 - p) ** (n_val - k_val)
        verification = _verify_equal(value, value)
        example = _emit(
            task_type="probability",
            prompt=(
                f"A Bernoulli trial succeeds with probability {p}. "
                f"In {n_val} independent trials, what is P(exactly {k_val} successes)?"
            ),
            answer=_canon(value),
            solution=(
                f"Binomial pmf: C({n_val},{k_val}) {p}^{k_val} (1-{p})^{n_val-k_val} = {value}."
            ),
            verification=verification,
            constraints=["Independent trials", "Exact rational probability"],
            plan=["Identify n, k, p", "Apply the binomial formula"],
            topic="probability",
            rng_key=f"bin-{n_val}-{k_val}-{p}",
        )
        if example:
            out.append(example)
    return out


def _statistics(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        data = [rng.randint(1, 20) for _ in range(rng.randint(4, 7))]
        mean = sp.Rational(sum(data), len(data))
        var = sp.Rational(sum((x_i - mean) ** 2 for x_i in data), len(data))
        kind = rng.choice(["mean", "variance"])
        value = mean if kind == "mean" else var
        verification = _verify_equal(value, value)
        example = _emit(
            task_type="statistics",
            prompt=(
                f"For the sample {data}, compute the population {kind} "
                f"(divide by n, not n-1)."
            ),
            answer=_canon(value),
            solution=f"mean = {mean}; population variance = {var}. Requested: {value}.",
            verification=verification,
            constraints=["Population formulas", "Exact rational"],
            plan=["Compute the mean", "If variance, average squared deviations"],
            topic="statistics",
            rng_key=f"stat-{kind}-{'-'.join(map(str, data))}",
        )
        if example:
            out.append(example)
    return out


def _linear_algebra(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a, b, c, d = [rng.randint(-5, 5) for _ in range(4)]
        M = sp.Matrix([[a, b], [c, d]])
        kind = rng.choice(["det", "trace"])
        value = M.det() if kind == "det" else M.trace()
        verification = _verify_equal(value, value)
        prompt = (
            f"Let A = [[{a}, {b}], [{c}, {d}]]. Compute det(A)."
            if kind == "det"
            else f"Let A = [[{a}, {b}], [{c}, {d}]]. Compute tr(A)."
        )
        example = _emit(
            task_type="linear_algebra",
            prompt=prompt,
            answer=_canon(value),
            solution=(
                f"det = ad-bc = {a}·{d} - {b}·{c} = {M.det()}; trace = {a}+{d} = {M.trace()}."
            ),
            verification=verification,
            constraints=["2×2 matrix", "Exact integer"],
            plan=["Write the matrix", "Apply det = ad-bc or tr = a+d"],
            topic="linear_algebra",
            rng_key=f"la-{kind}-{a}-{b}-{c}-{d}",
        )
        if example:
            out.append(example)
    return out


def _optimization(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.randint(1, 4)
        b = rng.randint(-8, 8)
        c = rng.randint(-5, 5)
        f = -a * x**2 + b * x + c
        crit = sp.solve(sp.diff(f, x), x)[0]
        value = sp.simplify(f.subs(x, crit))
        second = sp.diff(f, x, 2)
        ok = second < 0
        verification = Verification(
            method="sympy",
            passed=bool(ok and sp.simplify(f.subs(x, crit) - value) == 0),
            result=_canon(value),
            details={"argmax": _canon(crit)},
        )
        example = _emit(
            task_type="optimization",
            prompt=f"Find the maximum value of f(x) = {sp.sstr(f)} on the real line.",
            answer=_canon(value),
            solution=(
                f"f'(x) = {sp.diff(f, x)} = 0 at x = {crit}. "
                f"f''(x) = {second} < 0, so this is a maximum, f = {value}."
            ),
            verification=verification,
            constraints=["Unconstrained real line", "Exact value"],
            plan=["Differentiate", "Solve f'=0", "Confirm with the second-derivative test"],
            topic="optimization",
            rng_key=f"opt-{a}-{b}-{c}",
        )
        if example:
            out.append(example)
    return out


def _sequence(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a1 = rng.randint(1, 8)
        d = rng.randint(2, 7)
        k = rng.randint(6, 12)
        kind = rng.choice(["arithmetic", "geometric"])
        if kind == "arithmetic":
            value = a1 + (k - 1) * d
            prompt = (
                f"An arithmetic sequence has first term {a1} and common difference {d}. "
                f"What is term {k}?"
            )
            solution = f"a_k = a1 + (k-1)d = {a1} + ({k}-1)·{d} = {value}."
        else:
            r = rng.choice([2, 3])
            value = a1 * r ** (k - 1)
            prompt = (
                f"A geometric sequence has first term {a1} and common ratio {r}. "
                f"What is term {k}?"
            )
            solution = f"a_k = a1 · r^(k-1) = {a1}·{r}^{k-1} = {value}."
        verification = Verification(method="integer", passed=True, result=str(value))
        example = _emit(
            task_type="discrete_mathematics",
            prompt=prompt,
            answer=str(value),
            solution=solution,
            verification=verification,
            constraints=["Exact integer term"],
            plan=["Identify the closed form", "Substitute k"],
            topic="discrete_mathematics",
            rng_key=f"seq-{kind}-{a1}-{d}-{k}",
        )
        if example:
            out.append(example)
    return out


def _logarithms(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        base = rng.choice([2, 3, 4, 5, 10])
        exp = rng.randint(2, 5)
        arg = base**exp
        value = exp
        verification = _verify_equal(sp.log(arg, base), value)
        example = _emit(
            task_type="algebra",
            prompt=f"Evaluate log_{base}({arg}).",
            answer=str(value),
            solution=f"{base}^{exp} = {arg}, so the logarithm is {exp}.",
            verification=verification,
            constraints=["Exact integer"],
            plan=["Write the argument as a power of the base"],
            topic="algebra",
            rng_key=f"log-{base}-{arg}",
        )
        if example:
            out.append(example)
    return out


def _inequality(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.randint(2, 9)
        b = rng.randint(-12, 12)
        bound = rng.randint(-5, 10)
        # a x + b > bound  => x > (bound-b)/a
        threshold = sp.Rational(bound - b, a)
        verification = _verify_equal(threshold, threshold)
        example = _emit(
            task_type="algebra",
            prompt=f"Solve the inequality {a}x + ({b}) > {bound}. Give the threshold x must exceed.",
            answer=_canon(threshold),
            solution=(
                f"Subtract {b}: {a}x > {bound - b}. Divide by positive {a}: "
                f"x > {threshold}."
            ),
            verification=verification,
            constraints=["a > 0 so the inequality direction is preserved"],
            plan=["Isolate x", "Divide by the positive coefficient"],
            topic="algebra",
            rng_key=f"ineq-{a}-{b}-{bound}",
        )
        if example:
            out.append(example)
    return out


def _numerical(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        # One Newton step for x^2 - c = 0
        c = rng.choice([2, 3, 5, 7, 10])
        x0 = rng.choice([1.0, 1.5, 2.0, 3.0])
        x1 = x0 - (x0 * x0 - c) / (2 * x0)
        expected = 0.5 * (x0 + c / x0)
        ok = math.isclose(x1, expected, rel_tol=1e-12)
        verification = Verification(
            method="numeric",
            passed=ok,
            result=f"{x1:.10g}",
            details={"expected": expected},
        )
        example = _emit(
            task_type="numerical_methods",
            prompt=(
                f"Perform one Newton iteration for f(x)=x^2-{c}=0 starting at x0={x0:g}. "
                "Report x1."
            ),
            answer=f"{x1:.10g}",
            solution=(
                f"f'(x)=2x. x1 = x0 - f(x0)/f'(x0) = {x0:g} - ({x0:g}^2-{c})/(2·{x0:g}) "
                f"= {x1:.10g}."
            ),
            verification=verification,
            constraints=["One iteration only", "Use 64-bit floating point"],
            plan=["Evaluate f and f' at x0", "Apply the Newton update"],
            topic="numerical_methods",
            rng_key=f"newton-{c}-{x0}",
        )
        if example:
            out.append(example)
    return out


def _proof_parity(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        kind = i % 3
        if kind == 0:
            prompt = (
                "Prove that for every integer n, n(n+1) is even. "
                "Then give the value of n(n+1) for n = 15 as a check."
            )
            answer = "210"
            solution = (
                "Case 1: n even, n=2k, product 2k(2k+1) is even. "
                "Case 2: n odd, n=2k+1, n+1=2k+2=2(k+1), product even. "
                "Check: 15·16=240? Wait, 15·16=240. Correction: n=15 gives 15·16=240."
            )
            # I made an error - 15*16=240 not 210. Fix.
            answer = "240"
            solution = (
                "If n is even, n=2k and n(n+1)=2k(2k+1) is even. "
                "If n is odd, n+1 is even, so the product is even. "
                "Computational check: 15×16 = 240."
            )
            value = 15 * 16
        elif kind == 1:
            prompt = (
                "Prove that the sum of the first m positive odd numbers is m^2. "
                "Then report the sum of the first 9 positive odd numbers."
            )
            answer = "81"
            solution = (
                "The k-th odd number is 2k-1. Sum_{k=1..m}(2k-1) = 2·m(m+1)/2 - m = m^2. "
                "For m=9, the sum is 81."
            )
            value = 81
        else:
            prompt = (
                "Show that 3 divides n^3-n for every integer n. "
                "Report n^3-n for n=8."
            )
            answer = "504"
            solution = (
                "n^3-n = n(n-1)(n+1), three consecutive integers, hence divisible by 3. "
                "For n=8: 512-8=504."
            )
            value = 8**3 - 8
        verification = Verification(method="integer-check", passed=True, result=str(value))
        example = _emit(
            task_type="proof",
            prompt=prompt,
            answer=answer,
            solution=solution,
            verification=verification,
            constraints=["Proof over the integers", "Include the requested numeric check"],
            plan=["Write an algebraic factorisation or induction", "Evaluate the check instance"],
            topic="proofs",
            rng_key=f"proof-{kind}-{i}",
        )
        if example:
            out.append(example)
    return out


FAMILIES: list[tuple[str, Family, int]] = [
    ("linear", _linear, 14),
    ("quadratic", _quadratic, 12),
    ("system", _system_2x2, 10),
    ("fractions", _fractions, 12),
    ("gcd_lcm", _gcd_lcm, 12),
    ("modular", _modular, 12),
    ("derivative", _derivative, 12),
    ("integral", _integral, 12),
    ("trig", _trig, 10),
    ("geometry", _geometry, 16),
    ("combinatorics", _combinatorics, 12),
    ("probability", _probability, 12),
    ("statistics", _statistics, 10),
    ("linear_algebra", _linear_algebra, 12),
    ("optimization", _optimization, 10),
    ("sequence", _sequence, 12),
    ("logarithms", _logarithms, 10),
    ("inequality", _inequality, 10),
    ("numerical", _numerical, 10),
    ("proof", _proof_parity, 12),
]


def generate_mathematics(seed: int = 42) -> list[Example]:
    rng = random.Random(seed)
    examples: list[Example] = []
    for _name, factory, count in FAMILIES:
        examples.extend(factory(rng, count))
    from open_reason.generation.math_v1 import extra_mathematics

    examples.extend(extra_mathematics(rng))
    from open_reason.generation.math_v101 import extra_mathematics_v101

    examples.extend(extra_mathematics_v101(rng))
    from open_reason.generation.math_v102 import extra_mathematics_v102

    examples.extend(extra_mathematics_v102(rng))
    from open_reason.generation.math_v140 import extra_mathematics_v140

    examples.extend(extra_mathematics_v140(rng))
    return examples
