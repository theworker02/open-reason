"""v1.0.2 science: extra numeric families with independent checks."""

from __future__ import annotations

import math
import random

from open_reason.generation.science import _emit
from open_reason.models import Example


def extra_science_v102(rng: random.Random) -> list[Example]:
    out: list[Example] = []
    out.extend(_centripetal(rng, 18))
    out.extend(_coulomb(rng, 14))
    out.extend(_photon(rng, 14))
    out.extend(_escape(rng, 12))
    out.extend(_beer_lambert(rng, 12))
    out.extend(_capacitance(rng, 12))
    out.extend(_latent_heat(rng, 14))
    out.extend(_kepler_period(rng, 12))
    out.extend(_work_force(rng, 16))
    out.extend(_molality(rng, 12))
    out.extend(_snell_angle(rng, 12))
    out.extend(_radio_intensity(rng, 12))
    return out


def _centripetal(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        m = rng.randint(1, 8)
        v = rng.randint(2, 12)
        r = rng.randint(1, 6)
        f = m * v * v / r
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"A mass of {m} kg moves in a horizontal circle of radius {r} m "
                f"at {v} m/s. What is the centripetal force in newtons?"
            ),
            answer=f"{f:.10g}",
            solution=f"F = mv²/r = {m}·{v}²/{r} = {f}.",
            expected=f,
            got=m * v * v / r,
            constraints=["Uniform circular motion", "SI units"],
            observations=[f"m={m} kg", f"v={v} m/s", f"r={r} m"],
            plan=["Apply F=mv²/r"],
            key=f"cent-{m}-{v}-{r}",
        )
        if example:
            out.append(example)
    return out


def _coulomb(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    k = 9.0e9
    for _ in range(count):
        q1 = rng.choice([1, 2, 3]) * 1e-6
        q2 = rng.choice([1, 2, 4]) * 1e-6
        r = rng.choice([0.1, 0.2, 0.5, 1.0])
        f = k * abs(q1 * q2) / (r * r)
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"Two point charges {q1:.0e} C and {q2:.0e} C are {r} m apart in vacuum. "
                "Magnitude of the Coulomb force in newtons? Use k=9.0e9."
            ),
            answer=f"{f:.10g}",
            solution=f"F=k|q1 q2|/r² = 9e9·{abs(q1*q2)}/{r*r} = {f}.",
            expected=f,
            got=k * abs(q1 * q2) / (r * r),
            constraints=["Coulomb's law", "Vacuum", "k=9.0e9"],
            observations=[f"q1={q1}", f"q2={q2}", f"r={r}"],
            plan=["Substitute into Coulomb's law"],
            key=f"coul-{q1}-{q2}-{r}",
            rel_tol=1e-6,
        )
        if example:
            out.append(example)
    return out


def _photon(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    h = 6.62607015e-34
    for _ in range(count):
        freq = rng.choice([5e14, 6e14, 7e14, 1e15])
        e = h * freq
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"A photon has frequency {freq:.0e} Hz. What is its energy in joules? "
                "Use h=6.62607015e-34 J·s."
            ),
            answer=f"{e:.10g}",
            solution=f"E=hf={h}·{freq}={e}.",
            expected=e,
            got=h * freq,
            constraints=["E=hf", "SI"],
            observations=[f"f={freq} Hz"],
            plan=["Multiply Planck's constant by frequency"],
            key=f"ph-{freq}",
        )
        if example:
            out.append(example)
    return out


def _escape(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    g = 6.6743e-11
    for _ in range(count):
        m = rng.choice([6.0e24, 7.3e22, 5.97e24])
        r = rng.choice([6.37e6, 1.74e6, 3.4e6])
        v = math.sqrt(2 * g * m / r)
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"Escape speed from a sphere of mass {m:.3e} kg and radius {r:.3e} m? "
                "Use G=6.6743e-11. Answer in m/s."
            ),
            answer=f"{v:.10g}",
            solution=f"v=sqrt(2GM/R)={v}.",
            expected=v,
            got=math.sqrt(2 * g * m / r),
            constraints=["Non-rotating sphere", "No atmosphere"],
            observations=[f"M={m}", f"R={r}"],
            plan=["Apply v=√(2GM/R)"],
            key=f"esc-{m}-{r}",
            rel_tol=1e-6,
        )
        if example:
            out.append(example)
    return out


def _beer_lambert(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        eps = rng.choice([1000, 2000, 5000])
        c = rng.choice([0.001, 0.002, 0.005])
        path = rng.choice([0.5, 1.0, 2.0])
        a = eps * c * path
        example = _emit(
            task_type="calculation",
            field="chemistry",
            prompt=(
                f"Beer–Lambert: ε={eps} L·mol⁻¹·cm⁻¹, c={c} mol·L⁻¹, l={path} cm. "
                "What is the absorbance A=εcl (dimensionless)?"
            ),
            answer=f"{a:.10g}",
            solution=f"A=εcl={eps}·{c}·{path}={a}.",
            expected=a,
            got=eps * c * path,
            constraints=["Linear Beer–Lambert", "No scattering"],
            observations=[f"ε={eps}", f"c={c}", f"l={path}"],
            plan=["Multiply ε, c, and path length"],
            key=f"beer-{eps}-{c}-{path}",
        )
        if example:
            out.append(example)
    return out


def _capacitance(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        c = rng.choice([2e-6, 5e-6, 1e-5])
        v = rng.randint(5, 24)
        q = c * v
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"A capacitor of {c:.0e} F is charged to {v} V. What is the stored charge in coulombs?"
            ),
            answer=f"{q:.10g}",
            solution=f"Q=CV={c}·{v}={q}.",
            expected=q,
            got=c * v,
            constraints=["Ideal capacitor", "SI"],
            observations=[f"C={c} F", f"V={v} V"],
            plan=["Apply Q=CV"],
            key=f"cap-{c}-{v}",
        )
        if example:
            out.append(example)
    return out


def _latent_heat(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        m = rng.choice([0.1, 0.2, 0.5, 1.0])
        l = rng.choice([334000, 2260000])
        q = m * l
        kind = "fusion" if l < 1e6 else "vaporization"
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"How much energy in joules is needed for {kind} of {m} kg of water "
                f"using L={l} J/kg (phase change only, no temperature change)?"
            ),
            answer=f"{q:.10g}",
            solution=f"Q=mL={m}·{l}={q}.",
            expected=q,
            got=m * l,
            constraints=["Isothermal phase change"],
            observations=[f"m={m} kg", f"L={l} J/kg"],
            plan=["Apply Q=mL"],
            key=f"lat-{m}-{l}",
        )
        if example:
            out.append(example)
    return out


def _kepler_period(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        t1, a1 = 1.0, 1.0
        a2 = rng.choice([4.0, 9.0, 16.0])
        # T^2 ∝ a^3  => T2 = T1 * (a2/a1)^(3/2)
        t2 = t1 * (a2 / a1) ** 1.5
        example = _emit(
            task_type="calculation",
            field="astronomy",
            prompt=(
                f"A planet orbits with period {t1} year at semi-major axis {a1} AU. "
                f"Another body has a={a2} AU around the same star. Period in years?"
            ),
            answer=f"{t2:.10g}",
            solution=f"T²∝a³ ⇒ T2=T1·(a2/a1)^(3/2)={t2}.",
            expected=t2,
            got=t1 * (a2 / a1) ** 1.5,
            constraints=["Kepler's third law", "Same central mass"],
            observations=[f"T1={t1}", f"a1={a1}", f"a2={a2}"],
            plan=["Scale period by a^(3/2)"],
            key=f"kep-{a2}",
        )
        if example:
            out.append(example)
    return out


def _work_force(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        f = rng.randint(5, 40)
        d = rng.randint(2, 15)
        theta = rng.choice([0, 60, 90])
        w = f * d * math.cos(math.radians(theta))
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"A constant force of {f} N acts through {d} m at {theta}° to the displacement. "
                "Work in joules?"
            ),
            answer=f"{w:.10g}",
            solution=f"W=Fd cosθ={f}·{d}·cos({theta}°)={w}.",
            expected=w,
            got=f * d * math.cos(math.radians(theta)),
            constraints=["Constant force", "θ from displacement"],
            observations=[f"F={f} N", f"d={d} m", f"theta={theta}"],
            plan=["Apply W=Fd cosθ"],
            key=f"work-{f}-{d}-{theta}",
        )
        if example:
            out.append(example)
    return out


def _molality(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        moles = rng.choice([0.25, 0.5, 1.0, 2.0])
        kg = rng.choice([0.5, 1.0, 2.0])
        molal = moles / kg
        example = _emit(
            task_type="calculation",
            field="chemistry",
            prompt=(
                f"Dissolve {moles} mol of solute in {kg} kg of solvent. What is the molality?"
            ),
            answer=f"{molal:.10g}",
            solution=f"m=n/kg_solvent={moles}/{kg}={molal}.",
            expected=molal,
            got=moles / kg,
            constraints=["Molality uses kg of solvent, not solution volume"],
            observations=[f"n={moles} mol", f"kg={kg}"],
            plan=["Divide moles by kilograms of solvent"],
            key=f"molal-{moles}-{kg}",
        )
        if example:
            out.append(example)
    return out


def _snell_angle(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n1, n2 = 1.0, 1.5
        theta1 = rng.choice([30, 45])
        s2 = n1 * math.sin(math.radians(theta1)) / n2
        theta2 = math.degrees(math.asin(s2))
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"Light goes from n={n1} into n={n2} at incidence {theta1}°. "
                "Refraction angle in degrees?"
            ),
            answer=f"{theta2:.10g}",
            solution=f"n1 sinθ1=n2 sinθ2 ⇒ θ2={theta2}.",
            expected=theta2,
            got=math.degrees(math.asin(n1 * math.sin(math.radians(theta1)) / n2)),
            constraints=["Snell's law", "No TIR"],
            observations=[f"n1={n1}", f"n2={n2}", f"theta1={theta1}"],
            plan=["Solve for θ2"],
            key=f"snell-{theta1}-{n2}",
            rel_tol=1e-5,
        )
        if example:
            out.append(example)
    return out


def _radio_intensity(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        p = rng.choice([10, 20, 50, 100])
        r = rng.choice([2, 5, 10])
        i = p / (4 * math.pi * r * r)
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"An isotropic source radiates {p} W. Intensity at {r} m, in W/m²?"
            ),
            answer=f"{i:.10g}",
            solution=f"I=P/(4πr²)={p}/(4π·{r}²)={i}.",
            expected=i,
            got=p / (4 * math.pi * r * r),
            constraints=["Isotropic point source", "No absorption"],
            observations=[f"P={p} W", f"r={r} m"],
            plan=["Divide power by sphere area"],
            key=f"int-{p}-{r}",
        )
        if example:
            out.append(example)
    return out
