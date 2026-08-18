"""New science families: ideal gas, density, thin lens."""

from __future__ import annotations

import random

from open_reason.generation.science import _emit
from open_reason.models import Example


def extra_science(rng: random.Random) -> list[Example]:
    out: list[Example] = []
    out.extend(_ideal_gas(rng, 10))
    out.extend(_density(rng, 10))
    out.extend(_thin_lens(rng, 8))
    return out


def _ideal_gas(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    r = 8.314
    for _ in range(count):
        n = rng.choice([1, 2, 3])
        t = rng.choice([200, 250, 273, 300, 350])
        v = rng.choice([1, 2, 4, 5, 10])
        p = n * r * t / v
        example = _emit(
            task_type="calculation",
            field="chemistry",
            prompt=(
                f"An ideal gas has n={n} mol, T={t} K, V={v} m^3. "
                "Using R=8.314 J/(mol·K), what is P in pascals from PV=nRT?"
            ),
            answer=f"{p:.10g}",
            solution=f"P = nRT/V = {n}*{r}*{t}/{v} = {p}.",
            expected=p,
            got=n * r * t / v,
            constraints=["Ideal gas", "SI units"],
            observations=[f"n={n}", f"T={t} K", f"V={v} m^3"],
            plan=["Write PV=nRT", "Solve for P"],
            key=f"gas-{n}-{t}-{v}",
        )
        if example:
            out.append(example)
    return out


def _density(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        mass = rng.randint(2, 20)
        volume = rng.choice([0.5, 1, 2, 4, 5])
        rho = mass / volume
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"A sample has mass {mass} kg and volume {volume:g} m^3. "
                "What is its density in kg/m^3?"
            ),
            answer=f"{rho:.10g}",
            solution=f"ρ = m/V = {mass}/{volume:g} = {rho}.",
            expected=rho,
            got=mass / volume,
            constraints=["Uniform density", "SI units"],
            observations=[f"m={mass} kg", f"V={volume:g} m^3"],
            plan=["Divide mass by volume"],
            key=f"dens-{mass}-{volume}",
        )
        if example:
            out.append(example)
    return out


def _thin_lens(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        f = rng.choice([5, 8, 10, 12])
        u = rng.choice([15, 20, 24, 30, 40])
        if u == f:
            u = f + 5
        v = 1 / (1 / f - 1 / u)
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"A thin converging lens has f={f} cm. A real object is u={u} cm away. "
                "Using 1/f = 1/v + 1/u with positive distances, what is v in cm?"
            ),
            answer=f"{v:.10g}",
            solution=f"1/v = 1/f - 1/u = 1/{f} - 1/{u} so v = {v}.",
            expected=v,
            got=1 / (1 / f - 1 / u),
            constraints=["Thin-lens equation", "Positive real-object distances"],
            observations=[f"f={f} cm", f"u={u} cm"],
            plan=["Rearrange 1/f=1/v+1/u", "Compute v"],
            key=f"lens-{f}-{u}",
            rel_tol=1e-6,
        )
        if example:
            out.append(example)
    return out
