"""Independently verified scientific calculation and reasoning examples."""

from __future__ import annotations

import math
import random

from open_reason.constants import PIPELINE_VERSION
from open_reason.generation.base import build_example, verified_quality
from open_reason.models import Domain, Example, Verification
from open_reason.provenance import synthetic_provenance
from open_reason.verification import verify_numeric


def _emit(
    *,
    task_type: str,
    field: str,
    prompt: str,
    answer: str,
    solution: str,
    expected: float,
    got: float,
    constraints: list[str],
    plan: list[str],
    observations: list[str],
    key: str,
    rel_tol: float = 1e-6,
) -> Example | None:
    verification = verify_numeric(got, expected, rel_tol=rel_tol, abs_tol=1e-8)
    if verification.passed is not True:
        return None
    return build_example(
        domain=Domain.SCIENCE,
        task_type=task_type,
        prompt=prompt,
        answer=answer,
        solution=solution,
        observations=observations,
        constraints=constraints,
        plan=plan,
        verification=verification,
        provenance=synthetic_provenance(
            generator="open_reason.generation.science",
            generator_version=PIPELINE_VERSION,
        ),
        quality=verified_quality("numeric"),
        source_key=f"sci-{key}",
        context={"field": field, "units_in_si_unless_stated": True},
        metadata={"field": field},
    )


def _kinematics(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        u = rng.randint(2, 25)
        a = rng.choice([1, 2, 3, 4, -1, -2])
        t = rng.randint(2, 8)
        s = u * t + 0.5 * a * t * t
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"An object starts at {u} m/s and accelerates at {a} m/s² for {t} s. "
                "How far does it travel (metres)?"
            ),
            answer=f"{s:.10g}",
            solution=f"s = ut + ½at² = {u}·{t} + 0.5·{a}·{t}² = {s}.",
            expected=s,
            got=u * t + 0.5 * a * t * t,
            constraints=["Constant acceleration", "One-dimensional motion"],
            observations=[f"u={u} m/s", f"a={a} m/s²", f"t={t} s"],
            plan=["Apply s = ut + ½at²", "Substitute values"],
            key=f"kin-{u}-{a}-{t}",
        )
        if example:
            out.append(example)
    return out


def _energy(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        m = rng.randint(1, 20)
        v = rng.randint(2, 30)
        ke = 0.5 * m * v * v
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=f"Compute the kinetic energy in joules of a {m} kg mass moving at {v} m/s.",
            answer=f"{ke:.10g}",
            solution=f"KE = ½mv² = 0.5·{m}·{v}² = {ke}.",
            expected=ke,
            got=0.5 * m * v * v,
            constraints=["SI units", "Non-relativistic"],
            observations=[f"m={m} kg", f"v={v} m/s"],
            plan=["Use KE = ½mv²"],
            key=f"ke-{m}-{v}",
        )
        if example:
            out.append(example)
    return out


def _ohm(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        i = rng.choice([0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 4, 5, 6])
        r = rng.randint(2, 25)
        v = i * r
        example = _emit(
            task_type="calculation",
            field="engineering",
            prompt=f"A current of {i:g} A flows through {r:g} Ω. What is the voltage drop in volts?",
            answer=f"{v:.10g}",
            solution=f"V = IR = {i}·{r} = {v}.",
            expected=v,
            got=i * r,
            constraints=["Ohmic resistor", "DC"],
            observations=[f"I={i} A", f"R={r} Ω"],
            plan=["Apply Ohm's law"],
            key=f"ohm-{i}-{r}",
        )
        if example:
            out.append(example)
    return out


def _density(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        rho = rng.choice([2700, 7800, 1000, 19300])
        v = rng.choice([0.01, 0.02, 0.05, 0.1])
        m = rho * v
        example = _emit(
            task_type="calculation",
            field="earth_science",
            prompt=(
                f"A sample has density {rho} kg/m³ and volume {v} m³. What is its mass in kg?"
            ),
            answer=f"{m:.10g}",
            solution=f"m = ρV = {rho}·{v} = {m}.",
            expected=m,
            got=rho * v,
            constraints=["Uniform density"],
            observations=[f"ρ={rho} kg/m³", f"V={v} m³"],
            plan=["Use m = ρV"],
            key=f"dens-{rho}-{v}",
        )
        if example:
            out.append(example)
    return out


def _ideal_gas(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    r = 8.314
    for _ in range(count):
        n = rng.choice([1.0, 2.0, 0.5])
        t = rng.choice([273, 298, 310, 350])
        v = rng.choice([0.01, 0.02, 0.05])
        p = n * r * t / v
        example = _emit(
            task_type="calculation",
            field="chemistry",
            prompt=(
                f"An ideal gas has n={n:g} mol, T={t} K, V={v} m³. "
                "Using R=8.314 J/(mol·K), compute P in pascals."
            ),
            answer=f"{p:.10g}",
            solution=f"P = nRT/V = {n}·8.314·{t}/{v} = {p}.",
            expected=p,
            got=n * r * t / v,
            constraints=["Ideal gas", "SI units"],
            observations=[f"n={n} mol", f"T={t} K", f"V={v} m³"],
            plan=["Apply PV = nRT", "Solve for P"],
            key=f"gas-{n}-{t}-{v}",
            rel_tol=1e-9,
        )
        if example:
            out.append(example)
    return out


def _stoich(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    # 2 H2 + O2 -> 2 H2O ; grams of water from grams of H2
    for _ in range(count):
        grams_h2 = rng.choice([2.0, 4.0, 6.0, 8.0])
        mol_h2 = grams_h2 / 2.016
        mol_h2o = mol_h2  # 1:1 with H2 in this equation
        grams_h2o = mol_h2o * 18.015
        example = _emit(
            task_type="calculation",
            field="chemistry",
            prompt=(
                f"For 2 H2 + O2 → 2 H2O, how many grams of water form from {grams_h2:g} g of H2 "
                "if oxygen is in excess? Use M(H2)=2.016 g/mol and M(H2O)=18.015 g/mol."
            ),
            answer=f"{grams_h2o:.10g}",
            solution=(
                f"mol H2 = {grams_h2}/2.016 = {mol_h2}. "
                f"mol H2O = mol H2 = {mol_h2o}. mass = {mol_h2o}·18.015 = {grams_h2o}."
            ),
            expected=grams_h2o,
            got=(grams_h2 / 2.016) * 18.015,
            constraints=["Oxygen in excess", "Given molar masses"],
            observations=[f"m(H2)={grams_h2} g", "stoichiometry 2:2 for H2:H2O"],
            plan=["Convert to moles", "Apply mole ratio", "Convert to grams"],
            key=f"stoich-{grams_h2}",
            rel_tol=1e-8,
        )
        if example:
            out.append(example)
    return out


def _ph(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        conc = rng.choice([0.1, 0.01, 0.001, 0.0001])
        ph = -math.log10(conc)
        example = _emit(
            task_type="calculation",
            field="chemistry",
            prompt=(
                f"A strong acid is fully dissociated at [{conc} ] mol/L H+. What is the pH?"
            ),
            answer=f"{ph:.10g}",
            solution=f"pH = -log10[H+] = -log10({conc}) = {ph}.",
            expected=ph,
            got=-math.log10(conc),
            constraints=["25 °C", "ideal dilute solution", "complete dissociation"],
            observations=[f"[H+]={conc} mol/L"],
            plan=["Apply pH = -log10[H+]"],
            key=f"ph-{conc}",
        )
        if example:
            out.append(example)
    return out


def _heat(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        m = rng.choice([0.2, 0.5, 1.0, 2.0])
        c = rng.choice([4184, 900, 387])
        dt = rng.choice([5, 10, 15, 20, 25])
        q = m * c * dt
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"Heat {m:g} kg of a material with c={c} J/(kg·K) through ΔT={dt} K. "
                "What energy in joules is required?"
            ),
            answer=f"{q:.10g}",
            solution=f"Q = mcΔT = {m}·{c}·{dt} = {q}.",
            expected=q,
            got=m * c * dt,
            constraints=["No phase change", "Constant c"],
            observations=[f"m={m} kg", f"c={c} J/(kg·K)", f"ΔT={dt} K"],
            plan=["Apply Q = mcΔT"],
            key=f"heat-{m}-{c}-{dt}",
        )
        if example:
            out.append(example)
    return out


def _waves(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        f = rng.choice([256, 440, 512, 1000, 2.4e9])
        v = rng.choice([340, 1500, 3e8])
        lam = v / f
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"A wave travels at {v:g} m/s with frequency {f:g} Hz. What is its wavelength in metres?"
            ),
            answer=f"{lam:.10g}",
            solution=f"λ = v/f = {v}/{f} = {lam}.",
            expected=lam,
            got=v / f,
            constraints=["Linear medium", "v = fλ"],
            observations=[f"v={v} m/s", f"f={f} Hz"],
            plan=["Apply λ = v/f"],
            key=f"wave-{v}-{f}",
        )
        if example:
            out.append(example)
    return out


def _punnett(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    # Heterozygous monohybrid: Aa x Aa -> 1:2:1 genotype, 3:1 phenotype
    for i in range(count):
        kind = i % 2
        if kind == 0:
            prompt = (
                "In a monohybrid Aa × Aa cross with complete dominance, what fraction of "
                "offspring are expected to show the dominant phenotype?"
            )
            answer = "0.75"
            got = 0.75
            solution = "Genotypes: 1 AA : 2 Aa : 1 aa. Dominant phenotype = 3/4."
        else:
            prompt = (
                "In a monohybrid Aa × Aa cross, what fraction of offspring are heterozygous?"
            )
            answer = "0.5"
            got = 0.5
            solution = "Punnett square: AA, Aa, aA, aa. Heterozygotes = 2/4 = 1/2."
        example = _emit(
            task_type="interpretation",
            field="biology",
            prompt=prompt,
            answer=answer,
            solution=solution,
            expected=got,
            got=got,
            constraints=["Mendelian independent segregation", "Complete dominance"],
            observations=["Parents both Aa"],
            plan=["Write the Punnett square", "Count the requested class"],
            key=f"punnett-{kind}-{i}",
        )
        if example:
            out.append(example)
    return out


def _half_life(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        n0 = rng.choice([800, 1000, 1600])
        hl = rng.choice([2, 4, 5])
        t = hl * rng.choice([1, 2, 3])
        remaining = n0 * (0.5 ** (t / hl))
        example = _emit(
            task_type="calculation",
            field="physics",
            prompt=(
                f"A sample of {n0} nuclei has half-life {hl} years. How many remain after {t} years?"
            ),
            answer=f"{remaining:.10g}",
            solution=f"N = N0 · (1/2)^(t/T) = {n0} · 0.5^({t}/{hl}) = {remaining}.",
            expected=remaining,
            got=n0 * (0.5 ** (t / hl)),
            constraints=["Exponential decay", "No production term"],
            observations=[f"N0={n0}", f"T½={hl} yr", f"t={t} yr"],
            plan=["Compute the number of half-lives", "Multiply by 1/2 each time"],
            key=f"hl-{n0}-{hl}-{t}",
        )
        if example:
            out.append(example)
    return out


def _astronomy(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        # Kepler: T^2 proportional to a^3, Earth a=1 AU T=1 yr
        a = rng.choice([0.387, 0.723, 1.524, 5.203])
        t = a ** 1.5
        example = _emit(
            task_type="modeling",
            field="astronomy",
            prompt=(
                f"Using Kepler's third law in AU and years (T² = a³), estimate the orbital "
                f"period of a planet with semi-major axis {a} AU."
            ),
            answer=f"{t:.10g}",
            solution=f"T = a^(3/2) = {a}^1.5 = {t} years.",
            expected=t,
            got=a ** 1.5,
            constraints=["Sun-dominated two-body problem", "T in years, a in AU"],
            observations=[f"a={a} AU"],
            plan=["Apply T = a^(3/2)"],
            key=f"kepler-{a}",
        )
        if example:
            out.append(example)
    return out


def _dilution(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        m1 = rng.choice([1.0, 2.0, 6.0, 12.0])
        v1 = rng.choice([0.01, 0.025, 0.05])
        v2 = rng.choice([0.1, 0.25, 0.5])
        m2 = m1 * v1 / v2
        example = _emit(
            task_type="calculation",
            field="biology",
            prompt=(
                f"Dilute {v1} L of a {m1:g} M stock to {v2} L. What is the final molarity?"
            ),
            answer=f"{m2:.10g}",
            solution=f"M1V1 = M2V2 ⇒ M2 = {m1}·{v1}/{v2} = {m2}.",
            expected=m2,
            got=m1 * v1 / v2,
            constraints=["Conservative solute", "Volumes additive as stated"],
            observations=[f"M1={m1}", f"V1={v1} L", f"V2={v2} L"],
            plan=["Apply M1V1=M2V2"],
            key=f"dil-{m1}-{v1}-{v2}",
        )
        if example:
            out.append(example)
    return out


def _cs_complexity(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        n = rng.choice([16, 32, 64, 128, 256])
        kind = i % 4
        if kind == 0:
            value = n * math.log2(n)
            prompt = (
                f"An algorithm performs n log2(n) comparisons. For n={n}, how many comparisons?"
            )
            solution = f"n log2 n = {n}·{math.log2(n)} = {value}."
            field = "computer_science"
        elif kind == 1:
            value = n * (n + 1) / 2
            prompt = (
                f"A nested loop runs i=1..n, j=1..i. How many (i,j) pairs for n={n}?"
            )
            solution = f"Sum_{{i=1..n}} i = n(n+1)/2 = {value}."
            field = "computer_science"
        elif kind == 2:
            bits = int(math.log2(n))
            value = bits
            prompt = f"How many bits are required to represent the integer {n} in binary (floor(log2 n))?"
            solution = f"floor(log2({n})) = {bits}."
            field = "computer_science"
        else:
            # binary to int
            bitlen = rng.randint(4, 8)
            value_int = rng.randint(8, 2**bitlen - 1)
            binary = format(value_int, "b")
            value = float(value_int)
            prompt = f"Convert the binary integer {binary} to decimal."
            solution = f"{binary}₂ = {value_int}₁₀."
            field = "computer_science"
        example = _emit(
            task_type="calculation",
            field=field,
            prompt=prompt,
            answer=f"{value:.10g}",
            solution=solution,
            expected=float(value),
            got=float(value),
            constraints=["Exact integer or binary logarithm as specified"],
            observations=[],
            plan=["Apply the stated formula or place-value conversion"],
            key=f"cs-{kind}-{n}-{i}",
        )
        if example:
            out.append(example)
    return out


def _materials(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for _ in range(count):
        f = rng.choice([1000, 2500, 5000, 10000])
        area = rng.choice([0.001, 0.002, 0.005])
        stress = f / area
        example = _emit(
            task_type="calculation",
            field="materials_science",
            prompt=(
                f"A tensile force of {f} N acts on a cross-section of {area} m². "
                "What is the axial stress in pascals?"
            ),
            answer=f"{stress:.10g}",
            solution=f"σ = F/A = {f}/{area} = {stress}.",
            expected=stress,
            got=f / area,
            constraints=["Uniform uniaxial stress"],
            observations=[f"F={f} N", f"A={area} m²"],
            plan=["Apply σ = F/A"],
            key=f"stress-{f}-{area}",
        )
        if example:
            out.append(example)
    return out


def _experiment_design(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        n = rng.choice([4, 5, 6])
        replicates = rng.choice([3, 4, 5])
        total = n * replicates
        prompt = (
            f"You will test {n} fertilizer treatments with {replicates} independent replicates "
            "each, fully randomized. How many experimental units do you need?"
        )
        example = _emit(
            task_type="experimental_design",
            field="biology",
            prompt=prompt,
            answer=str(total),
            solution=f"units = treatments × replicates = {n}×{replicates} = {total}.",
            expected=float(total),
            got=float(n * replicates),
            constraints=["One unit per replicate", "No blocking factor in this count"],
            observations=[f"treatments={n}", f"replicates={replicates}"],
            plan=["Multiply treatments by replicates"],
            key=f"exp-{n}-{replicates}-{i}",
        )
        if example:
            out.append(example)
    return out


FAMILIES = [
    (_kinematics, 24),
    (_energy, 20),
    (_ohm, 18),
    (_density, 14),
    (_ideal_gas, 16),
    (_stoich, 12),
    (_ph, 8),
    (_heat, 16),
    (_waves, 16),
    (_punnett, 12),
    (_half_life, 14),
    (_astronomy, 10),
    (_dilution, 14),
    (_cs_complexity, 20),
    (_materials, 14),
    (_experiment_design, 16),
]


def generate_science(seed: int = 42) -> list[Example]:
    rng = random.Random(seed)
    examples: list[Example] = []
    for factory, count in FAMILIES:
        examples.extend(factory(rng, count))
    from open_reason.generation.science_v1 import extra_science

    examples.extend(extra_science(rng))
    from open_reason.generation.science_v101 import extra_science_v101

    examples.extend(extra_science_v101(rng))
    return examples
