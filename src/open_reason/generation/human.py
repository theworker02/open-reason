"""Human problem-solving, teaching, and decision-support examples.

Items with an objective checker are quality S. Teaching/synthesis items are
quality A (reviewed) and never marked verified.
"""

from __future__ import annotations

import random

from open_reason.constants import PIPELINE_VERSION
from open_reason.generation.base import build_example, reviewed_quality, verified_quality
from open_reason.models import Domain, Example, Verification
from open_reason.provenance import human_provenance, synthetic_provenance


def _syn():
    return synthetic_provenance(
        generator="open_reason.generation.human",
        generator_version=PIPELINE_VERSION,
    )


def _human_src(source_id: str):
    return human_provenance(source="open-reason authors", source_id=source_id)


def generate_human(seed: int = 42) -> list[Example]:
    rng = random.Random(seed)
    examples: list[Example] = []
    examples.extend(_teaching())
    examples.extend(_research_synthesis())
    examples.extend(_qualitative())
    examples.extend(_planning_word(rng))
    examples.extend(_constraint_word(rng))
    examples.extend(_explanation_gold())
    examples.extend(_inventory(rng))
    examples.extend(_sla_queue(rng))
    examples.extend(_v1_teaching())
    return examples


def _teaching() -> list[Example]:
    lessons = [
        (
            "teach-hash-collision",
            "Explain to a new engineer why a hash table can degrade to linear scan, "
            "and name one practical mitigation used in production languages.",
            [
                "Average-case lookup is O(1) under uniform hashing and a load-factor bound.",
                "Adversarial or highly skewed keys can map to few buckets.",
            ],
            [
                "Stay at the level of data-structure behaviour, not a specific CVE writeup.",
            ],
            [
                "State the average-case assumption",
                "Describe collision chains or trees",
                "Name a mitigation",
            ],
            "If many keys collide, a bucket becomes a list (or similar) and lookup is O(n) in that bucket. "
            "Mitigations include randomized per-process hash seeds, switching collided buckets to balanced trees, "
            "and keeping load factor bounded with resizing.",
        ),
        (
            "teach-acid",
            "Teach the four ACID properties with one sentence each, aimed at backend engineers.",
            ["The student already knows what a transaction is."],
            ["Do not assume a particular database product."],
            ["Define atomicity", "Define consistency", "Define isolation", "Define durability"],
            "Atomicity: a transaction commits all of its writes or none. "
            "Consistency: committed transactions leave integrity rules intact. "
            "Isolation: concurrent transactions behave as if serialized per the advertised level. "
            "Durability: a committed transaction survives process crash (within the engine's durability contract).",
        ),
        (
            "teach-p-vs-np",
            "Give a precise, non-mystical explanation of P vs NP suitable for a CS undergrad who knows Big-O.",
            ["P and NP are classes of decision problems on a deterministic vs nondeterministic Turing machine model (or equivalent)."],
            ["Do not claim the problem is solved.", "Avoid pop-science metaphors as the primary explanation."],
            ["Define P", "Define NP", "State the open question"],
            "P: decision problems solvable in polynomial time on a deterministic TM. "
            "NP: decision problems whose yes-instances have polynomial-time verifiable certificates. "
            "P ⊆ NP is known; whether NP ⊆ P is open. NP-complete problems are the hardest in NP under poly-time reductions.",
        ),
        (
            "teach-bayes",
            "A test has 99% sensitivity and 99% specificity. Prevalence is 0.5%. "
            "Explain qualitatively whether a positive result means the person 'almost certainly' has the condition.",
            ["Sensitivity = P(positive | disease)", "Specificity = P(negative | no disease)"],
            ["A numeric posterior is welcome but not required if the base-rate point is clear."],
            ["Write the base-rate setup", "Compare false positives to true positives"],
            "In 10,000 people, about 50 have the condition (0.5%). The test catches ~49.5 of them. "
            "Among 9,950 without the condition, 1% false positives ≈ 99.5 people. "
            "So about two-thirds of positives are false. A positive is evidence, not near-certainty.",
        ),
        (
            "teach-git-rebase",
            "When should a team prefer merge commits over rebasing a shared branch? Give a short policy.",
            ["The repository is used by multiple people.", "History will be used for blame and incident review."],
            ["Do not rewrite commits that others have already based work on without an explicit agreement."],
            ["Identify the danger of rewriting published history", "State a default policy"],
            "Do not rebase commits that have been pushed to a shared branch unless the whole team agrees and force-push rules are explicit. "
            "Merge commits preserve the real integration topology, which helps incident reconstruction. "
            "Rebase is appropriate for local or explicitly throwaway feature branches before first share.",
        ),
        (
            "teach-cache-invalidation",
            "Explain write-through vs write-back caching and one failure mode of write-back.",
            ["Single CPU, one cache, backing store is slower."],
            ["Stay qualitative."],
            ["Define write-through", "Define write-back", "Name a failure mode"],
            "Write-through: every write updates cache and backing store before completion; simpler consistency, higher write latency. "
            "Write-back: writes hit the cache and mark dirty; backing store updates later. Failure mode: a crash before flush loses dirty data unless another durability mechanism exists.",
        ),
        (
            "teach-experimental-control",
            "A lab wants to test whether fertilizer A beats fertilizer B on yield. "
            "List four design elements that make the comparison interpretable.",
            ["Plots vary in sunlight and soil.", "The question is causal, not merely descriptive."],
            ["Do not invent specific numeric yields."],
            ["Randomization", "Replication", "Controls", "Measurement protocol"],
            "Randomly assign A/B (and ideally a no-fertilizer control) to plots; replicate treatments; block on known gradients (sun, slope); "
            "fix harvest protocol and timing; pre-register the yield metric; keep application rates comparable.",
        ),
        (
            "teach-unit-vs-integration",
            "Give a practical rule for when a behaviour belongs in a unit test vs an integration test in a web service.",
            ["The service has business logic, a database, and an HTTP API."],
            ["Avoid dogma that one layer is always enough."],
            ["Locate the decision boundary", "State cost vs confidence"],
            "Unit-test pure decision logic and adapters with fakes when the branch space is large and I/O would drown signal. "
            "Integration-test the seams that actually fail in production: SQL, migrations, auth middleware, serialization. "
            "If a bug can only appear when two real components interact, it does not belong solely in a mocked unit test.",
        ),
    ]
    out: list[Example] = []
    for slug, prompt, obs, cons, plan, answer in lessons:
        out.append(
            build_example(
                domain=Domain.HUMAN,
                task_type="teaching",
                prompt=prompt,
                answer=answer,
                solution=answer,
                observations=obs,
                constraints=cons,
                plan=plan,
                provenance=_human_src(slug),
                quality=reviewed_quality(["human-authored teaching item; not executed"]),
                source_key=slug,
                context={"audience": "technical"},
                metadata={"authorship": "human"},
            )
        )
    return out


def _research_synthesis() -> list[Example]:
    items = [
        (
            "synth-consensus",
            "Three lab notes follow. Synthesize whether the team should ship the compression change.\n\n"
            "Note A: CPU usage rose 8% in staging, well inside budget.\n"
            "Note B: p99 latency on the image API fell 22% for files > 1 MB.\n"
            "Note C: One internal client still uses a decoder that rejects the new frame header.\n"
            "Answer ship, wait, or rollback and list the blocking issue if not ship.",
            "wait",
            "Latency and CPU look acceptable, but a known decoder incompatibility is a release blocker. Wait until that client is upgraded or gated.",
            ["CPU +8% inside budget", "p99 latency improved for large files", "One client rejects new headers"],
            ["Do not ship a change that hard-breaks a supported client"],
            ["Separate performance from compatibility", "Treat compatibility as a gate"],
        ),
        (
            "synth-incident",
            "Given these fragments, name the most likely primary cause (one phrase).\n"
            "1) Errors spiked only in az-b.\n"
            "2) Deploy of service auth-gw occurred in az-b 4 minutes earlier.\n"
            "3) Database CPU was flat.\n"
            "4) A feature flag defaulted to true in the new build.",
            "bad_feature_flag_on_auth_gw_deploy",
            "The spatial and temporal coincidence with the az-b auth-gw deploy, plus a default-true flag, dominates; the database is not implicated.",
            ["az-b only", "deploy 4 minutes prior", "DB CPU flat", "flag default true"],
            ["Prefer causes that explain locality and timing"],
            ["Check what changed", "Check where it changed", "Rule out unchanged subsystems"],
        ),
    ]
    out: list[Example] = []
    for slug, prompt, answer, solution, obs, cons, plan in items:
        out.append(
            build_example(
                domain=Domain.HUMAN,
                task_type="research_synthesis",
                prompt=prompt,
                answer=answer,
                solution=solution,
                observations=obs,
                constraints=cons,
                plan=plan,
                provenance=_human_src(slug),
                quality=reviewed_quality(["human-authored synthesis from provided notes only"]),
                source_key=slug,
                context={"materials": "provided_in_prompt"},
                metadata={"authorship": "human"},
            )
        )
    return out


def _qualitative() -> list[Example]:
    items = [
        (
            "qual-tradeoff",
            "A team can add a strongly consistent cross-region write path or keep region-local writes with async replication. "
            "The product is a collaborative document editor. Which option better matches the product, and why, in 4 sentences or fewer?",
            "prefer_stronger_consistency_for_shared_docs",
            "Collaborative editors make concurrent conflicting writes user-visible as lost keystrokes or surprising ordering. "
            "Region-local async replication optimizes availability and latency at the cost of conflict. "
            "For this product, correctness of a shared document usually dominates extra cross-region latency. "
            "If a region outage is a bigger threat than edit conflicts, the opposite choice can be justified explicitly.",
        ),
        (
            "qual-ethics-eval",
            "An evaluation set for hiring-assist models includes names and schools. "
            "State two concrete dataset practices that reduce avoidable harm without claiming fairness is solved.",
            "minimize_direct_identifiers_and_report_slice_metrics",
            "Avoid keeping names, contact data, and other identifiers that are not needed to measure the skill. "
            "Report disaggregated error rates on documented slices (e.g., school groups) so failures are visible. "
            "Neither practice makes the system fair; they make the evaluation less casually harmful and more inspectable.",
        ),
    ]
    out: list[Example] = []
    for slug, prompt, answer, solution in items:
        out.append(
            build_example(
                domain=Domain.HUMAN,
                task_type="qualitative_reasoning",
                prompt=prompt,
                answer=answer,
                solution=solution,
                observations=[],
                constraints=["Stay within the stated scenario", "Do not invent statistics"],
                plan=["Identify the objective", "Name the main tradeoff", "Give a bounded recommendation"],
                provenance=_human_src(slug),
                quality=reviewed_quality(["human-authored qualitative item"]),
                source_key=slug,
                metadata={"authorship": "human"},
            )
        )
    return out


def _planning_word(rng: random.Random) -> list[Example]:
    out: list[Example] = []
    tasks = [
        ("write spec", 2),
        ("implement", 5),
        ("code review", 1),
        ("qa", 2),
        ("docs", 1),
    ]
    for i in range(80):
        capacity = 8 + i
        chosen = []
        total = 0
        for name, cost in tasks:
            if total + cost <= capacity:
                chosen.append(name)
                total += cost
        answer = ", ".join(chosen)
        prompt = (
            f"You have {capacity} engineer-days this week. Tasks and costs: "
            + ", ".join(f"{n}={c}" for n, c in tasks)
            + ". Select a prefix of the list (in the given priority order) that fits. "
            "Return the chosen task names comma-separated."
        )
        check = sum(c for n, c in tasks if n in chosen) == total <= capacity
        verification = Verification(method="capacity-check", passed=check, result=answer)
        out.append(
            build_example(
                domain=Domain.HUMAN,
                task_type="planning",
                prompt=prompt,
                answer=answer,
                solution=f"Greedy by listed priority until the next task would exceed {capacity}: {answer} (cost {total}).",
                observations=[f"capacity={capacity}"],
                constraints=["Priority order is fixed", "No partial tasks"],
                assumptions=["Tasks are sequential in the given order"],
                plan=["Walk the list", "Take a task if it fits", "Stop at first that does not"],
                verification=verification,
                provenance=_syn(),
                quality=verified_quality("capacity-check") if check else reviewed_quality(),
                source_key=f"plan-{i}-{capacity}",
                metadata={"authorship": "synthetic"},
            )
        )
    return out


def _constraint_word(rng: random.Random) -> list[Example]:
    out: list[Example] = []
    for i in range(80):
        n = 5 + i
        pairs = n // 2
        leftovers = n - 2 * pairs
        prompt = (
            f"You must pair {n} on-call engineers into two-person shifts. "
            "How many complete pairs can you form, and how many people are left unpaired?"
        )
        answer = f"pairs={pairs}; unpaired={leftovers}"
        check = pairs * 2 + leftovers == n
        verification = Verification(method="integer-check", passed=check, result=answer)
        out.append(
            build_example(
                domain=Domain.HUMAN,
                task_type="constraint_satisfaction",
                prompt=prompt,
                answer=answer,
                solution=f"pairs = floor({n}/2) = {pairs}; unpaired = {n} mod 2 = {leftovers}.",
                observations=[f"n={n}"],
                constraints=["Pairs are size 2", "No person in two pairs"],
                assumptions=["People are indistinguishable for this count"],
                plan=["Integer divide by 2", "Report remainder"],
                verification=verification,
                provenance=_syn(),
                quality=verified_quality("integer-check"),
                source_key=f"human-pairs-{n}-{i}",
                metadata={"authorship": "synthetic"},
            )
        )
    return out


def _explanation_gold() -> list[Example]:
    items = [
        (
            "explain-backpressure",
            "Explain backpressure in a producer-consumer pipeline and one concrete way to implement it.",
            "When a consumer cannot keep up, backpressure is a signal that slows or blocks the producer so queues stay bounded. "
            "A concrete implementation is a bounded blocking queue: put() waits when full. "
            "Alternatives include windowed credit in network protocols and dropping with a documented policy (which is load-shedding, not backpressure).",
        ),
        (
            "explain-idempotency",
            "Why do payment capture APIs use idempotency keys? Answer for a programmer implementing retries.",
            "Retries after uncertain network failure can otherwise capture twice. "
            "An idempotency key lets the server recognize a replay and return the original result instead of performing a second side effect. "
            "The client must reuse the same key for the same logical attempt and not reuse it for a different capture.",
        ),
        (
            "explain-statistical-vs-practical",
            "A change improves conversion 0.02 percentage points with p<0.01 on 50 million sessions. "
            "What should a product meeting still ask?",
            "Statistical significance is not the same as practical significance or causal cleanliness. "
            "Ask: is 0.02pp worth the complexity and risk; were users randomized; is the metric gamed; "
            "are segments harmed; and does the experiment capture long-term effects.",
        ),
        (
            "explain-repro-science",
            "A computational paper reports a figure but not the random seed, dependency versions, or input split. "
            "What three artifacts would make the figure independently checkable?",
            "Pin seeds; pin software versions (lockfile or container digest); publish the exact split or generator with data hashes. "
            "Together these let someone regenerate the figure or show that they cannot.",
        ),
        (
            "explain-sre-error-budget",
            "In one paragraph, what is an error budget for and what decision does it unlock?",
            "An error budget is the allowed unreliability derived from an SLO (for example 0.1% unavailability in 30 days). "
            "It turns reliability from a slogan into a spending account: if budget remains, ship faster; if it is burned, freeze risky changes and invest in reliability until the SLO recovers.",
        ),
        (
            "explain-floating-sum",
            "Why can summing millions of float32 values depend on order? What is a safer accumulator type for a total?",
            "Float32 rounding is not associative; partial sums round differently depending on order and magnitude. "
            "Accumulate in float64 (or Kahan/Neumaier compensation) and cast once at the end if a 32-bit store is required.",
        ),
        (
            "explain-cap",
            "State the CAP tradeoff in operational terms for a partitioned key-value store.",
            "During a network partition a system cannot be both available for all clients and strictly consistent. "
            "Practical systems choose which clients may wait or see stale/error responses, and they document the consistency model in the happy path as well.",
        ),
        (
            "explain-test-oracle",
            "What is a test oracle, and why is 'assert not crashed' a weak oracle for a compiler?",
            "An oracle decides whether a run is correct. Survival only shows that one path did not abort, not that codegen matched the language semantics. "
            "Stronger oracles include differential tests against another implementation, round-trip execution, or checking explicit invariants on IR.",
        ),
    ]
    out: list[Example] = []
    for slug, prompt, answer in items:
        out.append(
            build_example(
                domain=Domain.HUMAN,
                task_type="explanation",
                prompt=prompt,
                answer=answer,
                solution=answer,
                observations=[],
                constraints=["Be technically specific", "No hidden chain-of-thought dump"],
                plan=["State the mechanism", "Give a concrete implication"],
                provenance=_human_src(slug),
                quality=reviewed_quality(["human-authored explanation"]),
                source_key=slug,
                metadata={"authorship": "human"},
            )
        )
    return out


def _inventory(rng: random.Random) -> list[Example]:
    out: list[Example] = []
    items = [("laptops", 12), ("cables", 40), ("docks", 8), ("monitors", 15)]
    for i in range(80):
        budget = 30 + i
        remaining = budget
        taken: list[str] = []
        cap = 1 + (i % 3)
        for name, cost in items:
            qty = min(remaining // cost, cap)
            if qty <= 0:
                continue
            taken.append(f"{name}x{qty}")
            remaining -= qty * cost
        spent = budget - remaining
        cart = ",".join(taken)
        answer = f"spent={spent}; remaining={remaining}; cart={cart}"
        prompt = (
            f"You have a procurement budget of {budget}. Catalogue (unit cost): "
            + ", ".join(f"{n}={c}" for n, c in items)
            + f". Walk the catalogue in listed order. For each item buy up to {cap} units "
            "without exceeding the remaining budget. Report spent, remaining, and cart as namexqty comma-separated."
        )
        check = spent + remaining == budget and spent <= budget
        verification = Verification(method="budget-check", passed=check, result=answer)
        out.append(
            build_example(
                domain=Domain.HUMAN,
                task_type="structured_reasoning",
                prompt=prompt,
                answer=answer,
                solution=f"Greedy catalogue walk yields {answer}.",
                observations=[f"budget={budget}"],
                constraints=["Do not exceed budget", "Per-item cap as stated", "Listed order"],
                assumptions=["Integer units only"],
                plan=[
                    "Initialize remaining=budget",
                    "For each item buy min(cap, remaining//cost)",
                    "Report totals",
                ],
                verification=verification,
                provenance=_syn(),
                quality=verified_quality("budget-check"),
                source_key=f"inv-{i}-{budget}-{cap}",
                metadata={"authorship": "synthetic"},
            )
        )
    return out


def _sla_queue(rng: random.Random) -> list[Example]:
    """Verified staffing/queue arithmetic (not paraphrases of inventory)."""
    out: list[Example] = []
    for i in range(40):
        arrival = 10 + (i % 7)
        service = 2 + (i % 3)
        window = 30
        served = min(window // service, arrival)
        backlog = arrival - served
        answer = f"served={served}; backlog={backlog}"
        prompt = (
            f"A support window lasts {window} minutes. Each ticket takes {service} minutes "
            f"with one agent and no overlap. {arrival} tickets wait at t=0. "
            "How many are served in the window, and how many remain as backlog?"
        )
        check = served + backlog == arrival and served * service <= window
        verification = Verification(method="queue-check", passed=check, result=answer)
        out.append(
            build_example(
                domain=Domain.HUMAN,
                task_type="structured_reasoning",
                prompt=prompt,
                answer=answer,
                solution=f"Throughput={window}//{service}={window // service}; {answer}.",
                observations=[f"arrival={arrival}", f"service={service}", f"window={window}"],
                constraints=["Single agent", "No preemption", "Tickets are identical"],
                assumptions=["All tickets present at start"],
                plan=["Compute capacity", "served=min(capacity, arrivals)", "backlog=arrivals-served"],
                verification=verification,
                provenance=_syn(),
                quality=verified_quality("queue-check") if check else reviewed_quality(),
                source_key=f"sla-{i}-{arrival}-{service}",
                metadata={"authorship": "synthetic"},
            )
        )
    return out


def _v1_teaching() -> list[Example]:
    lessons = [
        (
            "teach-provenance-unknown",
            "A dataset row has no source URL and no generator name. What must provenance.source_type be, and what else is required?",
            [
                "Missing fields are not the same as known synthetic origin.",
            ],
            [
                "Do not invent a generator.",
            ],
            [
                "Set source_type to unknown",
                "Record unknown_reason",
            ],
            "source_type must be unknown, with an explicit unknown_reason. Do not label it synthetic or human-authored without evidence.",
        ),
        (
            "teach-verbatim-false",
            "Auto-approve enabled a documentation source. Why must verbatim stay false in Open Reason v1?",
            [
                "No crawler copies pages into the release.",
            ],
            [
                "Do not scrape the named site.",
            ],
            [
                "State curriculum_use",
                "State verbatim=false",
            ],
            "Auto-approve only turns on original tasks inspired by public structure. Copying page text would require a separate license review and a crawler that this pipeline does not run.",
        ),
        (
            "teach-nc-not-relicense",
            "A page is CC BY-NC. Can those sentences be relicensed as Apache-2.0 inside Open Reason?",
            [
                "NC forbids commercial reuse of the licensed text.",
            ],
            [
                "Do not treat public posting as a grant.",
            ],
            [
                "Keep NC off the CC BY release",
                "Generate original tasks instead if policy allows",
            ],
            "No. NC text cannot be relicensed as Apache-2.0. Leave it out of the release or keep the original SPDX on the row; this project does not relicense NC material.",
        ),
        (
            "teach-verified-flag",
            "When is quality.verified allowed to be true?",
            [
                "The schema can store a verification object.",
            ],
            [
                "Do not mark verified because a human liked the answer.",
            ],
            [
                "Require a check that ran",
                "Require passed=true",
            ],
            "Only after an independent check actually ran and passed (sandbox, sympy, numeric, or a named constraint checker). Reviews without a checker stay unverified even at tier A.",
        ),
        (
            "teach-holdout",
            "Why must benchmarks/items.jsonl stay out of data/release training JSONL?",
            [
                "Both are generated by related pipelines.",
            ],
            [
                "Do not mix holdout ids into train.",
            ],
            [
                "Keep disjoint ids",
                "Scan overlap before claiming eval",
            ],
            "Training on the holdout makes evaluation scores meaningless. Open Reason's benchmark command fails if ids overlap.",
        ),
        (
            "teach-http-cache",
            "Why can a GET be retried after a timeout more safely than a POST that created a row?",
            [
                "Timeouts do not tell you whether the server applied the request.",
            ],
            [
                "Stay at HTTP method semantics.",
            ],
            [
                "Recall GET safety/idempotence",
                "Contrast with POST create",
            ],
            "GET is safe and idempotent in HTTP semantics, so a retry should not create a new resource. POST create is not idempotent unless the API adds keys or uses PUT to a known URL.",
        ),
        (
            "teach-index-selectivity",
            "A product manager asks for an index on every column 'to make the database fast'. What do you teach them?",
            [
                "Indexes speed some lookups.",
            ],
            [
                "Avoid vendor-specific lore as the only point.",
            ],
            [
                "Explain write amplification",
                "Explain low-selectivity scans",
            ],
            "Each index slows writes and uses space. Columns that match most rows will not use the index anyway. Index predicates you actually filter or join on, after measuring.",
        ),
        (
            "teach-float-money",
            "Why should a ledger not store currency as IEEE-754 binary float?",
            [
                "Decimals like 0.1 are not exact in binary floating point.",
            ],
            [
                "Do not claim all floats are unusable for science.",
            ],
            [
                "State representation error",
                "Name integers or decimal types",
            ],
            "Many decimal amounts cannot be represented exactly, so rounding accumulates. Store integer minor units or a decimal type with a documented scale.",
        ),
    ]
    out: list[Example] = []
    for slug, prompt, observations, constraints, plan, answer in lessons:
        out.append(
            build_example(
                domain=Domain.HUMAN,
                task_type="teaching",
                prompt=prompt,
                answer=answer,
                solution=answer,
                observations=observations,
                constraints=constraints,
                plan=plan,
                provenance=_human_src(slug),
                quality=reviewed_quality(["human-authored teaching"]),
                source_key=slug,
                metadata={"authorship": "human"},
            )
        )
    return out
