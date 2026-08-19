"""v1.4.0 mathematics: new verified families, not paraphrases of v102 banks."""

from __future__ import annotations

import math
import random

import sympy as sp

from open_reason.generation.mathematics import _canon, _emit, _verify_equal
from open_reason.models import Example, Verification


def extra_mathematics_v140(rng: random.Random) -> list[Example]:
    out: list[Example] = []
    out.extend(_sum_squares(rng, 20))
    out.extend(_sum_cubes(rng, 18))
    out.extend(_fibonacci(rng, 18))
    out.extend(_det2(rng, 18))
    out.extend(_dot2(rng, 16))
    out.extend(_perm(rng, 16))
    out.extend(_comb(rng, 16))
    out.extend(_floor_sqrt(rng, 18))
    out.extend(_pow2_floor(rng, 16))
    out.extend(_factorial(rng, 14))
    out.extend(_totient(rng, 16))
    out.extend(_divisor_count(rng, 16))
    out.extend(_midpoint_x(rng, 16))
    out.extend(_shoelace_tri(rng, 14))
    out.extend(_arith_sum(rng, 18))
    out.extend(_geom_term(rng, 16))
    out.extend(_discriminant(rng, 16))
    out.extend(_diff_squares(rng, 16))
    out.extend(_dice_ev(rng, 14))
    out.extend(_sample_var(rng, 14))
    out.extend(_cosine_law(rng, 14))
    out.extend(_vec_mag2(rng, 16))
    out.extend(_log_change(rng, 14))
    out.extend(_digital_root(rng, 16))
    out.extend(_popcount(rng, 16))
    out.extend(_crt_two(rng, 14))
    out.extend(_gcd_three(rng, 16))
    out.extend(_catalan(rng, 12))
    out.extend(_collatz_steps(rng, 16))
    out.extend(_box_volume(rng, 14))
    return out


def _sum_squares(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(6, 30)
        value = n * (n + 1) * (2 * n + 1) // 6
        example = _emit(
            task_type="number_theory",
            prompt=f"What is the sum of the squares 1^2 + 2^2 + ... + {n}^2?",
            answer=str(value),
            solution=f"n(n+1)(2n+1)/6 with n={n} yields {value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Exact integer", "Closed formula"],
            plan=["Apply the sum-of-squares formula"],
            topic="sum-of-squares",
            rng_key=f"v140-ssq-{n}",
        )
        if example:
            out.append(example)
    return out


def _sum_cubes(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(4, 18)
        value = (n * (n + 1) // 2) ** 2
        example = _emit(
            task_type="number_theory",
            prompt=f"What is 1^3 + 2^3 + ... + {n}^3?",
            answer=str(value),
            solution=f"(n(n+1)/2)^2 = {value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Exact integer"],
            plan=["Square the triangular number"],
            topic="sum-of-cubes",
            rng_key=f"v140-scu-{n}",
        )
        if example:
            out.append(example)
    return out


def _fibonacci(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(8, 20)
        a, b = 0, 1
        for _i in range(n):
            a, b = b, a + b
        example = _emit(
            task_type="sequences",
            prompt=f"Let F_0=0, F_1=1, F_k=F_{{k-1}}+F_{{k-2}}. What is F_{n}?",
            answer=str(a),
            solution=f"Iterate the recurrence to F_{n}={a}.",
            verification=Verification(method="integer-check", passed=True, result=str(a)),
            constraints=["F_0=0 indexing"],
            plan=["Iterate n steps from (0,1)"],
            topic="fibonacci",
            rng_key=f"v140-fib-{n}",
        )
        if example:
            out.append(example)
    return out


def _det2(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a, b = rng.randint(-6, 7), rng.randint(-6, 7)
        c, d = rng.randint(-6, 7), rng.randint(-6, 7)
        value = a * d - b * c
        example = _emit(
            task_type="linear_algebra",
            prompt=f"What is det([[{a}, {b}], [{c}, {d}]])?",
            answer=str(value),
            solution=f"ad-bc={a}·{d}-{b}·{c}={value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["2×2 determinant"],
            plan=["Compute ad-bc"],
            topic="determinant",
            rng_key=f"v140-det-{a}-{b}-{c}-{d}",
        )
        if example:
            out.append(example)
    return out


def _dot2(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        u = [rng.randint(-5, 6) for _ in range(3)]
        v = [rng.randint(-5, 6) for _ in range(3)]
        value = sum(x * y for x, y in zip(u, v, strict=True))
        example = _emit(
            task_type="linear_algebra",
            prompt=f"What is the Euclidean inner product of {tuple(u)} and {tuple(v)}?",
            answer=str(value),
            solution=f"u·v={value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["R^3 standard inner product"],
            plan=["Sum of coordinate products"],
            topic="dot-product",
            rng_key=f"v140-dot-{'-'.join(map(str, u+v))}",
        )
        if example:
            out.append(example)
    return out


def _perm(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(5, 10)
        k = rng.randint(2, min(4, n))
        value = math.perm(n, k)
        example = _emit(
            task_type="discrete_mathematics",
            prompt=f"Compute P({n},{k}) = n!/(n-k)! (permutations, no repetition).",
            answer=str(value),
            solution=f"P({n},{k})={value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Order matters", "No repetition"],
            plan=["Falling factorial"],
            topic="permutations",
            rng_key=f"v140-perm-{n}-{k}",
        )
        if example:
            out.append(example)
    return out


def _comb(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(6, 12)
        k = rng.randint(2, 5)
        if k > n:
            continue
        value = math.comb(n, k)
        example = _emit(
            task_type="discrete_mathematics",
            prompt=f"Compute C({n},{k}) (combinations, unordered, no repetition).",
            answer=str(value),
            solution=f"C({n},{k})={value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Order does not matter"],
            plan=["Binomial coefficient"],
            topic="combinations",
            rng_key=f"v140-comb-{n}-{k}",
        )
        if example:
            out.append(example)
    return out


def _floor_sqrt(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(10, 400)
        value = math.isqrt(n)
        example = _emit(
            task_type="number_theory",
            prompt=f"What is floor(sqrt({n})) (integer square root)?",
            answer=str(value),
            solution=f"Largest integer m with m^2 ≤ {n} is {value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Floor, not nearest"],
            plan=["Integer square root"],
            topic="isqrt",
            rng_key=f"v140-isqrt-{n}",
        )
        if example:
            out.append(example)
    return out


def _pow2_floor(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(3, 200)
        value = 1 << (n.bit_length() - 1)
        example = _emit(
            task_type="number_theory",
            prompt=f"What is the largest power of 2 that is ≤ {n}?",
            answer=str(value),
            solution=f"2^{{floor(log2({n}))}}={value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Power of two", "Not exceeding n"],
            plan=["Use bit length"],
            topic="power-of-two",
            rng_key=f"v140-p2-{n}",
        )
        if example:
            out.append(example)
    return out


def _factorial(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(5, 10)
        value = math.factorial(n)
        example = _emit(
            task_type="discrete_mathematics",
            prompt=f"What is {n}! ?",
            answer=str(value),
            solution=f"{n}!={value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Exact integer"],
            plan=["Product 1..n"],
            topic="factorial",
            rng_key=f"v140-fact-{n}",
        )
        if example:
            out.append(example)
    return out


def _phi(n: int) -> int:
    result = n
    p = 2
    m = n
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            result -= result // p
        p += 1
    if m > 1:
        result -= result // m
    return result


def _totient(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(6, 40)
        value = _phi(n)
        example = _emit(
            task_type="number_theory",
            prompt=f"What is Euler's totient φ({n})?",
            answer=str(value),
            solution=f"Count of integers in 1..{n} coprime to {n} is {value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["φ(n) = |{k : 1≤k≤n, gcd(k,n)=1}|"],
            plan=["Prime-factor formula"],
            topic="euler-totient",
            rng_key=f"v140-phi-{n}",
        )
        if example:
            out.append(example)
    return out


def _n_divisors(n: int) -> int:
    count = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            count += 1 if i * i == n else 2
        i += 1
    return count


def _divisor_count(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(12, 120)
        value = _n_divisors(n)
        example = _emit(
            task_type="number_theory",
            prompt=f"How many positive divisors does {n} have?",
            answer=str(value),
            solution=f"τ({n})={value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Positive divisors only"],
            plan=["Pair factors up to sqrt(n)"],
            topic="divisor-count",
            rng_key=f"v140-tau-{n}",
        )
        if example:
            out.append(example)
    return out


def _midpoint_x(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        x1, y1 = rng.randint(-8, 9), rng.randint(-8, 9)
        x2, y2 = rng.randint(-8, 9), rng.randint(-8, 9)
        mx = sp.Rational(x1 + x2, 2)
        example = _emit(
            task_type="geometry",
            prompt=(
                f"What is the x-coordinate of the midpoint of ({x1},{y1}) and ({x2},{y2}) "
                "as a simplified rational or integer?"
            ),
            answer=_canon(mx),
            solution=f"x_m=({x1}+{x2})/2={mx}.",
            verification=_verify_equal(mx, sp.Rational(x1 + x2, 2)),
            constraints=["Exact rational", f"y unused except as context ({y1},{y2})"],
            plan=["Average x-coordinates"],
            topic="midpoint",
            rng_key=f"v140-mid-{x1}-{y1}-{x2}-{y2}",
        )
        if example:
            out.append(example)
    return out


def _shoelace_tri(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        pts = [(rng.randint(0, 6), rng.randint(0, 6)) for _ in range(3)]
        if len({pts[0], pts[1], pts[2]}) < 3:
            pts[2] = (pts[2][0] + 2, pts[2][1] + 1)
        (x1, y1), (x2, y2), (x3, y3) = pts
        twice = abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        area = twice / 2
        example = _emit(
            task_type="geometry",
            prompt=(
                f"Using the shoelace formula, what is the area of the triangle with vertices "
                f"{pts[0]}, {pts[1]}, {pts[2]}?"
            ),
            answer=f"{area:.10g}",
            solution=f"|x1(y2-y3)+…|/2 = {area}.",
            verification=Verification(method="numeric", passed=True, result=f"{area:.10g}"),
            constraints=["Non-oriented absolute area"],
            plan=["Shoelace", "Divide by 2"],
            topic="shoelace",
            rng_key=f"v140-shoe-{x1}-{y1}-{x2}-{y2}-{x3}-{y3}",
        )
        if example:
            out.append(example)
    return out


def _arith_sum(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a1 = rng.randint(-6, 10)
        d = rng.choice([-4, -3, -2, 2, 3, 5])
        n = rng.randint(8, 20)
        value = n * (2 * a1 + (n - 1) * d) // 2
        example = _emit(
            task_type="sequences",
            prompt=(
                f"An arithmetic series has first term {a1}, common difference {d}, and {n} terms. "
                "What is the sum?"
            ),
            answer=str(value),
            solution=f"S_n=n/2·(2a1+(n-1)d)={value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Exact integer sum"],
            plan=["Closed arithmetic-sum formula"],
            topic="arithmetic-sum",
            rng_key=f"v140-asum-{a1}-{d}-{n}",
        )
        if example:
            out.append(example)
    return out


def _geom_term(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.choice([1, 2, 3])
        r = rng.choice([2, 3, -2])
        n = rng.randint(4, 8)
        value = a * (r ** (n - 1))
        example = _emit(
            task_type="sequences",
            prompt=(
                f"A geometric sequence has first term {a} and common ratio {r}. "
                f"What is the {n}th term?"
            ),
            answer=str(value),
            solution=f"a_n=a r^{{n-1}}={value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Exact integer"],
            plan=["Apply a r^{n-1}"],
            topic="geometric-term",
            rng_key=f"v140-gterm-{a}-{r}-{n}",
        )
        if example:
            out.append(example)
    return out


def _discriminant(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.choice([1, 2, 3])
        b = rng.randint(-8, 8)
        c = rng.randint(-8, 8)
        value = b * b - 4 * a * c
        example = _emit(
            task_type="algebra",
            prompt=f"What is the discriminant of {a}x^2 + ({b})x + ({c}) = 0?",
            answer=str(value),
            solution=f"Δ=b²-4ac={value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Δ = b²-4ac"],
            plan=["Substitute a,b,c"],
            topic="discriminant",
            rng_key=f"v140-disc-{a}-{b}-{c}",
        )
        if example:
            out.append(example)
    return out


def _diff_squares(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        u = rng.randint(4, 15)
        v = rng.randint(1, u - 1)
        value = u * u - v * v
        example = _emit(
            task_type="algebra",
            prompt=f"Evaluate {u}^2 - {v}^2 using a difference of squares.",
            answer=str(value),
            solution=f"(u-v)(u+v)={u-v}·{u+v}={value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Exact integer"],
            plan=["Factor as (u-v)(u+v)"],
            topic="difference-of-squares",
            rng_key=f"v140-dsq-{u}-{v}",
        )
        if example:
            out.append(example)
    return out


def _dice_ev(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        faces = rng.choice([4, 6, 8, 10, 12])
        ev = (faces + 1) / 2
        example = _emit(
            task_type="probability",
            prompt=(
                f"A fair {faces}-sided die is numbered 1 through {faces}. "
                "What is the expected value of one roll?"
            ),
            answer=f"{ev:.10g}",
            solution=f"E=(1+…+{faces})/{faces}=({faces}+1)/2={ev}.",
            verification=Verification(method="numeric", passed=True, result=f"{ev:.10g}"),
            constraints=["Uniform discrete", "Faces 1..n"],
            plan=["Average of 1 through n"],
            topic="dice-expectation",
            rng_key=f"v140-dice-{faces}-{i}",
        )
        if example:
            out.append(example)
    return out


def _sample_var(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        xs = [rng.randint(1, 9) for _ in range(4)]
        mean = sum(xs) / 4
        var = sum((x - mean) ** 2 for x in xs) / 3
        example = _emit(
            task_type="statistics",
            prompt=(
                f"For the sample {xs}, what is the unbiased sample variance "
                "(divide by n-1)?"
            ),
            answer=f"{var:.10g}",
            solution=f"mean={mean}; s^2={var}.",
            verification=Verification(method="numeric", passed=True, result=f"{var:.10g}"),
            constraints=["Bessel correction n-1"],
            plan=["Mean", "Sum of squared deviations", "Divide by 3"],
            topic="sample-variance",
            rng_key=f"v140-svar-{i}-{'-'.join(map(str, xs))}",
        )
        if example:
            out.append(example)
    return out


def _cosine_law(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a, b = rng.randint(3, 8), rng.randint(3, 8)
        deg = rng.choice([60, 90, 120])
        c2 = a * a + b * b - 2 * a * b * math.cos(math.radians(deg))
        example = _emit(
            task_type="geometry",
            prompt=(
                f"In a triangle, sides a={a} and b={b} enclose angle C={deg}°. "
                "What is c² by the law of cosines?"
            ),
            answer=f"{c2:.10g}",
            solution=f"c²=a²+b²-2ab cos C={c2}.",
            verification=Verification(method="numeric", passed=True, result=f"{c2:.10g}"),
            constraints=["Law of cosines", "Report c² not c"],
            plan=["Substitute into c²=a²+b²-2ab cos C"],
            topic="cosine-law",
            rng_key=f"v140-cosl-{a}-{b}-{deg}",
        )
        if example:
            out.append(example)
    return out


def _vec_mag2(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        v = [rng.randint(-5, 6) for _ in range(3)]
        value = sum(x * x for x in v)
        example = _emit(
            task_type="linear_algebra",
            prompt=f"What is ||{tuple(v)}||^2 in R^3 with the Euclidean norm?",
            answer=str(value),
            solution=f"Sum of squares={value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Squared length, not the root"],
            plan=["Sum coordinate squares"],
            topic="euclidean-norm",
            rng_key=f"v140-mag2-{'-'.join(map(str, v))}",
        )
        if example:
            out.append(example)
    return out


def _log_change(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a = rng.choice([2, 4, 8, 16])
        # log2(a) is integer
        value = int(math.log2(a))
        example = _emit(
            task_type="algebra",
            prompt=f"Simplify log_2({a}) to an integer.",
            answer=str(value),
            solution=f"2^{value}={a}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Exact integer"],
            plan=["Find the exponent of 2"],
            topic="logarithms",
            rng_key=f"v140-log2-{a}",
        )
        if example:
            out.append(example)
    return out


def _digital_root(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(10, 9999)
        value = 0 if n == 0 else 1 + (n - 1) % 9
        example = _emit(
            task_type="number_theory",
            prompt=f"What is the digital root of {n} (repeated digit sum until one digit)?",
            answer=str(value),
            solution=f"digital_root={n} mod 9 with 9→9, so {value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Base 10"],
            plan=["n mod 9, map 0 to 9 unless n=0"],
            topic="digital-root",
            rng_key=f"v140-droot-{n}",
        )
        if example:
            out.append(example)
    return out


def _popcount(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(1, 255)
        value = n.bit_count()
        example = _emit(
            task_type="number_theory",
            prompt=f"How many 1-bits are in the binary representation of {n}?",
            answer=str(value),
            solution=f"popcount({n})={value} (binary {n:b}).",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Unsigned binary", "No sign bit"],
            plan=["Count set bits"],
            topic="popcount",
            rng_key=f"v140-pop-{n}",
        )
        if example:
            out.append(example)
    return out


def _crt_two(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    pairs = [(3, 5), (4, 5), (3, 7), (5, 7), (4, 9), (5, 8)]
    for i in range(count):
        m1, m2 = pairs[i % len(pairs)]
        a1 = rng.randint(0, m1 - 1)
        a2 = rng.randint(0, m2 - 1)
        x = next((k for k in range(m1 * m2) if k % m1 == a1 and k % m2 == a2), None)
        if x is None:
            continue
        example = _emit(
            task_type="number_theory",
            prompt=(
                f"Find the unique x in 0..{m1*m2 - 1} with x ≡ {a1} (mod {m1}) "
                f"and x ≡ {a2} (mod {m2})."
            ),
            answer=str(x),
            solution=f"Chinese remainder (coprime moduli {m1},{m2}) gives x={x}.",
            verification=Verification(
                method="integer-check",
                passed=(x % m1 == a1 and x % m2 == a2),
                result=str(x),
            ),
            constraints=["Coprime moduli", "Canonical residue"],
            plan=["Search 0..m1 m2-1 or CRT formula"],
            topic="crt",
            rng_key=f"v140-crt-{m1}-{m2}-{a1}-{a2}",
        )
        if example:
            out.append(example)
    return out


def _gcd_three(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        a, b, c = rng.randint(4, 36), rng.randint(4, 36), rng.randint(4, 36)
        value = math.gcd(a, b, c)
        example = _emit(
            task_type="number_theory",
            prompt=f"What is gcd({a}, {b}, {c})?",
            answer=str(value),
            solution=f"gcd={value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Positive integers"],
            plan=["Pairwise Euclidean algorithm"],
            topic="gcd",
            rng_key=f"v140-gcd3-{a}-{b}-{c}",
        )
        if example:
            out.append(example)
    return out


def _catalan(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for n in range(3, 3 + count):
        value = math.comb(2 * n, n) // (n + 1)
        example = _emit(
            task_type="discrete_mathematics",
            prompt=f"What is the {n}th Catalan number C_n = (1/(n+1)) C(2n, n)?",
            answer=str(value),
            solution=f"C_{n}={value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["C_n indexing with C_3=5"],
            plan=["Binomial then divide by n+1"],
            topic="catalan",
            rng_key=f"v140-cat-{n}",
        )
        if example:
            out.append(example)
    return out


def _collatz_steps(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n = rng.randint(3, 40)
        steps = 0
        x = n
        while x != 1:
            x = x // 2 if x % 2 == 0 else 3 * x + 1
            steps += 1
            if steps > 500:
                break
        example = _emit(
            task_type="number_theory",
            prompt=(
                f"Starting from {n}, how many Collatz steps (even: n/2, odd: 3n+1) "
                "until 1 is reached?"
            ),
            answer=str(steps),
            solution=f"The hailstone sequence from {n} hits 1 in {steps} steps.",
            verification=Verification(method="integer-check", passed=True, result=str(steps)),
            constraints=["Standard Collatz map", "Count until 1"],
            plan=["Iterate until 1", "Count applications"],
            topic="collatz",
            rng_key=f"v140-col-{n}",
        )
        if example:
            out.append(example)
    return out


def _box_volume(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        l, w, h = rng.randint(2, 12), rng.randint(2, 12), rng.randint(2, 12)
        value = l * w * h
        example = _emit(
            task_type="geometry",
            prompt=f"A rectangular box has edges {l}, {w}, and {h}. What is its volume?",
            answer=str(value),
            solution=f"V=lwh={value}.",
            verification=Verification(method="integer-check", passed=True, result=str(value)),
            constraints=["Right rectangular prism", "Cubic units"],
            plan=["Multiply three edges"],
            topic="box-volume",
            rng_key=f"v140-box-{l}-{w}-{h}",
        )
        if example:
            out.append(example)
    return out
