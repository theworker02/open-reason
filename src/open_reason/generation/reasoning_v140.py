"""v1.4.0 reasoning: distinct checkable scenarios, not paraphrases of v102."""

from __future__ import annotations

import itertools
import random

from open_reason.generation.reasoning import _emit
from open_reason.models import Example


def extra_reasoning_v140(rng: random.Random) -> list[Example]:
    out: list[Example] = []
    out.extend(_knapsack(rng, 18))
    out.extend(_bfs_dist(rng, 16))
    out.extend(_lru_hits(rng, 16))
    out.extend(_hamming(rng, 16))
    out.extend(_two_sum_count(rng, 16))
    out.extend(_round_robin(rng, 14))
    out.extend(_tax_bracket(rng, 14))
    out.extend(_weighted_avg(rng, 16))
    out.extend(_deadline_miss(rng, 16))
    out.extend(_topo_ok(rng, 16))
    out.extend(_lis_len(rng, 14))
    out.extend(_next_fit(rng, 16))
    out.extend(_interval_select(rng, 16))
    out.extend(_coin_change(rng, 14))
    out.extend(_majority_el(rng, 14))
    return out


def _knapsack(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        weights = [rng.randint(1, 5) for _ in range(4)]
        values = [rng.randint(1, 9) for _ in range(4)]
        cap = rng.randint(6, 12)
        best = 0
        for mask in range(16):
            w = v = 0
            for j in range(4):
                if mask & (1 << j):
                    w += weights[j]
                    v += values[j]
            if w <= cap:
                best = max(best, v)
        prompt = (
            f"0/1 knapsack: weights {weights}, values {values}, capacity {cap}. "
            "Maximum value (items chosen at most once)?"
        )
        example = _emit(
            task_type="planning",
            prompt=prompt,
            answer=str(best),
            solution=f"Enumerate 16 subsets; best feasible value is {best}.",
            observations=[f"weights={weights}", f"values={values}", f"cap={cap}"],
            constraints=["0/1, no fractions"],
            assumptions=["Independent items"],
            plan=["Enumerate subsets", "Keep feasible max value"],
            key=f"v140-ks-{i}-{cap}-{weights}-{values}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _bfs_dist(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    edges_opts = [
        [(0, 1), (1, 2), (2, 3), (0, 3)],
        [(0, 1), (1, 2), (0, 2), (2, 3)],
        [(0, 1), (1, 3), (3, 2), (0, 2)],
    ]
    for i in range(count):
        edges = edges_opts[i % 3]
        start, goal = 0, 3
        adj: dict[int, list[int]] = {0: [], 1: [], 2: [], 3: []}
        for a, b in edges:
            adj[a].append(b)
            adj[b].append(a)
        q = [start]
        dist = {start: 0}
        seen = {start}
        while q:
            u = q.pop(0)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    dist[v] = dist[u] + 1
                    q.append(v)
        d = dist.get(goal, -1)
        prompt = (
            f"Undirected graph on nodes 0-3 with edges {edges}. "
            f"BFS distance from {start} to {goal} (unweighted)?"
        )
        example = _emit(
            task_type="planning",
            prompt=prompt,
            answer=str(d),
            solution=f"BFS layers give dist[{goal}]={d}.",
            observations=[f"edges={edges}"],
            constraints=["Unweighted undirected", "BFS"],
            assumptions=["Connected enough to reach 3"],
            plan=["Breadth-first search"],
            key=f"v140-bfs-{i}-{d}-{edges}",
            check=d >= 0,
        )
        if example:
            out.append(example)
    return out


def _lru_hits(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        cap = rng.choice([2, 3])
        reqs = [rng.randint(1, 4) for _ in range(7)]
        cache: list[int] = []
        hits = 0
        for key in reqs:
            if key in cache:
                hits += 1
                cache.remove(key)
                cache.append(key)
            else:
                if len(cache) >= cap:
                    cache.pop(0)
                cache.append(key)
        prompt = (
            f"An LRU cache of capacity {cap} sees requests {reqs}. "
            "How many hits (key already present before the access)?"
        )
        example = _emit(
            task_type="temporal_reasoning",
            prompt=prompt,
            answer=str(hits),
            solution=f"Simulate LRU; hits={hits}.",
            observations=[f"cap={cap}", f"reqs={reqs}"],
            constraints=["LRU eviction of least recently used"],
            assumptions=["Empty cache at start"],
            plan=["Walk requests", "Count hits", "Update recency"],
            key=f"v140-lru-{i}-{cap}-{hits}-{reqs}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _hamming(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        n = 8
        a = [rng.randint(0, 1) for _ in range(n)]
        b = [rng.randint(0, 1) for _ in range(n)]
        d = sum(x != y for x, y in zip(a, b, strict=True))
        prompt = f"Hamming distance between bitstrings {a} and {b}?"
        example = _emit(
            task_type="comparison",
            prompt=prompt,
            answer=str(d),
            solution=f"Positions that differ: {d}.",
            observations=[f"a={a}", f"b={b}"],
            constraints=["Equal length", "Bit alphabet"],
            assumptions=["Index-aligned"],
            plan=["Count mismatches"],
            key=f"v140-ham-{i}-{d}-{''.join(map(str, a))}-{''.join(map(str, b))}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _two_sum_count(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        xs = [rng.randint(1, 9) for _ in range(6)]
        target = rng.randint(6, 14)
        n = 0
        for a, b in itertools.combinations(range(len(xs)), 2):
            if xs[a] + xs[b] == target:
                n += 1
        prompt = (
            f"How many unordered index pairs in {xs} sum to {target}? "
            "Count each pair of distinct indices once."
        )
        example = _emit(
            task_type="quantitative_reasoning",
            prompt=prompt,
            answer=str(n),
            solution=f"There are {n} pairs summing to {target}.",
            observations=[f"xs={xs}", f"target={target}"],
            constraints=["Distinct indices", "Unordered pairs"],
            assumptions=["Values may repeat"],
            plan=["Enumerate pairs"],
            key=f"v140-ts-{i}-{target}-{n}-{xs}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _round_robin(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        wins, draws, losses = rng.randint(0, 5), rng.randint(0, 4), rng.randint(0, 5)
        pts = 3 * wins + draws
        prompt = (
            f"A team has {wins} wins, {draws} draws, {losses} losses. "
            "Points with win=3, draw=1, loss=0?"
        )
        example = _emit(
            task_type="quantitative_reasoning",
            prompt=prompt,
            answer=str(pts),
            solution=f"3·{wins}+{draws}={pts}.",
            observations=[f"W={wins}", f"D={draws}", f"L={losses}"],
            constraints=["Standard football scoring"],
            assumptions=["No extra time bonuses"],
            plan=["3W+D"],
            key=f"v140-rr-{i}-{wins}-{draws}-{losses}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _tax_bracket(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        income = rng.choice([8, 15, 25, 40, 60]) * 1000
        # 0-10k: 10%, 10-30k: 20%, 30k+: 30%
        if income <= 10000:
            tax = int(0.10 * income)
        elif income <= 30000:
            tax = int(0.10 * 10000 + 0.20 * (income - 10000))
        else:
            tax = int(0.10 * 10000 + 0.20 * 20000 + 0.30 * (income - 30000))
        prompt = (
            f"Tax: 10% on the first 10000, 20% on the next 20000, 30% above 30000. "
            f"Income={income}. Tax as a whole-currency integer (no rounding up)?"
        )
        example = _emit(
            task_type="quantitative_reasoning",
            prompt=prompt,
            answer=str(tax),
            solution=f"Bracket arithmetic yields {tax}.",
            observations=[f"income={income}"],
            constraints=["Marginal brackets", "Floor via int() of the stated percents"],
            assumptions=["No deductions"],
            plan=["Apply each band"],
            key=f"v140-tax-{i}-{income}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _weighted_avg(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        scores = [rng.randint(50, 100) for _ in range(3)]
        weights = [rng.choice([1, 2, 3]) for _ in range(3)]
        num = sum(s * w for s, w in zip(scores, weights, strict=True))
        den = sum(weights)
        avg = num / den
        prompt = (
            f"Weighted average of scores {scores} with weights {weights}?"
        )
        example = _emit(
            task_type="quantitative_reasoning",
            prompt=prompt,
            answer=f"{avg:.10g}",
            solution=f"Σ(score·weight)/Σweight={avg}.",
            observations=[f"scores={scores}", f"weights={weights}"],
            constraints=["Weights are positive integers"],
            assumptions=["No extra scaling"],
            plan=["Dot product then divide"],
            key=f"v140-wavg-{i}-{scores}-{weights}",
            check=den > 0,
        )
        if example:
            out.append(example)
    return out


def _deadline_miss(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        durs = [rng.randint(1, 5) for _ in range(4)]
        deadlines = [rng.randint(4, 16) for _ in range(4)]
        t = 0
        miss = 0
        for d, due in zip(durs, deadlines, strict=True):
            t += d
            if t > due:
                miss += 1
        prompt = (
            f"Jobs run in listed order. Durations {durs}, deadlines {deadlines} "
            "(finish time must be ≤ deadline). How many jobs miss?"
        )
        example = _emit(
            task_type="temporal_reasoning",
            prompt=prompt,
            answer=str(miss),
            solution=f"Cumulative finish times miss {miss} deadlines.",
            observations=[f"durations={durs}", f"deadlines={deadlines}"],
            constraints=["Fixed order", "No preemption"],
            assumptions=["Start at t=0"],
            plan=["Accumulate finish times", "Compare to deadlines"],
            key=f"v140-dead-{i}-{miss}-{durs}-{deadlines}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _topo_ok(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        order = list(rng.sample(range(4), 4))
        # edges: 0->1, 2->3
        ok = order.index(0) < order.index(1) and order.index(2) < order.index(3)
        prompt = (
            f"Is permutation {order} a topological order of DAG edges 0→1 and 2→3? "
            "Answer yes or no."
        )
        ans = "yes" if ok else "no"
        example = _emit(
            task_type="constraint_satisfaction",
            prompt=prompt,
            answer=ans,
            solution=f"Check both edges against positions → {ans}.",
            observations=[f"order={order}"],
            constraints=["Directed edges must go left-to-right in the permutation"],
            assumptions=["Only those two edges"],
            plan=["Compare indices"],
            key=f"v140-topo-{i}-{ans}-{''.join(map(str, order))}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _lis_len(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        xs = [rng.randint(1, 9) for _ in range(6)]
        n = len(xs)
        dp = [1] * n
        for a in range(n):
            for b in range(a):
                if xs[b] < xs[a]:
                    dp[a] = max(dp[a], dp[b] + 1)
        best = max(dp)
        prompt = (
            f"Length of a longest strictly increasing subsequence of {xs}?"
        )
        example = _emit(
            task_type="planning",
            prompt=prompt,
            answer=str(best),
            solution=f"DP LIS length={best}.",
            observations=[f"xs={xs}"],
            constraints=["Strictly increasing", "Not necessarily contiguous"],
            assumptions=["Any subsequence of indices"],
            plan=["O(n^2) LIS DP"],
            key=f"v140-lis-{i}-{best}-{xs}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _next_fit(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        cap = rng.choice([10, 12])
        items = [rng.randint(2, cap - 1) for _ in range(5)]
        bins = 0
        rem = 0
        for w in items:
            if bins == 0 or w > rem:
                bins += 1
                rem = cap - w
            else:
                rem -= w
        prompt = (
            f"Pack items {items} into bins of capacity {cap} using **next-fit** "
            "(only the current bin; never reopen). How many bins?"
        )
        example = _emit(
            task_type="planning",
            prompt=prompt,
            answer=str(bins),
            solution=f"Next-fit uses {bins} bins.",
            observations=[f"cap={cap}", f"items={items}"],
            constraints=["Next-fit, not first-fit"],
            assumptions=["Items fit individually"],
            plan=["Keep one open bin", "Open a new bin when the item does not fit"],
            key=f"v140-nf-{i}-{cap}-{bins}-{items}",
            check=bins >= 1,
        )
        if example:
            out.append(example)
    return out


def _interval_select(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        iv = []
        t = 0
        for _ in range(4):
            a = t + rng.randint(0, 2)
            b = a + rng.randint(2, 4)
            iv.append((a, b))
            t = a + rng.randint(0, 2)
        chosen = []
        last = -10**9
        for a, b in sorted(iv, key=lambda p: p[1]):
            if a >= last:
                chosen.append((a, b))
                last = b
        n = len(chosen)
        prompt = (
            f"Select a maximum number of non-overlapping half-open intervals from {iv} "
            "by earliest finish time. How many are kept?"
        )
        example = _emit(
            task_type="planning",
            prompt=prompt,
            answer=str(n),
            solution=f"Earliest-finish greedy keeps {chosen}; n={n}.",
            observations=[f"intervals={iv}"],
            constraints=["Non-overlapping: next start ≥ previous finish", "Half-open"],
            assumptions=["Value is count, not weight"],
            plan=["Sort by finish", "Greedy take"],
            key=f"v140-is-{i}-{n}-{iv}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _coin_change(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    coins = [25, 10, 5, 1]
    for i in range(count):
        amount = rng.randint(1, 99)
        left = amount
        used = 0
        for c in coins:
            n, left = divmod(left, c)
            used += n
        prompt = (
            f"US coins {coins} (greedy). Minimum coins to make {amount} cents?"
        )
        example = _emit(
            task_type="quantitative_reasoning",
            prompt=prompt,
            answer=str(used),
            solution=f"Canonical greedy uses {used} coins.",
            observations=[f"amount={amount}"],
            constraints=["Greedy canonical coin system"],
            assumptions=["Unlimited supply"],
            plan=["Take as many of each denomination as possible, largest first"],
            key=f"v140-coin-{i}-{amount}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _majority_el(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        maj = rng.choice(["A", "B", "C"])
        others = [x for x in "ABC" if x != maj]
        seq = [maj] * 5 + [others[0]] * 2 + [others[1]] * 2
        rng.shuffle(seq)
        winner = max(set(seq), key=seq.count)
        prompt = (
            f"Sequence {seq}. Which label is the strict plurality (most frequent)?"
        )
        example = _emit(
            task_type="classification",
            prompt=prompt,
            answer=winner,
            solution=f"Counts favor {winner}.",
            observations=[f"seq={seq}"],
            constraints=["Plurality, not majority of 50%+1 required"],
            assumptions=["Ties broken by Python max(set, key=count) — unique here"],
            plan=["Count frequencies"],
            key=f"v140-maj-{i}-{winner}-{''.join(seq)}",
            check=seq.count(winner) > len(seq) // 3,
        )
        if example:
            out.append(example)
    return out
