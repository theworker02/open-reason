"""v1.0.2 reasoning: distinct checkable scenarios, not paraphrases of v1 banks."""

from __future__ import annotations

import itertools
import random

from open_reason.generation.reasoning import _emit
from open_reason.models import Example


def extra_reasoning_v102(rng: random.Random) -> list[Example]:
    out: list[Example] = []
    out.extend(_bin_pack(rng, 20))
    out.extend(_shortest_unique(rng, 18))
    out.extend(_majority(rng, 16))
    out.extend(_interval_merge_count(rng, 16))
    out.extend(_token_budget(rng, 18))
    out.extend(_gate_order(rng, 16))
    out.extend(_inventory_cover(rng, 16))
    out.extend(_parity_votes(rng, 16))
    return out


def _bin_pack(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        cap = rng.choice([10, 12, 15])
        items = [rng.randint(2, cap - 1) for _ in range(4)]
        # first-fit decreasing
        sizes = sorted(items, reverse=True)
        bins: list[int] = []
        for w in sizes:
            placed = False
            for b, rem in enumerate(bins):
                if rem >= w:
                    bins[b] -= w
                    placed = True
                    break
            if not placed:
                bins.append(cap - w)
        n = len(bins)
        prompt = (
            f"Pack items {items} into bins of capacity {cap} using first-fit decreasing. "
            "How many bins are used?"
        )
        example = _emit(
            task_type="planning",
            prompt=prompt,
            answer=str(n),
            solution=f"Sort descending {sizes}; first-fit uses {n} bins.",
            observations=[f"capacity={cap}", f"items={items}"],
            constraints=["First-fit decreasing", "Do not split items"],
            assumptions=["Items fit individually"],
            plan=["Sort descending", "Place each item in the first bin with room"],
            key=f"ffd-{i}-{cap}-{'-'.join(map(str, items))}",
            check=n >= 1,
        )
        if example:
            out.append(example)
    return out


def _shortest_unique(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    names = ["Ivy", "Jules", "Kiran", "Lane", "Mira", "Nico", "Omar", "Pia"]
    for i in range(count):
        k = 4
        chosen = names[i % 3 : i % 3 + k]
        costs = {name: rng.randint(2, 9) for name in chosen}
        must = {chosen[0], chosen[1]}
        best = None
        best_cost = 10**9
        for r in range(2, k + 1):
            for combo in itertools.combinations(chosen, r):
                if not must.issubset(combo):
                    continue
                c = sum(costs[n] for n in combo)
                if c < best_cost:
                    best_cost = c
                    best = combo
        assert best is not None
        prompt = (
            f"Select a team from {chosen} with costs {costs}. "
            f"Must include {sorted(must)}. Minimize total cost. What is that cost?"
        )
        example = _emit(
            task_type="constraint_satisfaction",
            prompt=prompt,
            answer=str(best_cost),
            solution=f"Cheapest feasible set {list(best)} costs {best_cost}.",
            observations=[f"costs={costs}", f"required={sorted(must)}"],
            constraints=["Required members", "Minimize sum"],
            assumptions=["No other constraints"],
            plan=["Enumerate subsets containing required names", "Pick min cost"],
            key=f"team-{i}-{best_cost}-{'-'.join(chosen)}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _majority(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    labels = ["accept", "reject", "defer"]
    for i in range(count):
        votes = [rng.choice(labels) for _ in range(7)]
        counts = {lab: votes.count(lab) for lab in labels}
        winner = max(labels, key=lambda lab: (counts[lab], -labels.index(lab)))
        prompt = (
            f"Seven reviewers vote {votes}. Majority (ties broken by accept>reject>defer). "
            "What is the outcome?"
        )
        example = _emit(
            task_type="classification",
            prompt=prompt,
            answer=winner,
            solution=f"Counts {counts}; winner {winner}.",
            observations=[f"votes={votes}"],
            constraints=["Plurality", "Fixed tie-break order"],
            assumptions=["All votes valid"],
            plan=["Count labels", "Apply tie-break"],
            key=f"maj-{i}-{winner}-{''.join(v[0] for v in votes)}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _interval_merge_count(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        start = rng.randint(0, 5)
        spans = []
        t = start
        for _ in range(3):
            a = t + rng.randint(0, 2)
            b = a + rng.randint(1, 4)
            spans.append((a, b))
            t = a + rng.randint(0, 3)
        merged: list[tuple[int, int]] = []
        for a, b in sorted(spans):
            if not merged or a > merged[-1][1]:
                merged.append((a, b))
            else:
                merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        n = len(merged)
        prompt = (
            f"Merge overlapping half-open intervals {spans} on the integer line. "
            "How many disjoint intervals remain?"
        )
        example = _emit(
            task_type="temporal_reasoning",
            prompt=prompt,
            answer=str(n),
            solution=f"Merged {merged}; count={n}.",
            observations=[f"intervals={spans}"],
            constraints=["Merge if they touch or overlap", "Integer endpoints"],
            assumptions=["Half-open [a,b) treated as overlapping when a < prev_b"],
            plan=["Sort", "Sweep merge"],
            key=f"iv-{i}-{n}-{spans}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _token_budget(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        budget = rng.choice([32, 48, 64])
        chunks = [rng.randint(6, 20) for _ in range(5)]
        used = 0
        kept = 0
        for c in chunks:
            if used + c <= budget:
                used += c
                kept += 1
            else:
                break
        prompt = (
            f"A context window has {budget} tokens. Pack chunks {chunks} in order, "
            "skipping none except by stopping when the next chunk would overflow. "
            "How many chunks are kept?"
        )
        example = _emit(
            task_type="planning",
            prompt=prompt,
            answer=str(kept),
            solution=f"Greedy prefix uses {used} tokens and keeps {kept} chunks.",
            observations=[f"budget={budget}", f"chunks={chunks}"],
            constraints=["Preserve order", "No skipping in the middle"],
            assumptions=["Each chunk is atomic"],
            plan=["Add chunks until the next would exceed budget"],
            key=f"tok-{i}-{budget}-{kept}-{'-'.join(map(str, chunks))}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _gate_order(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        n = 4
        perm = list(rng.sample(range(n), n))
        # jobs A B C D with deps: 0 before 2, 1 before 3
        ok = perm.index(0) < perm.index(2) and perm.index(1) < perm.index(3)
        prompt = (
            f"Jobs 0,1,2,3 run in order {perm}. Constraints: 0 before 2, and 1 before 3. "
            "Is the order valid? Answer yes or no."
        )
        ans = "yes" if ok else "no"
        example = _emit(
            task_type="constraint_satisfaction",
            prompt=prompt,
            answer=ans,
            solution=f"Positions: 0@{perm.index(0)}, 2@{perm.index(2)}, 1@{perm.index(1)}, 3@{perm.index(3)} → {ans}.",
            observations=[f"order={perm}"],
            constraints=["Two precedence edges"],
            assumptions=["Total order given"],
            plan=["Check both precedence constraints"],
            key=f"gate-{i}-{ans}-{''.join(map(str, perm))}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _inventory_cover(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        demand = [rng.randint(1, 5) for _ in range(3)]
        stock = [rng.randint(0, 6) for _ in range(3)]
        short = sum(max(0, d - s) for d, s in zip(demand, stock, strict=True))
        prompt = (
            f"SKUs have demand {demand} and on-hand {stock}. "
            "Total units short (unmet demand)?"
        )
        example = _emit(
            task_type="quantitative_reasoning",
            prompt=prompt,
            answer=str(short),
            solution="shortfall = sum(max(0, demand-stock)) = " + str(short) + ".",
            observations=[f"demand={demand}", f"stock={stock}"],
            constraints=["No substitution across SKUs"],
            assumptions=["Integer units"],
            plan=["Per SKU max(0, d-s)", "Sum"],
            key=f"inv-{i}-{short}-{demand}-{stock}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _parity_votes(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        bits = [rng.randint(0, 1) for _ in range(8)]
        parity = sum(bits) % 2
        prompt = (
            f"Eight bits {bits} are sent with even parity. "
            "What parity bit should be appended (0 or 1) so the nine-bit string has even parity?"
        )
        example = _emit(
            task_type="classification",
            prompt=prompt,
            answer=str(parity),
            solution=f"Sum={sum(bits)}; even parity bit={parity}.",
            observations=[f"bits={bits}"],
            constraints=["Even parity over the eight data bits plus the appended bit"],
            assumptions=["No errors yet"],
            plan=["Sum bits mod 2"],
            key=f"par-{i}-{parity}-{''.join(map(str, bits))}",
            check=True,
        )
        if example:
            out.append(example)
    return out
