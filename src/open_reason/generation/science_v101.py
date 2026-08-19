"""v1.0.1 science: interpretation, modeling, and new numeric families."""

from __future__ import annotations

import math
import random

from open_reason.generation.science import _emit
from open_reason.models import Example


def extra_science_v101(rng: random.Random) -> list[Example]:
    out: list[Example] = []
    out.extend(_pendulum(rng, 8))
    out.extend(_gravitation(rng, 8))
    out.extend(_molarity(rng, 8))
    out.extend(_snell(rng, 6))
    out.extend(_radioactive(rng, 8))
    out.extend(_punnett_ratio(rng, 8))
    out.extend(_heat_capacity(rng, 8))
    out.extend(_buoyancy(rng, 6))
    out.extend(_photon(rng, 6))
    out.extend(_dilution_c1v1(rng, 8))
    out.extend(_model_linear(rng, 6))
    out.extend(_interpret_slope(rng, 6))
    return out


def _pendulum(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    g = 10.0
    for _ in range(count):
        L = rng.choice([0.4, 0.9, 1.6, 2.5, 4.0])
        T = 2 * math.pi * math.sqrt(L / g)
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"A simple pendulum has length {L:g} m. Take g=10 m/s² and "
                "T=2π√(L/g). What is the period in seconds?"
            ),
            answer=f"{T:.10g}",
            solution=f"T=2π√({L:g}/10) = {T}.",
            expected=T,
            got=2 * math.pi * math.sqrt(L / g),
            constraints=["Small-angle pendulum", "g=10"],
            observations=[f"L={L:g} m"],
            plan=["Write T=2π√(L/g)", "Substitute"],
            key=f"pend-{L}",
        )
        if example:
            out.append(example)
    return out


def _gravitation(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    gconst = 6.67e-11
    for _ in range(count):
        m1 = rng.choice([2, 4, 5, 8]) * 1e5
        m2 = rng.choice([2, 3, 6]) * 1e5
        r = rng.choice([2, 4, 5]) * 1e2
        F = gconst * m1 * m2 / (r * r)
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"Two point masses {m1:g} kg and {m2:g} kg are {r:g} m apart. "
                "Using G=6.67e-11, what is the Newtonian force magnitude in newtons?"
            ),
            answer=f"{F:.10g}",
            solution=f"F=G m1 m2 / r^2 = {F}.",
            expected=F,
            got=gconst * m1 * m2 / (r * r),
            constraints=["Point masses", "SI"],
            observations=[f"m1={m1:g}", f"m2={m2:g}", f"r={r:g}"],
            plan=["Write Newton's gravity law", "Substitute"],
            key=f"grav-{m1}-{m2}-{r}",
            rel_tol=1e-6,
        )
        if example:
            out.append(example)
    return out


def _molarity(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        mol = rng.choice([0.25, 0.5, 1.0, 2.0])
        vol = rng.choice([0.25, 0.5, 1.0, 2.0])
        M = mol / vol
        example = _emit(
            task_type="calculation",
            field="chemistry",
            prompt=(
                f"{mol:g} mol of solute is dissolved to {vol:g} L of solution. "
                "What is the molarity in mol/L?"
            ),
            answer=f"{M:.10g}",
            solution=f"M = n/V = {mol:g}/{vol:g} = {M}.",
            expected=M,
            got=mol / vol,
            constraints=["Molarity is moles per litre of solution"],
            observations=[f"n={mol:g} mol", f"V={vol:g} L"],
            plan=["Divide moles by volume"],
            key=f"mol-{mol}-{vol}",
        )
        if example:
            out.append(example)
    return out


def _snell(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n1 = rng.choice([1.0, 1.33])
        n2 = rng.choice([1.5, 1.6])
        s1 = rng.choice([0.3, 0.4, 0.5])
        s2 = n1 * s1 / n2
        example = _emit(
            task_type="calculation",
            field="optics",
            prompt=(
                f"Snell's law: n1 sin θ1 = n2 sin θ2. n1={n1:g}, n2={n2:g}, "
                f"sin θ1={s1:g}. What is sin θ2?"
            ),
            answer=f"{s2:.10g}",
            solution=f"sin θ2 = n1 sin θ1 / n2 = {s2}.",
            expected=s2,
            got=n1 * s1 / n2,
            constraints=["Given sines, not angles"],
            observations=[f"n1={n1}", f"n2={n2}", f"sinθ1={s1}"],
            plan=["Solve Snell for sin θ2"],
            key=f"snell-{n1}-{n2}-{s1}",
        )
        if example:
            out.append(example)
    return out


def _radioactive(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n0 = rng.choice([80, 160, 320])
        halves = rng.choice([1, 2, 3, 4])
        remain = n0 / (2 ** halves)
        example = _emit(
            task_type="calculation",
            field="chemistry",
            prompt=(
                f"A sample starts at {n0} units. After {halves} half-lives, "
                "how many units remain (exponential decay, integer-power of two)?"
            ),
            answer=f"{remain:.10g}",
            solution=f"N = N0 / 2^h = {n0}/2^{halves} = {remain}.",
            expected=remain,
            got=n0 / (2 ** halves),
            constraints=["Exact half-lives", "No background"],
            observations=[f"N0={n0}", f"half-lives={halves}"],
            plan=["Divide by 2 once per half-life"],
            key=f"hl-{n0}-{halves}",
        )
        if example:
            out.append(example)
    return out


def _punnett_ratio(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        kind = rng.choice(["hetero_mono", "testcross"])
        if kind == "hetero_mono":
            # Aa x Aa -> 3:1 dominant phenotype
            num, den = 3, 4
            prompt = (
                "Aa × Aa, complete dominance. What is P(dominant phenotype) as a "
                "reduced fraction a/b? Report a/b."
            )
            answer = "3/4"
            got = 0.75
        else:
            num, den = 1, 2
            prompt = (
                "Aa × aa testcross, complete dominance. What is P(recessive phenotype) "
                "as a reduced fraction a/b? Report a/b."
            )
            answer = "1/2"
            got = 0.5
        example = _emit(
            task_type="calculation",
            field="biology",
            prompt=prompt,
            answer=answer,
            solution=f"{num}/{den} of the Punnett cells match.",
            expected=got,
            got=num / den,
            constraints=["Mendelian, independent, complete dominance"],
            observations=[kind],
            plan=["Draw Punnett", "Count matching genotypes"],
            key=f"punnett-{kind}-{i}",
        )
        if example:
            out.append(example)
    return out


def _heat_capacity(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        m = rng.choice([0.5, 1.0, 2.0])
        c = rng.choice([4180, 900, 387])
        dT = rng.choice([5, 10, 20])
        Q = m * c * dT
        example = _emit(
            task_type="calculation",
            field="thermodynamics",
            prompt=(
                f"Q=mcΔT. Mass {m:g} kg, c={c} J/(kg·K), ΔT={dT} K. What is Q in joules?"
            ),
            answer=f"{Q:.10g}",
            solution=f"Q={m:g}·{c}·{dT}={Q}.",
            expected=Q,
            got=m * c * dT,
            constraints=["No phase change"],
            observations=[f"m={m}", f"c={c}", f"dT={dT}"],
            plan=["Multiply m c ΔT"],
            key=f"q-{m}-{c}-{dT}",
        )
        if example:
            out.append(example)
    return out


def _buoyancy(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    rho = 1000
    g = 10
    for _ in range(count):
        V = rng.choice([0.002, 0.005, 0.01])
        F = rho * V * g
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"Archimedes: a fully submerged volume {V:g} m³ in freshwater "
                f"(ρ=1000 kg/m³), g=10 m/s². What is the buoyant force in newtons?"
            ),
            answer=f"{F:.10g}",
            solution=f"F=ρVg={rho}·{V:g}·{g}={F}.",
            expected=F,
            got=rho * V * g,
            constraints=["Fully submerged", "Fresh water"],
            observations=[f"V={V:g}"],
            plan=["Write F=ρVg"],
            key=f"buoy-{V}",
        )
        if example:
            out.append(example)
    return out


def _photon(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    h = 6.626e-34
    for _ in range(count):
        f = rng.choice([5e14, 6e14, 1e15])
        E = h * f
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"A photon has frequency {f:g} Hz. Using E=hf and h=6.626e-34 J·s, "
                "what is E in joules?"
            ),
            answer=f"{E:.10g}",
            solution=f"E=hf={h}·{f:g}={E}.",
            expected=E,
            got=h * f,
            constraints=["Single photon", "SI"],
            observations=[f"f={f:g}"],
            plan=["Multiply h by f"],
            key=f"phot-{f}",
            rel_tol=1e-6,
        )
        if example:
            out.append(example)
    return out


def _dilution_c1v1(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        c1 = rng.choice([2.0, 4.0, 6.0, 10.0])
        v1 = rng.choice([0.1, 0.2, 0.25])
        v2 = rng.choice([0.5, 1.0, 2.0])
        c2 = c1 * v1 / v2
        example = _emit(
            task_type="calculation",
            field="chemistry",
            prompt=(
                f"Dilute {v1:g} L of {c1:g} mol/L solution to {v2:g} L. "
                "What is the new concentration in mol/L (C1V1=C2V2)?"
            ),
            answer=f"{c2:.10g}",
            solution=f"C2=C1V1/V2={c1:g}·{v1:g}/{v2:g}={c2}.",
            expected=c2,
            got=c1 * v1 / v2,
            constraints=["Conservative solute", "Volumes additive as given"],
            observations=[f"C1={c1}", f"V1={v1}", f"V2={v2}"],
            plan=["Solve C1V1=C2V2 for C2"],
            key=f"dil-{c1}-{v1}-{v2}",
        )
        if example:
            out.append(example)
    return out


def _model_linear(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        m = rng.randint(2, 9)
        b = rng.randint(-4, 4)
        x = rng.randint(1, 8)
        y = m * x + b
        example = _emit(
            task_type="modeling",
            field="applied",
            prompt=(
                f"A calibrated sensor is modeled as y={m}x+{b}. If the reading x={x}, "
                "what is the modeled y?"
            ),
            answer=str(y),
            solution=f"y={m}·{x}+{b}={y}.",
            expected=float(y),
            got=float(m * x + b),
            constraints=["Linear calibration", "No noise term in this item"],
            observations=[f"m={m}", f"b={b}", f"x={x}"],
            plan=["Substitute into the affine model"],
            key=f"model-{m}-{b}-{x}-{i}",
        )
        if example:
            out.append(example)
    return out


def _interpret_slope(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        dx = rng.choice([2, 4, 5])
        dy = rng.choice([6, 8, 10, 12])
        slope = dy / dx
        example = _emit(
            task_type="interpretation",
            field="applied",
            prompt=(
                f"On a distance-time graph, distance rises {dy} m over {dx} s of "
                "straight-line motion. What is the constant speed in m/s?"
            ),
            answer=f"{slope:.10g}",
            solution=f"speed = Δs/Δt = {dy}/{dx} = {slope}.",
            expected=slope,
            got=dy / dx,
            constraints=["Straight line", "Speed is the slope"],
            observations=[f"dy={dy} m", f"dx={dx} s"],
            plan=["Divide rise by run"],
            key=f"slope-{dy}-{dx}-{i}",
        )
        if example:
            out.append(example)
    return out
