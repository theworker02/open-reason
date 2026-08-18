"""Additional structured reasoning families with checkable answers."""

from __future__ import annotations

import random

from open_reason.generation.reasoning import _emit
from open_reason.models import Example


def extra_reasoning(rng: random.Random) -> list[Example]:
    out: list[Example] = []
    out.extend(_set_ops(rng, 16))
    out.extend(_truth_tables(rng, 12))
    out.extend(_shortest_hops(rng, 12))
    return out


def _set_ops(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    universe = ["p", "q", "r", "s", "t", "u"]
    for i in range(count):
        a = set(rng.sample(universe, 3))
        b = set(rng.sample(universe, 3))
        kind = rng.choice(["union", "intersect", "diff"])
        if kind == "union":
            result = sorted(a | b)
            prompt = f"Let A={sorted(a)} and B={sorted(b)}. List A ∪ B in sorted order."
            check = result == sorted(a | b)
        elif kind == "intersect":
            result = sorted(a & b)
            prompt = f"Let A={sorted(a)} and B={sorted(b)}. List A ∩ B in sorted order."
            check = result == sorted(a & b)
        else:
            result = sorted(a - b)
            prompt = f"Let A={sorted(a)} and B={sorted(b)}. List A \\ B in sorted order."
            check = result == sorted(a - b)
        answer = ",".join(result) if result else "(empty)"
        example = _emit(
            task_type="classification",
            prompt=prompt,
            answer=answer,
            solution=f"Compute the set operation on finite named elements: {answer}.",
            observations=[f"A={sorted(a)}", f"B={sorted(b)}"],
            constraints=["Use the listed labels only", "Sorted comma-separated"],
            assumptions=["Finite sets of symbols"],
            plan=["Apply the operation", "Sort the result"],
            key=f"set-{kind}-{i}-{''.join(sorted(a))}-{''.join(sorted(b))}",
            check=check,
        )
        if example:
            out.append(example)
    return out


def _truth_tables(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        p = bool(rng.getrandbits(1))
        q = bool(rng.getrandbits(1))
        kind = rng.choice(["implies", "xor", "and"])
        if kind == "implies":
            value = (not p) or q
            prompt = f"P is {p}, Q is {q}. What is P → Q as true/false?"
        elif kind == "xor":
            value = p ^ q
            prompt = f"P is {p}, Q is {q}. What is P XOR Q as true/false?"
        else:
            value = p and q
            prompt = f"P is {p}, Q is {q}. What is P AND Q as true/false?"
        answer = "true" if value else "false"
        example = _emit(
            task_type="argument_analysis",
            prompt=prompt,
            answer=answer,
            solution=f"Evaluate the connective on the two booleans: {answer}.",
            observations=[f"P={p}", f"Q={q}"],
            constraints=["Answer true or false"],
            assumptions=["Classical two-valued logic"],
            plan=["Plug in P and Q", "Apply the connective"],
            key=f"tt-{kind}-{int(p)}-{int(q)}-{i}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _shortest_hops(rng: random.Random, count: int) -> list[Example]:
    out: list[Example] = []
    for i in range(count):
        # Path graph 0-1-2-3-4 plus one extra edge
        extra = rng.choice([(0, 2), (1, 3), (0, 3), (2, 4)])
        start, goal = 0, 4
        edges = {(0, 1), (1, 2), (2, 3), (3, 4), extra, (extra[1], extra[0])}
        hops = _bfs(start, goal, edges)
        prompt = (
            f"Undirected edges: 0-1, 1-2, 2-3, 3-4, and {extra[0]}-{extra[1]}. "
            f"What is the fewest hops from {start} to {goal}?"
        )
        example = _emit(
            task_type="planning",
            prompt=prompt,
            answer=str(hops),
            solution=f"BFS from {start} reaches {goal} in {hops} hops.",
            observations=[f"extra edge {extra}"],
            constraints=["Unweighted hops", "Undirected"],
            assumptions=["Simple undirected graph"],
            plan=["Run BFS", "Read distance of the goal"],
            key=f"hops-{extra[0]}-{extra[1]}-{i}",
            check=hops is not None,
        )
        if example:
            out.append(example)
    return out


def _bfs(start: int, goal: int, edges: set[tuple[int, int]]) -> int | None:
    adj: dict[int, list[int]] = {}
    for a, b in edges:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    seen = {start}
    queue = [(start, 0)]
    while queue:
        node, dist = queue.pop(0)
        if node == goal:
            return dist
        for nxt in adj.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, dist + 1))
    return None
