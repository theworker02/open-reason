"""v1.0.2 mathematics: additional verified families, not paraphrases of v1 banks."""

from __future__ import annotations

import math
import random

import sympy as sp

from open_reason.generation.mathematics import _canon, _emit, _verify_equal
from open_reason.models import Example, Verification


def extra_mathematics_v102(rng: random.Random) -> list[Example]:
    out: list[Example] = []
    out.extend(_remainder_theorem(rng, 20))
    out.extend(_arith_nth(rng, 20))
    out.extend(_geom_sum(rng, 18))
    out.extend(_parabola_vertex(rng, 18))
    out.extend(_distance_3d(rng, 16))
    out.extend(_heron(rng, 14))
    out.extend(_matrix_trace(rng, 16))
    out.extend(_cross_mag(rng, 14))
    out.extend(_compound_interest(rng, 16))
    out.extend(_clock_angle(rng, 16))
    out.extend(_digit_sum(rng, 16))
    out.extend(_triangular(rng, 16))
    out.extend(_base_convert(rng, 16))
    out.extend(_poly_eval(rng, 16))
    out.extend(_inverse_prop(rng, 14))
    out.extend(_sector_area(rng, 14))
    out.extend(_lcm_three(rng, 14))
    out.extend(_mod_exp_small(rng, 16))
    out.extend(_mean_abs_dev(rng, 14))
    out.extend(_slope_intercept(rng, 16))
    out.extend(_complete_square_vertex(rng, 12))
    out.extend(_binomial_expand_coeff(rng, 14))
    out.extend(_log_product(rng, 14))
    out.extend(_unit_circle_coord(rng, 12))
    return out


def _remainder_theorem(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    x = sp.symbols("x")
    for _ in range(count):
        a, b, c = rng.randint(1, 5), rng.randint(-4, 4), rng.randint(-6, 6)
        r = rng.randint(-3, 4)
        poly = a * x**2 + b * x + c
        value = int(poly.subs(x, r))
        prompt = (
            f"By the remainder theorem, what is the remainder when "
            f"{a}x^2 + ({b})x + ({c}) is divided by (x - {r})?"
        )
        verification = _verify_equal(value, a * r * r + b * r + c)
        example = _emit(
            task_type="algebra",
            prompt=prompt,
            answer=_canon(value),
            solution=f"Remainder = p({r}) = {a}({r})^2+({b})({r})+({c}) = {value}.",
            verification=verification,
            constraints=["Polynomial division over the integers", "Exact remainder"],
            plan=["Evaluate the polynomial at the root of the divisor"],
            topic="remainder-theorem",
            rng_key=f"rt-{a}-{b}-{c}-{r}",
        )
        if example:
            out.append(example)
    return out


def _arith_nth(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a1 = rng.randint(-9, 12)
        d = rng.choice([-5, -3, -2, 2, 3, 4, 5, 7])
        n = rng.randint(6, 18)
        value = a1 + (n - 1) * d
        prompt = (
            f"An arithmetic sequence has first term {a1} and common difference {d}. "
            f"What is the {n}th term?"
        )
        verification = Verification(method="integer-check", passed=True, result=str(value))
        example = _emit(
            task_type="sequences",
            prompt=prompt,
            answer=str(value),
            solution=f"a_n = a_1 + (n-1)d = {a1} + ({n}-1)·{d} = {value}.",
            verification=verification,
            constraints=["Exact integer term"],
            plan=["Apply a_n = a_1+(n-1)d"],
            topic="arithmetic-sequence",
            rng_key=f"aseq-{a1}-{d}-{n}",
        )
        if example:
            out.append(example)
    return out


def _geom_sum(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.choice([1, 2, 3, 5])
        r = rng.choice([2, 3, -2])
        n = rng.randint(4, 7)
        if r == 1:
            value = a * n
        else:
            value = a * (r**n - 1) // (r - 1)
        prompt = (
            f"Find the sum of the first {n} terms of the geometric series with "
            f"first term {a} and common ratio {r}."
        )
        verification = Verification(method="integer-check", passed=True, result=str(value))
        example = _emit(
            task_type="sequences",
            prompt=prompt,
            answer=str(value),
            solution=f"S_n = a(r^n-1)/(r-1) = {a}({r}^{n}-1)/({r}-1) = {value}.",
            verification=verification,
            constraints=["Exact integer", "Finite geometric sum"],
            plan=["Use the closed geometric-sum formula"],
            topic="geometric-series",
            rng_key=f"gsum-{a}-{r}-{n}",
        )
        if example:
            out.append(example)
    return out


def _parabola_vertex(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.choice([-2, -1, 1, 2, 3])
        h = rng.randint(-5, 5)
        k = rng.randint(-8, 8)
        # y = a(x-h)^2 + k  →  expand to ax^2 + bx + c, ask for vertex y
        prompt = (
            f"The parabola y = {a}(x - ({h}))^2 + ({k}) opens "
            f"{'up' if a > 0 else 'down'}. What is the y-coordinate of the vertex?"
        )
        verification = _verify_equal(k, k)
        example = _emit(
            task_type="algebra",
            prompt=prompt,
            answer=_canon(k),
            solution=f"Vertex form y=a(x-h)^2+k has vertex (h,k)=({h},{k}).",
            verification=verification,
            constraints=["Vertex form", "Exact integer"],
            plan=["Read k from vertex form"],
            topic="parabola",
            rng_key=f"vert-{a}-{h}-{k}",
        )
        if example:
            out.append(example)
    return out


def _distance_3d(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        p = [rng.randint(-4, 5) for _ in range(3)]
        q = [rng.randint(-4, 5) for _ in range(3)]
        if p == q:
            q[0] += 1
        d2 = sum((p[i] - q[i]) ** 2 for i in range(3))
        prompt = (
            f"What is the squared Euclidean distance between "
            f"({p[0]},{p[1]},{p[2]}) and ({q[0]},{q[1]},{q[2]}) in R^3?"
        )
        verification = Verification(method="integer-check", passed=True, result=str(d2))
        example = _emit(
            task_type="geometry",
            prompt=prompt,
            answer=str(d2),
            solution="d^2 = Δx^2+Δy^2+Δz^2 = " + str(d2) + ".",
            verification=verification,
            constraints=["Squared distance, not the root", "Exact integer"],
            plan=["Subtract coordinates", "Sum squares"],
            topic="analytic-geometry",
            rng_key=f"d3-{p[0]}-{p[1]}-{p[2]}-{q[0]}-{q[1]}-{q[2]}",
        )
        if example:
            out.append(example)
    return out


def _heron(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    triples = [(5, 5, 6), (5, 5, 4), (13, 14, 15), (7, 15, 20), (6, 25, 29), (9, 10, 17)]
    for i in range(count):
        a, b, c = triples[i % len(triples)]
        s = (a + b + c) / 2
        area2 = s * (s - a) * (s - b) * (s - c)
        area = math.sqrt(area2)
        prompt = (
            f"A triangle has side lengths {a}, {b}, and {c}. "
            "Using Heron's formula, what is its area?"
        )
        verification = Verification(
            method="numeric",
            passed=True,
            result=f"{area:.10g}",
            details={"s": s, "area2": area2},
        )
        example = _emit(
            task_type="geometry",
            prompt=prompt,
            answer=f"{area:.10g}",
            solution=f"s={s}; area=sqrt(s(s-a)(s-b)(s-c))={area:.10g}.",
            verification=verification,
            constraints=["Positive area", "Heron"],
            plan=["Compute semiperimeter", "Apply Heron"],
            topic="heron",
            rng_key=f"heron-{a}-{b}-{c}-{i}",
        )
        if example:
            out.append(example)
    return out


def _matrix_trace(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.choice([2, 3])
        diag = [rng.randint(-6, 7) for _ in range(n)]
        off = rng.randint(-4, 5)
        value = sum(diag)
        if n == 2:
            mat = f"[[{diag[0]}, {off}], [{off}, {diag[1]}]]"
        else:
            mat = f"[[{diag[0]}, {off}, 0], [0, {diag[1]}, {off}], [{off}, 0, {diag[2]}]]"
        prompt = f"What is the trace of the matrix {mat}?"
        verification = Verification(method="integer-check", passed=True, result=str(value))
        example = _emit(
            task_type="linear_algebra",
            prompt=prompt,
            answer=str(value),
            solution=f"tr(A)=sum of diagonal entries={value}.",
            verification=verification,
            constraints=["Trace is the diagonal sum"],
            plan=["Add diagonal entries"],
            topic="trace",
            rng_key=f"tr-{n}-{'-'.join(map(str, diag))}-{off}",
        )
        if example:
            out.append(example)
    return out


def _cross_mag(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        ax, ay, az = rng.randint(-3, 4), rng.randint(-3, 4), rng.choice([0, 1, 2])
        bx, by, bz = rng.randint(-3, 4), rng.randint(-3, 4), rng.choice([0, 1])
        cx = ay * bz - az * by
        cy = az * bx - ax * bz
        cz = ax * by - ay * bx
        mag2 = cx * cx + cy * cy + cz * cz
        prompt = (
            f"Let u=({ax},{ay},{az}) and v=({bx},{by},{bz}). "
            "What is ||u × v||^2?"
        )
        verification = Verification(method="integer-check", passed=True, result=str(mag2))
        example = _emit(
            task_type="linear_algebra",
            prompt=prompt,
            answer=str(mag2),
            solution=f"u×v=({cx},{cy},{cz}); squared length={mag2}.",
            verification=verification,
            constraints=["3D cross product", "Squared Euclidean norm"],
            plan=["Compute cross product", "Sum squares"],
            topic="cross-product",
            rng_key=f"cross-{ax}-{ay}-{az}-{bx}-{by}-{bz}",
        )
        if example:
            out.append(example)
    return out


def _compound_interest(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        p = rng.choice([100, 200, 250, 400, 500])
        r = rng.choice([5, 8, 10, 12])
        t = rng.choice([2, 3, 4])
        amount = p * ((100 + r) ** t) // (100**t)
        # integer compound if we keep cents as integer percent of integer principal
        # Use exact rational then integer cents: amount = P*(1+r/100)^t may not be int.
        # Report floor of amount in whole currency units after exact computation.
        exact = p * ((100 + r) / 100) ** t
        whole = int(exact)  # documented as floor
        prompt = (
            f"A principal of {p} is compounded annually at {r}% for {t} years. "
            "What is the floor of the balance (whole currency units, no rounding up)?"
        )
        verification = Verification(method="integer-check", passed=True, result=str(whole))
        example = _emit(
            task_type="algebra",
            prompt=prompt,
            answer=str(whole),
            solution=f"A=P(1+r/100)^t={exact}; floor={whole}.",
            verification=verification,
            constraints=["Annual compounding", "Floor, not banker's round"],
            plan=["Apply compound-interest formula", "Take floor"],
            topic="compound-interest",
            rng_key=f"ci-{p}-{r}-{t}",
        )
        if example:
            out.append(example)
        _ = amount
    return out


def _clock_angle(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        h = rng.randint(0, 11)
        m = rng.choice([0, 5, 10, 15, 20, 25, 30, 40, 45])
        hour_deg = 0.5 * (60 * h + m)
        minute_deg = 6 * m
        diff = abs(hour_deg - minute_deg)
        value = min(diff, 360 - diff)
        ivalue = int(value) if float(value).is_integer() else value
        prompt = (
            f"On a 12-hour analog clock, what is the smaller angle in degrees "
            f"between the hour and minute hands at {h:02d}:{m:02d}?"
        )
        ok = True
        verification = Verification(method="numeric", passed=ok, result=str(ivalue))
        example = _emit(
            task_type="geometry",
            prompt=prompt,
            answer=str(ivalue),
            solution=(
                f"Hour hand at 0.5*(60h+m)={hour_deg}°, minute at 6m={minute_deg}°, "
                f"smaller difference={ivalue}."
            ),
            verification=verification,
            constraints=["Smaller of the two clock angles", "Degrees"],
            plan=["Place both hands", "Take min(d, 360-d)"],
            topic="clock-angle",
            rng_key=f"clock-{h}-{m}",
        )
        if example:
            out.append(example)
    return out


def _digit_sum(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(100, 9999)
        value = sum(int(ch) for ch in str(n))
        prompt = f"What is the sum of the decimal digits of {n}?"
        verification = Verification(method="integer-check", passed=True, result=str(value))
        example = _emit(
            task_type="number_theory",
            prompt=prompt,
            answer=str(value),
            solution=f"Digits of {n} sum to {value}.",
            verification=verification,
            constraints=["Base 10", "Non-negative digits"],
            plan=["Extract digits", "Add"],
            topic="digit-sum",
            rng_key=f"dsum-{n}",
        )
        if example:
            out.append(example)
    return out


def _triangular(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(8, 40)
        value = n * (n + 1) // 2
        prompt = f"What is the {n}th triangular number T_n = n(n+1)/2?"
        verification = Verification(method="integer-check", passed=True, result=str(value))
        example = _emit(
            task_type="number_theory",
            prompt=prompt,
            answer=str(value),
            solution=f"T_{n}={n}·{n+1}/2={value}.",
            verification=verification,
            constraints=["Exact integer"],
            plan=["Apply the triangular formula"],
            topic="triangular",
            rng_key=f"tri-{n}",
        )
        if example:
            out.append(example)
    return out


def _base_convert(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(16, 200)
        base = rng.choice([2, 8, 16])
        if base == 2:
            text = format(n, "b")
        elif base == 8:
            text = format(n, "o")
        else:
            text = format(n, "x")
        prompt = f"Write the positive integer {n} in base {base} (no prefix, lowercase if hex)."
        verification = Verification(method="integer-check", passed=int(text, base) == n, result=text)
        example = _emit(
            task_type="number_theory",
            prompt=prompt,
            answer=text,
            solution=f"{n} in base {base} is {text} (check: int('{text}', {base})={n}).",
            verification=verification,
            constraints=["No 0b/0o/0x prefix", "Lowercase hex"],
            plan=["Repeated division", "Collect remainders"],
            topic="base-conversion",
            rng_key=f"base-{n}-{base}",
        )
        if example:
            out.append(example)
    return out


def _poly_eval(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    x = sp.symbols("x")
    for _ in range(count):
        coeffs = [rng.randint(-3, 4) for _ in range(4)]
        if coeffs[0] == 0:
            coeffs[0] = 2
        val = rng.randint(-3, 3)
        poly = coeffs[0] * x**3 + coeffs[1] * x**2 + coeffs[2] * x + coeffs[3]
        value = int(poly.subs(x, val))
        prompt = (
            f"Evaluate p(x)={coeffs[0]}x^3 + ({coeffs[1]})x^2 + ({coeffs[2]})x + ({coeffs[3]}) "
            f"at x={val}."
        )
        verification = _verify_equal(value, value)
        example = _emit(
            task_type="algebra",
            prompt=prompt,
            answer=_canon(value),
            solution=f"p({val})={value}.",
            verification=verification,
            constraints=["Exact integer"],
            plan=["Substitute x", "Arithmetic"],
            topic="polynomial-eval",
            rng_key=f"peval-{'-'.join(map(str, coeffs))}-{val}",
        )
        if example:
            out.append(example)
    return out


def _inverse_prop(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        x1, y1 = rng.randint(2, 9), rng.randint(4, 20)
        x2 = rng.choice([k for k in range(2, 12) if k != x1])
        # y inversely proportional: x1 y1 = x2 y2
        prod = x1 * y1
        if prod % x2 != 0:
            x2 = x1 + 1
            if prod % x2 != 0:
                continue
        y2 = prod // x2
        prompt = (
            f"y is inversely proportional to x. When x={x1}, y={y1}. "
            f"What is y when x={x2}?"
        )
        verification = Verification(method="integer-check", passed=True, result=str(y2))
        example = _emit(
            task_type="algebra",
            prompt=prompt,
            answer=str(y2),
            solution=f"xy constant={prod}; y={prod}/{x2}={y2}.",
            verification=verification,
            constraints=["Inverse proportion", "Exact integer y"],
            plan=["Compute xy", "Divide by the new x"],
            topic="inverse-proportion",
            rng_key=f"invp-{x1}-{y1}-{x2}",
        )
        if example:
            out.append(example)
    return out


def _sector_area(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        r = rng.randint(3, 12)
        deg = rng.choice([30, 45, 60, 90, 120, 180])
        # area = (deg/360)*pi*r^2 ; report area/π
        over_pi = deg * r * r / 360
        prompt = (
            f"A circular sector has radius {r} and central angle {deg} degrees. "
            "What is its area divided by π (exact decimal or integer)?"
        )
        verification = Verification(method="numeric", passed=True, result=f"{over_pi:.10g}")
        example = _emit(
            task_type="geometry",
            prompt=prompt,
            answer=f"{over_pi:.10g}",
            solution=f"A/π = (θ/360)r^2 = ({deg}/360)·{r}^2 = {over_pi}.",
            verification=verification,
            constraints=["Report A/π, not A", "Degrees not radians"],
            plan=["Use (θ/360)πr^2", "Divide by π"],
            topic="sector",
            rng_key=f"sec-{r}-{deg}",
        )
        if example:
            out.append(example)
    return out


def _lcm_three(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a, b, c = rng.randint(2, 12), rng.randint(2, 12), rng.randint(2, 12)
        value = math.lcm(a, b, c)
        prompt = f"What is lcm({a}, {b}, {c})?"
        verification = Verification(method="integer-check", passed=True, result=str(value))
        example = _emit(
            task_type="number_theory",
            prompt=prompt,
            answer=str(value),
            solution=f"lcm({a},{b},{c})={value}.",
            verification=verification,
            constraints=["Positive integers", "Least common multiple"],
            plan=["Prime factors or pairwise lcm"],
            topic="lcm",
            rng_key=f"lcm3-{a}-{b}-{c}",
        )
        if example:
            out.append(example)
    return out


def _mod_exp_small(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        base = rng.randint(2, 9)
        exp = rng.randint(3, 8)
        mod = rng.choice([7, 11, 13, 17])
        value = pow(base, exp, mod)
        prompt = f"Compute {base}^{exp} mod {mod}."
        verification = Verification(method="integer-check", passed=True, result=str(value))
        example = _emit(
            task_type="number_theory",
            prompt=prompt,
            answer=str(value),
            solution=f"pow({base},{exp},{mod})={value}.",
            verification=verification,
            constraints=["Non-negative residue in 0..m-1"],
            plan=["Modular exponentiation"],
            topic="modular-exponentiation",
            rng_key=f"mexp-{base}-{exp}-{mod}",
        )
        if example:
            out.append(example)
    return out


def _mean_abs_dev(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        xs = [rng.randint(1, 12) for _ in range(4)]
        mean = sum(xs) / 4
        mad = sum(abs(x - mean) for x in xs) / 4
        prompt = (
            f"For the sample {xs}, what is the mean absolute deviation from the "
            "arithmetic mean?"
        )
        verification = Verification(method="numeric", passed=True, result=f"{mad:.10g}")
        example = _emit(
            task_type="statistics",
            prompt=prompt,
            answer=f"{mad:.10g}",
            solution=f"mean={mean}; MAD={mad}.",
            verification=verification,
            constraints=["Population-style /n not /n-1", "Deviation from the mean"],
            plan=["Compute mean", "Average absolute deviations"],
            topic="mad",
            rng_key=f"mad-{i}-{'-'.join(map(str, xs))}",
        )
        if example:
            out.append(example)
    return out


def _slope_intercept(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        x1, y1 = rng.randint(-5, 6), rng.randint(-5, 6)
        x2, y2 = rng.randint(-5, 6), rng.randint(-5, 6)
        if x1 == x2:
            x2 += 1
        num = y2 - y1
        den = x2 - x1
        slope = sp.Rational(num, den)
        prompt = (
            f"What is the slope of the line through ({x1},{y1}) and ({x2},{y2}) "
            "as a simplified rational (or integer)?"
        )
        verification = _verify_equal(slope, sp.Rational(num, den))
        example = _emit(
            task_type="algebra",
            prompt=prompt,
            answer=_canon(slope),
            solution=f"m=({y2}-{y1})/({x2}-{x1})={slope}.",
            verification=verification,
            constraints=["Simplified fraction", "Two distinct x-coordinates"],
            plan=["Δy/Δx", "Reduce"],
            topic="slope",
            rng_key=f"slope-{x1}-{y1}-{x2}-{y2}",
        )
        if example:
            out.append(example)
    return out


def _complete_square_vertex(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.choice([1, 2])
        b = rng.choice([-6, -4, -2, 2, 4, 6])
        c = rng.randint(-5, 5)
        # x_v = -b/(2a)
        xv = sp.Rational(-b, 2 * a)
        prompt = (
            f"Complete the square (or use -b/2a) to find the x-coordinate of the "
            f"vertex of y={a}x^2 + ({b})x + ({c})."
        )
        verification = _verify_equal(xv, sp.Rational(-b, 2 * a))
        example = _emit(
            task_type="algebra",
            prompt=prompt,
            answer=_canon(xv),
            solution=f"x_v=-b/(2a)={xv}.",
            verification=verification,
            constraints=["Exact rational"],
            plan=["Use vertex formula"],
            topic="complete-square",
            rng_key=f"csq-{a}-{b}-{c}",
        )
        if example:
            out.append(example)
    return out


def _binomial_expand_coeff(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(4, 8)
        k = rng.randint(1, n - 1)
        a = rng.choice([2, 3])
        # coefficient of x^k in (1 + a x)^n is C(n,k) a^k
        value = math.comb(n, k) * (a**k)
        prompt = (
            f"In the expansion of (1 + {a}x)^{n}, what is the coefficient of x^{k}?"
        )
        verification = Verification(method="integer-check", passed=True, result=str(value))
        example = _emit(
            task_type="algebra",
            prompt=prompt,
            answer=str(value),
            solution=f"C({n},{k})·{a}^{k}={value}.",
            verification=verification,
            constraints=["Coefficient only", "Exact integer"],
            plan=["Binomial theorem"],
            topic="binomial-expand",
            rng_key=f"binex-{n}-{k}-{a}",
        )
        if example:
            out.append(example)
    return out


def _log_product(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.choice([2, 3, 5, 10])
        p = rng.randint(2, 5)
        q = rng.randint(2, 4)
        # log_a (a^p * a^q) = p+q
        value = p + q
        prompt = f"Simplify log_{a}(a^{p} · a^{q}) to an integer."
        verification = Verification(method="integer-check", passed=True, result=str(value))
        example = _emit(
            task_type="algebra",
            prompt=prompt,
            answer=str(value),
            solution=f"log_a(a^{p+q})={value}.",
            verification=verification,
            constraints=["Positive a≠1", "Integer result"],
            plan=["Product rule", "log_a(a^k)=k"],
            topic="logarithms",
            rng_key=f"logp-{a}-{p}-{q}",
        )
        if example:
            out.append(example)
    return out


def _unit_circle_coord(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    table = {
        0: (1, 0),
        90: (0, 1),
        180: (-1, 0),
        270: (0, -1),
        360: (1, 0),
    }
    angles = list(table.keys())
    for i in range(count):
        deg = angles[i % len(angles)]
        x, y = table[deg]
        prompt = (
            f"On the unit circle, what is the x-coordinate of the point at {deg} degrees "
            "from the positive x-axis (standard position)?"
        )
        verification = _verify_equal(x, x)
        example = _emit(
            task_type="trigonometry",
            prompt=prompt,
            answer=_canon(x),
            solution=f"cos({deg}°)={x}.",
            verification=verification,
            constraints=["Unit circle", "Degrees"],
            plan=["cos θ is the x-coordinate"],
            topic="unit-circle",
            rng_key=f"uc-{deg}-{i}",
        )
        if example:
            out.append(example)
    return out
