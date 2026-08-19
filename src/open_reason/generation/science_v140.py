"""v1.4.0 science: extra numeric families with independent checks."""

from __future__ import annotations

import math
import random

from open_reason.generation.science import _emit
from open_reason.models import Example


def extra_science_v140(rng: random.Random) -> list[Example]:
    out: list[Example] = []
    out.extend(_ohm(rng, 16))
    out.extend(_density(rng, 14))
    out.extend(_hydrostatic(rng, 14))
    out.extend(_specific_heat(rng, 14))
    out.extend(_spring_energy(rng, 14))
    out.extend(_momentum(rng, 16))
    out.extend(_ideal_gas(rng, 14))
    out.extend(_wavelength(rng, 14))
    out.extend(_grav_pe(rng, 14))
    out.extend(_electric_power(rng, 14))
    out.extend(_efficiency(rng, 12))
    out.extend(_half_remain(rng, 14))
    out.extend(_thin_lens(rng, 12))
    out.extend(_pendulum(rng, 12))
    out.extend(_kinetic(rng, 14))
    out.extend(_series_r(rng, 14))
    out.extend(_parallel_r(rng, 12))
    out.extend(_pressure(rng, 12))
    return out


def _ohm(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        i = rng.choice([0.5, 1.0, 2.0, 3.0])
        r = rng.choice([4, 5, 10, 20])
        v = i * r
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=f"A current of {i} A flows through {r} Ω. Voltage in volts (Ohm's law)?",
            answer=f"{v:.10g}",
            solution=f"V=IR={i}·{r}={v}.",
            expected=v,
            got=i * r,
            constraints=["Ohmic resistor", "DC"],
            observations=[f"I={i} A", f"R={r} Ω"],
            plan=["Apply V=IR"],
            key=f"v140-ohm-{i}-{r}",
        )
        if example:
            out.append(example)
    return out


def _density(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        m = rng.choice([2.0, 5.0, 10.0, 12.0])
        vol = rng.choice([0.5, 1.0, 2.0, 4.0])
        d = m / vol
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=f"A sample has mass {m} kg and volume {vol} m³. Density in kg/m³?",
            answer=f"{d:.10g}",
            solution=f"ρ=m/V={m}/{vol}={d}.",
            expected=d,
            got=m / vol,
            constraints=["Uniform density"],
            observations=[f"m={m} kg", f"V={vol} m³"],
            plan=["Divide mass by volume"],
            key=f"v140-dens-{m}-{vol}",
        )
        if example:
            out.append(example)
    return out


def _hydrostatic(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    g = 9.8
    for _ in range(count):
        rho = rng.choice([1000, 800, 13600])
        h = rng.choice([2, 5, 10])
        p = rho * g * h
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"Gauge pressure at depth {h} m in a fluid of density {rho} kg/m³? "
                "Use g=9.8 m/s². Answer in pascals."
            ),
            answer=f"{p:.10g}",
            solution=f"P=ρgh={rho}·9.8·{h}={p}.",
            expected=p,
            got=rho * g * h,
            constraints=["Incompressible", "g=9.8"],
            observations=[f"rho={rho}", f"h={h}"],
            plan=["Apply P=ρgh"],
            key=f"v140-hyd-{rho}-{h}",
        )
        if example:
            out.append(example)
    return out


def _specific_heat(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        m = rng.choice([0.5, 1.0, 2.0])
        c = rng.choice([4180, 900, 450])
        dt = rng.choice([10, 20, 30])
        q = m * c * dt
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"How much heat in joules raises {m} kg of material (c={c} J/kg·K) "
                f"by {dt} K? No phase change."
            ),
            answer=f"{q:.10g}",
            solution=f"Q=mcΔT={m}·{c}·{dt}={q}.",
            expected=q,
            got=m * c * dt,
            constraints=["Constant c", "No phase change"],
            observations=[f"m={m}", f"c={c}", f"dT={dt}"],
            plan=["Apply Q=mcΔT"],
            key=f"v140-sh-{m}-{c}-{dt}",
        )
        if example:
            out.append(example)
    return out


def _spring_energy(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        k = rng.choice([20, 50, 100, 200])
        x = rng.choice([0.1, 0.2, 0.5])
        e = 0.5 * k * x * x
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"A Hookean spring with k={k} N/m is stretched {x} m from equilibrium. "
                "Elastic potential energy in joules?"
            ),
            answer=f"{e:.10g}",
            solution=f"U=½kx²=0.5·{k}·{x}²={e}.",
            expected=e,
            got=0.5 * k * x * x,
            constraints=["Ideal spring"],
            observations=[f"k={k}", f"x={x}"],
            plan=["Apply U=½kx²"],
            key=f"v140-spr-{k}-{x}",
        )
        if example:
            out.append(example)
    return out


def _momentum(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        m = rng.randint(1, 8)
        v = rng.randint(2, 15)
        p = m * v
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=f"Linear momentum of {m} kg moving at {v} m/s, in kg·m/s?",
            answer=f"{p:.10g}",
            solution=f"p=mv={m}·{v}={p}.",
            expected=p,
            got=m * v,
            constraints=["One dimension"],
            observations=[f"m={m} kg", f"v={v} m/s"],
            plan=["Apply p=mv"],
            key=f"v140-mom-{m}-{v}",
        )
        if example:
            out.append(example)
    return out


def _ideal_gas(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    r = 8.314
    for _ in range(count):
        n = rng.choice([1.0, 2.0])
        t = rng.choice([273, 300, 350])
        v = rng.choice([0.01, 0.02, 0.05])
        p = n * r * t / v
        example = _emit(
            task_type="calculation",
            field="chemistry",
            prompt=(
                f"Ideal gas: n={n} mol, T={t} K, V={v} m³. Pressure in pascals? "
                "Use R=8.314 J/mol·K."
            ),
            answer=f"{p:.10g}",
            solution=f"P=nRT/V={n}·8.314·{t}/{v}={p}.",
            expected=p,
            got=n * r * t / v,
            constraints=["Ideal gas", "SI"],
            observations=[f"n={n}", f"T={t}", f"V={v}"],
            plan=["Apply PV=nRT"],
            key=f"v140-gas-{n}-{t}-{v}",
            rel_tol=1e-6,
        )
        if example:
            out.append(example)
    return out


def _wavelength(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    c = 3.0e8
    for _ in range(count):
        f = rng.choice([1.0e8, 2.0e8, 5.0e8, 1.0e9])
        lam = c / f
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"An EM wave in vacuum has frequency {f:.0e} Hz. Wavelength in metres? "
                "Use c=3.0e8 m/s."
            ),
            answer=f"{lam:.10g}",
            solution=f"λ=c/f={c}/{f}={lam}.",
            expected=lam,
            got=c / f,
            constraints=["Vacuum", "c=3.0e8"],
            observations=[f"f={f}"],
            plan=["Apply λ=c/f"],
            key=f"v140-wav-{f}",
        )
        if example:
            out.append(example)
    return out


def _grav_pe(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    g = 9.8
    for _ in range(count):
        m = rng.choice([1, 2, 5, 10])
        h = rng.choice([2, 4, 8, 10])
        u = m * g * h
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"Gravitational potential energy of {m} kg raised {h} m near Earth? "
                "Use g=9.8 m/s² and U=0 at the lower level. Joules."
            ),
            answer=f"{u:.10g}",
            solution=f"U=mgh={m}·9.8·{h}={u}.",
            expected=u,
            got=m * g * h,
            constraints=["Uniform g", "g=9.8"],
            observations=[f"m={m}", f"h={h}"],
            plan=["Apply U=mgh"],
            key=f"v140-gpe-{m}-{h}",
        )
        if example:
            out.append(example)
    return out


def _electric_power(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        i = rng.choice([0.5, 1, 2, 4])
        v = rng.choice([5, 12, 24, 120])
        p = i * v
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=f"DC circuit: I={i} A, V={v} V. Instantaneous electrical power in watts?",
            answer=f"{p:.10g}",
            solution=f"P=IV={i}·{v}={p}.",
            expected=p,
            got=i * v,
            constraints=["DC", "P=IV"],
            observations=[f"I={i}", f"V={v}"],
            plan=["Multiply current and voltage"],
            key=f"v140-pow-{i}-{v}",
        )
        if example:
            out.append(example)
    return out


def _efficiency(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        useful = rng.choice([20, 40, 60, 80])
        total = rng.choice([100, 120, 200])
        if useful >= total:
            continue
        eta = useful / total
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"A machine delivers {useful} J of useful work from {total} J of input energy. "
                "Efficiency as a fraction (not percent)?"
            ),
            answer=f"{eta:.10g}",
            solution=f"η=W_out/E_in={useful}/{total}={eta}.",
            expected=eta,
            got=useful / total,
            constraints=["Report fraction 0–1", "Not percent"],
            observations=[f"useful={useful}", f"total={total}"],
            plan=["Divide useful energy by input"],
            key=f"v140-eff-{useful}-{total}",
        )
        if example:
            out.append(example)
    return out


def _half_remain(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n0 = rng.choice([800, 1600, 3200])
        half = rng.choice([2, 4])
        t = rng.choice([2, 4, 6])
        n = n0 * (0.5 ** (t / half))
        example = _emit(
            task_type="calculation",
            field="chemistry",
            prompt=(
                f"A sample starts with {n0} nuclei and half-life {half} years. "
                f"How many remain after {t} years? Exponential decay N=N0·(1/2)^(t/T)."
            ),
            answer=f"{n:.10g}",
            solution=f"N={n0}·(1/2)^({t}/{half})={n}.",
            expected=n,
            got=n0 * (0.5 ** (t / half)),
            constraints=["No branching", "Given half-life"],
            observations=[f"N0={n0}", f"T={half}", f"t={t}"],
            plan=["Apply N=N0 (1/2)^{t/T}"],
            key=f"v140-hl-{n0}-{half}-{t}",
        )
        if example:
            out.append(example)
    return out


def _thin_lens(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        f = rng.choice([10, 20, 25])
        u = rng.choice([30, 40, 50])
        v = 1 / (1 / f - 1 / u)
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"Thin lens: f={f} cm, object distance u={u} cm (real object, u>0). "
                "Image distance v in cm from 1/f=1/u+1/v?"
            ),
            answer=f"{v:.10g}",
            solution=f"1/v=1/f-1/u ⇒ v={v}.",
            expected=v,
            got=1 / (1 / f - 1 / u),
            constraints=["Cartesian convention stated", "Same units"],
            observations=[f"f={f}", f"u={u}"],
            plan=["Solve lens equation for v"],
            key=f"v140-lens-{f}-{u}",
            rel_tol=1e-6,
        )
        if example:
            out.append(example)
    return out


def _pendulum(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    g = 9.8
    for _ in range(count):
        length = rng.choice([0.25, 0.5, 1.0, 2.0])
        t = 2 * math.pi * math.sqrt(length / g)
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"Small-angle simple pendulum of length {length} m. Period in seconds? "
                "Use g=9.8 m/s² and T=2π√(L/g)."
            ),
            answer=f"{t:.10g}",
            solution=f"T=2π√(L/g)={t}.",
            expected=t,
            got=2 * math.pi * math.sqrt(length / g),
            constraints=["Small angle", "g=9.8"],
            observations=[f"L={length}"],
            plan=["Apply T=2π√(L/g)"],
            key=f"v140-pend-{length}",
            rel_tol=1e-6,
        )
        if example:
            out.append(example)
    return out


def _kinetic(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        m = rng.choice([1, 2, 4])
        v = rng.choice([3, 5, 10])
        k = 0.5 * m * v * v
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=f"Translational kinetic energy of {m} kg at {v} m/s, in joules?",
            answer=f"{k:.10g}",
            solution=f"K=½mv²=0.5·{m}·{v}²={k}.",
            expected=k,
            got=0.5 * m * v * v,
            constraints=["Non-relativistic"],
            observations=[f"m={m}", f"v={v}"],
            plan=["Apply K=½mv²"],
            key=f"v140-ke-{m}-{v}",
        )
        if example:
            out.append(example)
    return out


def _series_r(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        r1, r2, r3 = rng.choice([2, 4, 5]), rng.choice([3, 6, 10]), rng.choice([1, 8])
        total = r1 + r2 + r3
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=f"Three resistors {r1}, {r2}, {r3} Ω in series. Equivalent resistance in ohms?",
            answer=f"{total:.10g}",
            solution=f"R={r1}+{r2}+{r3}={total}.",
            expected=total,
            got=r1 + r2 + r3,
            constraints=["Series connection"],
            observations=[f"R1={r1}", f"R2={r2}", f"R3={r3}"],
            plan=["Sum resistances"],
            key=f"v140-ser-{r1}-{r2}-{r3}",
        )
        if example:
            out.append(example)
    return out


def _parallel_r(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        r1, r2 = rng.choice([4, 6, 12]), rng.choice([4, 12, 6])
        req = 1 / (1 / r1 + 1 / r2)
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=f"Two resistors {r1} Ω and {r2} Ω in parallel. Equivalent resistance in ohms?",
            answer=f"{req:.10g}",
            solution=f"1/Req=1/{r1}+1/{r2} ⇒ Req={req}.",
            expected=req,
            got=1 / (1 / r1 + 1 / r2),
            constraints=["Two ideal resistors", "Parallel"],
            observations=[f"R1={r1}", f"R2={r2}"],
            plan=["Reciprocal sum"],
            key=f"v140-par-{r1}-{r2}",
            rel_tol=1e-6,
        )
        if example:
            out.append(example)
    return out


def _pressure(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        f = rng.choice([10, 20, 50, 100])
        a = rng.choice([0.01, 0.02, 0.05])
        p = f / a
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=f"A force of {f} N is applied uniformly over {a} m². Pressure in pascals?",
            answer=f"{p:.10g}",
            solution=f"P=F/A={f}/{a}={p}.",
            expected=p,
            got=f / a,
            constraints=["Uniform normal force"],
            observations=[f"F={f} N", f"A={a} m²"],
            plan=["Apply P=F/A"],
            key=f"v140-pres-{f}-{a}",
        )
        if example:
            out.append(example)
    return out
