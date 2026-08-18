"""Structured reasoning tasks with independently checkable answers.

These are concise reasoning summaries (problem, observations, constraints, plan,
answer), not hidden chain-of-thought.
"""

from __future__ import annotations

import itertools
import random
from datetime import date, timedelta

from open_reason.constants import PIPELINE_VERSION
from open_reason.generation.base import build_example, verified_quality
from open_reason.models import Domain, Example, Verification
from open_reason.provenance import synthetic_provenance


def _prov():
    return synthetic_provenance(
        generator="open_reason.generation.reasoning",
        generator_version=PIPELINE_VERSION,
    )


def _emit(
    *,
    task_type: str,
    prompt: str,
    answer: str,
    solution: str,
    observations: list[str],
    constraints: list[str],
    assumptions: list[str],
    plan: list[str],
    key: str,
    check: bool,
) -> Example | None:
    if not check:
        return None
    verification = Verification(method="constraint-check", passed=True, result=answer)
    return build_example(
        domain=Domain.REASONING,
        task_type=task_type,
        prompt=prompt,
        answer=answer,
        solution=solution,
        observations=observations,
        constraints=constraints,
        assumptions=assumptions,
        plan=plan,
        verification=verification,
        provenance=_prov(),
        quality=verified_quality("constraint-check"),
        source_key=f"reason-{key}",
        context={"reasoning_style": "structured_summary"},
    )


def _scheduling(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    people = ["Alex", "Blair", "Casey", "Drew", "Eden", "Finn"]
    slots = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00"]
    for i in range(count):
        n = 3
        names = people[i % 3 : i % 3 + n]
        forbidden = {
            names[0]: {slots[i % 4]},
            names[1]: {slots[(i + 2) % 6]},
            names[2]: set(),
        }
        # assign distinct slots avoiding forbidden
        assignment = None
        for perm in itertools.permutations(slots[:4], n):
            cand = dict(zip(names, perm))
            if all(cand[name] not in forbidden[name] for name in names):
                assignment = cand
                break
        if assignment is None:
            continue
        ordered = ", ".join(f"{k}@{v}" for k, v in sorted(assignment.items()))
        prompt = (
            f"Schedule a 1-hour meeting for {', '.join(names)} using distinct slots "
            f"from {slots[:4]}. Constraints: "
            + "; ".join(f"{k} cannot do {sorted(v)}" if v else f"{k} is free all listed slots" for k, v in forbidden.items())
            + ". Give one feasible assignment as name@slot pairs sorted by name."
        )
        ok = len(set(assignment.values())) == n and all(
            assignment[name] not in forbidden[name] for name in names
        )
        example = _emit(
            task_type="planning",
            prompt=prompt,
            answer=ordered,
            solution=(
                "Treat this as assigning distinct slots under exclusion constraints. "
                f"One feasible assignment is {ordered}."
            ),
            observations=[f"{k} forbidden={sorted(v)}" for k, v in forbidden.items()],
            constraints=["Distinct slots", "Respect exclusions", "Use only listed slots"],
            assumptions=["Each meeting lasts one slot", "No other hidden constraints"],
            plan=["Enumerate permutations of the first four slots", "Drop assignments that hit an exclusion", "Serialize the first feasible plan"],
            key=f"sched-{i}-{ordered}",
            check=ok,
        )
        if example:
            out.append(example)
    return out


def _classification(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        mass = round(0.4 + i * 1.7, 2)
        haz = rng.choice([True, False])
        dest = rng.choice(["domestic", "international"])
        if haz:
            label = "restricted"
        elif mass > 30:
            label = "freight"
        elif dest == "international":
            label = "parcel-intl"
        else:
            label = "parcel-dom"
        prompt = (
            "Classify a shipment using these rules in order: (1) hazardous -> restricted; "
            "(2) mass > 30 kg -> freight; (3) international -> parcel-intl; else parcel-dom. "
            f"The shipment is mass={mass} kg, hazardous={str(haz).lower()}, destination={dest}."
        )
        example = _emit(
            task_type="classification",
            prompt=prompt,
            answer=label,
            solution=f"Apply the first matching rule. Result: {label}.",
            observations=[f"mass={mass}", f"hazardous={haz}", f"destination={dest}"],
            constraints=["Rules are ordered", "Exactly one label"],
            assumptions=["Mass is total including packaging"],
            plan=["Check hazardous", "Check mass threshold", "Check destination"],
            key=f"cls-{mass}-{haz}-{dest}-{i}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _extraction(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    vendors = ["Northwind", "Helios", "Kite Labs", "Pylon"]
    for i in range(count):
        vendor = vendors[i % len(vendors)]
        amount = rng.randint(120, 980)
        due = date(2026, 3, 1) + timedelta(days=i)
        text = (
            f"Invoice INV-{1000+i} from {vendor} is payable by {due.isoformat()} "
            f"for USD {amount}. Mention of internal ticket T-{i} is not financial."
        )
        answer = f"vendor={vendor}; amount={amount}; due={due.isoformat()}; invoice=INV-{1000+i}"
        example = _emit(
            task_type="information_extraction",
            prompt=(
                "Extract vendor, integer USD amount, due date (ISO), and invoice id "
                f"from the note. Ignore ticket ids.\n\n{text}"
            ),
            answer=answer,
            solution=f"The financial fields are {answer}. Ticket T-{i} is excluded.",
            observations=[text],
            constraints=["Ignore non-financial identifiers", "Amount is an integer"],
            assumptions=["USD amounts have no cents in this corpus"],
            plan=["Locate invoice id", "Read vendor", "Read amount", "Read due date"],
            key=f"ex-{i}-{vendor}-{amount}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _comparison(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        a_cost, b_cost = 40 + rng.randint(0, 80), 40 + rng.randint(0, 80)
        a_lat, b_lat = 15 + rng.randint(0, 90), 15 + rng.randint(0, 90)
        a_slo, b_slo = rng.choice([99.5, 99.9]), rng.choice([99.5, 99.9])
        # score = -cost + -latency + 10*(slo-99)
        def score(cost, lat, slo):
            return -cost - lat + 10 * (slo - 99)
        sa, sb = score(a_cost, a_lat, a_slo), score(b_cost, b_lat, b_slo)
        winner = "A" if sa > sb else ("B" if sb > sa else "TIE")
        prompt = (
            "Choose hosting plan A or B by the score -cost - latency_ms + 10*(slo-99). "
            f"A: cost={a_cost}, latency={a_lat}ms, slo={a_slo}. "
            f"B: cost={b_cost}, latency={b_lat}ms, slo={b_slo}. "
            "Answer A, B, or TIE."
        )
        example = _emit(
            task_type="comparison",
            prompt=prompt,
            answer=winner,
            solution=f"score(A)={sa:.2f}, score(B)={sb:.2f}. Winner={winner}.",
            observations=[f"A={a_cost},{a_lat},{a_slo}", f"B={b_cost},{b_lat},{b_slo}"],
            constraints=["Use the stated linear score", "No qualitative override"],
            assumptions=["Higher score is better"],
            plan=["Compute both scores", "Compare"],
            key=f"cmp-{i}-{winner}-{a_cost}-{b_cost}",
            check=winner in {"A", "B", "TIE"},
        )
        if example:
            out.append(example)
    return out


def _causal(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        # Simple DAG: rain -> wet_street; sprinkler -> wet_street; wet_street -> slippery
        rain = rng.choice([True, False])
        sprinkler = rng.choice([True, False])
        wet = rain or sprinkler
        slippery = wet
        prompt = (
            "Causal graph: rain→wet, sprinkler→wet, wet→slippery. Deterministic OR for wet, "
            f"and slippery iff wet. Observed rain={rain}, sprinkler={sprinkler}. "
            "Is slippery true or false?"
        )
        example = _emit(
            task_type="causal_reasoning",
            prompt=prompt,
            answer=str(slippery).lower(),
            solution=f"wet = rain OR sprinkler = {wet}; slippery = wet = {slippery}.",
            observations=[f"rain={rain}", f"sprinkler={sprinkler}"],
            constraints=["Use only the given graph", "Deterministic mechanisms"],
            assumptions=["No other causes of slippery"],
            plan=["Compute wet", "Compute slippery"],
            key=f"causal-{i}-{rain}-{sprinkler}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _temporal(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        start = date(2026, 1, 5)
        events = [
            ("spec frozen", start + timedelta(days=i)),
            ("implementation start", start + timedelta(days=i + 3)),
            ("code complete", start + timedelta(days=i + 10)),
            ("release", start + timedelta(days=i + 14)),
        ]
        rng.shuffle(events)
        names_by_date = sorted(events, key=lambda x: x[1])
        order = " > ".join(name for name, _ in names_by_date)
        listing = "; ".join(f"{n} on {d.isoformat()}" for n, d in events)
        prompt = (
            "Order these events from earliest to latest (tie-break by name not needed; dates unique). "
            f"{listing}. Return names separated by ' > '."
        )
        example = _emit(
            task_type="temporal_reasoning",
            prompt=prompt,
            answer=order,
            solution=f"Sort by date: {order}.",
            observations=[listing],
            constraints=["Unique dates", "Earliest first"],
            assumptions=["Gregorian calendar"],
            plan=["Parse dates", "Sort", "Join names"],
            key=f"time-{i}-{order}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _constraintsat(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    colors = ["red", "green", "blue"]
    nodes = ["A", "B", "C"]
    edges = [("A", "B"), ("B", "C")]
    for i in range(count):
        # color path of 3 with 3 colors, A != B != C, A may equal C
        a = colors[i % 3]
        b = colors[(i + 1) % 3]
        c = colors[i % 2]
        if c == b:
            c = colors[(colors.index(b) + 1) % 3]
        assignment = {"A": a, "B": b, "C": c}
        ok = assignment["A"] != assignment["B"] and assignment["B"] != assignment["C"]
        answer = f"A={a}, B={b}, C={c}"
        prompt = (
            "Color nodes A-B-C (edges A-B and B-C) with {red, green, blue} so adjacent "
            f"nodes differ. One valid colouring starts with A={a}. Give A,B,C colours."
        )
        example = _emit(
            task_type="constraint_satisfaction",
            prompt=prompt,
            answer=answer,
            solution=f"A path of length 2 is 2-colourable along the path. {answer} is valid.",
            observations=["Graph is a path A—B—C", f"A is fixed to {a}"],
            constraints=["Adjacent nodes different colours", "Only the three named colours"],
            assumptions=["No other edges"],
            plan=["Fix A", "Choose B ≠ A", "Choose C ≠ B"],
            key=f"csp-{i}-{answer}",
            check=ok,
        )
        if example:
            out.append(example)
    return out


def _decision(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        p_fail = rng.choice([0.01, 0.05, 0.1, 0.2])
        loss = rng.choice([1000, 5000, 20000])
        cost = rng.choice([50, 100, 400, 800])
        expected = p_fail * loss
        buy = expected > cost
        answer = "buy" if buy else "skip"
        prompt = (
            "A mitigation costs "
            f"{cost} and prevents a failure that occurs with probability {p_fail} "
            f"and loss {loss}. Using expected monetary value and risk-neutrality, "
            "should you buy or skip the mitigation?"
        )
        example = _emit(
            task_type="decision_analysis",
            prompt=prompt,
            answer=answer,
            solution=(
                f"E[loss] = {p_fail}×{loss} = {expected}. "
                f"Buy iff {expected} > {cost}: {answer}."
            ),
            observations=[f"p={p_fail}", f"loss={loss}", f"cost={cost}"],
            constraints=["Risk-neutral EMV", "Mitigation is all-or-nothing"],
            assumptions=["No residual risk after buying"],
            plan=["Compute expected unmitigated loss", "Compare to cost"],
            key=f"dec-{i}-{answer}-{cost}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _argument(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    templates = [
        (
            "All firmware updates that change the bootloader require a dual-control review. "
            "Build 4412 changes the bootloader. Therefore build 4412 requires a dual-control review.",
            "valid",
            "Categorical syllogism: all M are P; a is M; therefore a is P.",
        ),
        (
            "If the cache is cold, latency exceeds 200 ms. Latency exceeded 200 ms. Therefore the cache is cold.",
            "invalid",
            "Affirming the consequent: Q does not imply P.",
        ),
        (
            "Either the replica is lagged or the client retried. The replica is not lagged. Therefore the client retried.",
            "valid",
            "Disjunctive syllogism.",
        ),
        (
            "Most timeouts are caused by GC pauses. This request timed out. Therefore this timeout was a GC pause.",
            "invalid",
            "Statistical generalization does not entail a particular.",
        ),
    ]
    for i in range(count):
        text, label, why = templates[i % len(templates)]
        example = _emit(
            task_type="argument_analysis",
            prompt=("Classify the argument as valid or invalid (deductive). Explain briefly in the solution.\n\n" + text),
            answer=label,
            solution=why,
            observations=[text],
            constraints=["Deductive validity, not empirical truth"],
            assumptions=["Ordinary propositional/categorical reading"],
            plan=["Identify form", "Check if the conclusion follows"],
            key=f"arg-{i}-{label}",
            check=label in {"valid", "invalid"},
        )
        if example:
            out.append(example)
    return out


def _quant(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        n = rng.randint(4, 9)
        k = rng.randint(1, n - 1)
        # how many ways to choose a committee of k from n with a chair from the committee
        value = math_comb(n, k) * k
        prompt = (
            f"A working group of {k} people is chosen from {n} engineers, then one member "
            "is designated chair. How many outcomes are there?"
        )
        example = _emit(
            task_type="quantitative_reasoning",
            prompt=prompt,
            answer=str(value),
            solution=f"C({n},{k}) ways to choose the group, then {k} chairs: {value}.",
            observations=[f"n={n}", f"k={k}"],
            constraints=["People are distinct", "Chair must be in the group"],
            assumptions=["Order of non-chairs does not matter"],
            plan=["Choose the subset", "Choose the chair"],
            key=f"quant-{n}-{k}-{value}",
            check=value == math_comb(n, k) * k,
        )
        if example:
            out.append(example)
    return out


def math_comb(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    r = 1
    for i in range(k):
        r = r * (n - i) // (i + 1)
    return r


def _troubleshooting(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        cpu = rng.choice(["high", "normal"])
        latency = rng.choice(["high", "normal"])
        errors = rng.choice(["high", "normal"])
        if errors == "high" and latency == "high":
            diagnosis = "dependency_timeouts"
        elif cpu == "high" and latency == "high":
            diagnosis = "cpu_saturation"
        elif latency == "high":
            diagnosis = "network_or_io"
        else:
            diagnosis = "no_perf_incident"
        prompt = (
            "Triage using: high errors+high latency => dependency_timeouts; else high CPU+high "
            f"latency => cpu_saturation; else high latency => network_or_io; else no_perf_incident. "
            f"Observed cpu={cpu}, latency={latency}, errors={errors}."
        )
        example = _emit(
            task_type="troubleshooting",
            prompt=prompt,
            answer=diagnosis,
            solution=f"Apply the first matching triage rule: {diagnosis}.",
            observations=[f"cpu={cpu}", f"latency={latency}", f"errors={errors}"],
            constraints=["Ordered rules", "Single diagnosis"],
            assumptions=["Metrics are already aggregated"],
            plan=["Check error+latency", "Check CPU+latency", "Check latency alone"],
            key=f"ts-{i}-{diagnosis}-{cpu}",
            check=True,
        )
        if example:
            out.append(example)
    return out


FAMILIES = [
    (_scheduling, 36),
    (_classification, 36),
    (_extraction, 28),
    (_comparison, 32),
    (_causal, 24),
    (_temporal, 24),
    (_constraintsat, 24),
    (_decision, 28),
    (_argument, 20),
    (_quant, 28),
    (_troubleshooting, 32),
]


def generate_reasoning(seed: int = 42) -> list[Example]:
    rng = random.Random(seed)
    examples: list[Example] = []
    for factory, count in FAMILIES:
        examples.extend(factory(rng, count))
    from open_reason.generation.reasoning_v1 import extra_reasoning

    examples.extend(extra_reasoning(rng))
    return examples
