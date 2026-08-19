"""v1.0.1 reasoning: distinct checkable scenarios (not near-paraphrases)."""

from __future__ import annotations

import random
from datetime import date, timedelta

from open_reason.generation.reasoning import _emit
from open_reason.models import Example


def extra_reasoning_v101(rng: random.Random) -> list[Example]:
    _ = rng
    out: list[Example] = []
    out.extend(_causal_unique())
    out.extend(_planning_unique())
    out.extend(_matching())
    out.extend(_coloring())
    out.extend(_calendar())
    out.extend(_bills())
    out.extend(_syllogism())
    out.extend(_protocol())
    out.extend(_shortest_named())
    return out


def _causal_unique() -> list[Example]:
    specs = [
        {
            "prompt": (
                "A bakery's burnt-loaf rate rose the week they changed flour vendors "
                "and the week the oven thermostat failed. After replacing only the "
                "thermostat, the rate returned to baseline while still using the new "
                "flour. What is the better causal claim: flour, thermostat, or both required?"
            ),
            "answer": "thermostat",
            "solution": (
                "The flour change remained after the rate recovered, so it was not "
                "necessary for the spike. The thermostat repair coincided with recovery."
            ),
            "obs": ["Two changes co-occurred", "Only thermostat was reverted"],
        },
        {
            "prompt": (
                "App latency rose after a cache flush and after a schema migration. "
                "Rolling back the migration (cache still cold) restored latency. "
                "Which change is sufficient to explain the regression?"
            ),
            "answer": "schema migration",
            "solution": (
                "The cold cache remained after rollback, yet latency recovered, so the "
                "flush was not required for the regression."
            ),
            "obs": ["Two candidate causes", "Rollback isolated one"],
        },
        {
            "prompt": (
                "Plant height increased in a plot that received fertilizer and extra "
                "water. A neighboring plot with extra water only did not grow more. "
                "Relative to water-only, what is the supported cause of extra height?"
            ),
            "answer": "fertilizer",
            "solution": (
                "Water was present in both plots. The difference that tracks extra "
                "height is fertilizer."
            ),
            "obs": ["Water-only control", "Fertilizer+water treatment"],
        },
        {
            "prompt": (
                "Bug reports spiked after a Friday deploy and a Monday holiday. "
                "The deploy was reverted Tuesday; reports dropped though the holiday "
                "had already passed. What better explains the spike?"
            ),
            "answer": "Friday deploy",
            "solution": (
                "The holiday was over before the drop. Revert tracked the drop, so the "
                "deploy is the better explanation."
            ),
            "obs": ["Holiday ended before revert", "Revert then drop"],
        },
        {
            "prompt": (
                "A river's turbidity rose after rain and after a construction start. "
                "A later rain of similar size, while construction was paused, did not "
                "raise turbidity. What is the better explanation of the first spike?"
            ),
            "answer": "construction",
            "solution": (
                "Rain alone later did not reproduce the spike, so rain is not sufficient. "
                "Construction remaining on during the first rain is the distinguishing factor."
            ),
            "obs": ["Similar rain later", "Construction paused later"],
        },
        {
            "prompt": (
                "Exam scores fell after switching textbooks and after shortening the "
                "term. A later cohort used the new book with the original term length "
                "and scored like the historical baseline. What better explains the drop?"
            ),
            "answer": "shortened term",
            "solution": (
                "The new textbook with the old calendar matched baseline, so the book "
                "was not sufficient to cause the drop."
            ),
            "obs": ["Textbook held constant later", "Term length restored"],
        },
    ]
    out: list[Example] = []
    for i, spec in enumerate(specs):
        example = _emit(
            task_type="causal_reasoning",
            prompt=spec["prompt"],
            answer=spec["answer"],
            solution=spec["solution"],
            observations=spec["obs"],
            constraints=["Single best cause among the named options", "No unstated confounders"],
            assumptions=["The later isolation test is valid"],
            plan=["List co-occurring changes", "See what remained when the effect vanished"],
            key=f"causal-v101-{i}",
            check=True,
        )
        if example:
            out.append(example)
    return out


def _planning_unique() -> list[Example]:
    specs = [
        (
            "You must file taxes (2h), pick up a passport (1h, office open only 10:00-12:00), "
            "and grocery shop (1h, anytime). You start at 09:00. Give the start times "
            "HH:MM for passport, taxes, groceries in that order, with no overlap, "
            "finishing as early as possible.",
            "10:00,09:00,11:00",
            "Passport is constrained to 10-12 so start it at 10:00. Taxes fill 09:00-11:00 "
            "would overlap; so taxes 09:00-11:00 actually overlaps passport. Taxes must be "
            "09:00-11:00? 2h from 09:00 is 11:00, overlapping 10:00 passport. So taxes cannot "
            "start at 09:00. Passport 10:00-11:00, taxes 11:00-13:00, groceries 13:00-14:00 "
            "OR taxes 09:00-11:00 is invalid. Correct: taxes cannot overlap 10-11. "
            "Wait: taxes 09:00-11:00 overlaps 10:00-11:00. So: groceries 09:00-10:00, "
            "passport 10:00-11:00, taxes 11:00-13:00. Start times passport,taxes,groceries: "
            "10:00,11:00,09:00.",
        ),
    ]
    # Fix the first planning item carefully.
    items = [
        {
            "prompt": (
                "Tasks: taxes 2h unconstrained; passport 1h only 10:00-12:00; groceries 1h "
                "anytime. Work starts 09:00, no overlap. List start times as HH:MM for "
                "passport, taxes, groceries in that order, finishing as early as possible."
            ),
            "answer": "10:00,11:00,09:00",
            "solution": (
                "Groceries 09:00-10:00, passport 10:00-11:00 (inside the window), "
                "taxes 11:00-13:00. Finish 13:00."
            ),
            "obs": ["Passport window 10-12", "Earliest finish"],
            "key": "plan-passport",
        },
        {
            "prompt": (
                "A chemist needs 30 min of fume-hood time, 45 min of analysis that requires "
                "the hood product, and 20 min of glassware wash that can run anytime. "
                "The hood is free only 13:00-14:00. Start at 12:30. Give start times HH:MM "
                "for hood, analysis, wash in that order with no overlap."
            ),
            "answer": "13:00,13:30,12:30",
            "solution": (
                "Wash 12:30-12:50 (or any pre-hood slot). Hood must start 13:00. Analysis "
                "after hood: 13:30. Wash cannot be after if we want a feasible early plan; "
                "12:30 wash works."
            ),
            "obs": ["Hood only 13:00-14:00", "Analysis depends on hood"],
            "key": "plan-hood",
        },
        {
            "prompt": (
                "Three talks of 20 min must be scheduled in rooms A then B then A again "
                "(A cannot host two consecutive talks). Slots are 09:00, 09:30, 10:00. "
                "Assign rooms as a comma-separated list in slot order."
            ),
            "answer": "A,B,A",
            "solution": "A, A, A would consecutive-A. A,B,A alternates and uses A twice.",
            "obs": ["A cannot be consecutive", "Three slots"],
            "key": "plan-rooms",
        },
        {
            "prompt": (
                "You have a 15-min bus at :00 and :30 past each hour and a 10-min walk to "
                "the stop. You leave home at 08:07. What is the earliest bus you can catch "
                "as HH:MM?"
            ),
            "answer": "08:30",
            "solution": "Arrive at stop 08:17, missing 08:00. Next is 08:30.",
            "obs": ["Walk 10 min", "Buses :00 and :30"],
            "key": "plan-bus",
        },
        {
            "prompt": (
                "Bake 25 min, cool 10 min, glaze 5 min, in that order, no overlap. "
                "Oven is free from 16:40. When is glazing finished as HH:MM?"
            ),
            "answer": "17:20",
            "solution": "Bake 16:40-17:05, cool 17:05-17:15, glaze 17:15-17:20.",
            "obs": ["Serial tasks", "Oven from 16:40"],
            "key": "plan-bake",
        },
    ]
    out: list[Example] = []
    for spec in items:
        example = _emit(
            task_type="planning",
            prompt=spec["prompt"],
            answer=spec["answer"],
            solution=spec["solution"],
            observations=spec["obs"],
            constraints=["No overlapping exclusive resources", "Respect windows"],
            assumptions=["Instant travel unless stated"],
            plan=["Identify constrained tasks", "Place unconstrained fillers", "Check finish"],
            key=spec["key"],
            check=True,
        )
        if example:
            out.append(example)
    _ = specs
    return out


def _matching() -> list[Example]:
    items = [
        {
            "prompt": (
                "People {Ann, Bea, Cal} and jobs {desk, lab, field}. Ann refuses field, "
                "Bea refuses desk, Cal refuses lab. Each person one job. List person:job "
                "pairs alphabetically by person."
            ),
            "answer": "Ann:desk,Bea:lab,Cal:field",
            "solution": (
                "Ann cannot field so desk or lab. If Ann lab, Bea cannot desk so Bea field, "
                "Cal cannot lab (ok) would get desk: Cal:desk, Bea:field, Ann:lab. Also "
                "feasible: Ann desk, Bea lab, Cal field. The prompt asks for the assignment "
                "where Ann takes desk (the unique assignment if we also prefer Cal to field "
                "because Cal refuses lab only). Wait, two matchings exist. "
                "Ann:lab, Bea:field, Cal:desk is also valid. Need uniqueness."
            ),
        }
    ]
    # Make unique with extra constraint
    unique = [
        {
            "prompt": (
                "Assign {Ann, Bea, Cal} to {desk, lab, field}. Ann refuses field, Bea "
                "refuses desk, Cal refuses lab, and the lab must go to Ann. List "
                "person:job alphabetically by person."
            ),
            "answer": "Ann:lab,Bea:field,Cal:desk",
            "solution": "Lab is Ann. Bea cannot desk so Bea field. Cal gets desk.",
            "key": "match-jobs",
        },
        {
            "prompt": (
                "Four students want two lab benches. Compatible pairs are (Ada, Ben), "
                "(Ada, Cyd), (Ben, Di). Maximize pairs without sharing a person. How many "
                "pairs can you seat?"
            ),
            "answer": "1",
            "solution": (
                "Any two of those pairs share Ada or Ben. Maximum matching size is 1."
            ),
            "key": "match-benches",
        },
        {
            "prompt": (
                "Tutors {T1,T2} and students {S1,S2,S3}. Each tutor takes at most one "
                "student. Allowed: T1-S1, T1-S2, T2-S2, T2-S3. Maximum number of matched "
                "students?"
            ),
            "answer": "2",
            "solution": "Two tutors, so at most 2. T1-S1 and T2-S3 is a maximum matching.",
            "key": "match-tutors",
        },
    ]
    out: list[Example] = []
    for spec in unique:
        example = _emit(
            task_type="constraint_satisfaction",
            prompt=spec["prompt"],
            answer=spec["answer"],
            solution=spec["solution"],
            observations=["Finite matching instance"],
            constraints=["Respect refusals and capacities"],
            assumptions=["No unlisted edges"],
            plan=["Write the bipartite graph", "Find a maximum matching"],
            key=spec["key"],
            check=True,
        )
        if example:
            out.append(example)
    _ = items
    return out


def _coloring() -> list[Example]:
    items = [
        {
            "prompt": (
                "A triangle graph (3 vertices all adjacent) is to be vertex-colored. "
                "What is the chromatic number?"
            ),
            "answer": "3",
            "solution": "K3 needs three colors.",
            "key": "chrom-k3",
        },
        {
            "prompt": (
                "A cycle of 4 vertices (square) is to be vertex-colored. Chromatic number?"
            ),
            "answer": "2",
            "solution": "Even cycles are bipartite, so 2-colorable.",
            "key": "chrom-c4",
        },
        {
            "prompt": (
                "How many proper 2-colorings does a single edge (2 vertices, 1 edge) have "
                "if colors are {red, blue} and the two vertices must differ? Count labeled "
                "colorings, not up to swapping colors."
            ),
            "answer": "2",
            "solution": "Red-blue or blue-red. Same-color is forbidden.",
            "key": "chrom-edge",
        },
        {
            "prompt": (
                "A path of 3 vertices needs vertex colors so adjacent vertices differ. "
                "Using 2 colors, how many labeled colorings?"
            ),
            "answer": "2",
            "solution": (
                "Ends must match each other (both differ from the middle). 2 choices for "
                "the middle, then ends are forced. Wait: middle has 2 choices, each end "
                "has 1 remaining color. 2 colorings. Yes."
            ),
            "key": "chrom-p3",
        },
    ]
    out: list[Example] = []
    for spec in items:
        example = _emit(
            task_type="constraint_satisfaction",
            prompt=spec["prompt"],
            answer=spec["answer"],
            solution=spec["solution"],
            observations=["Finite simple graph"],
            constraints=["Proper vertex coloring"],
            assumptions=["Named colors are distinct labels"],
            plan=["Use bipartiteness or clique number"],
            key=spec["key"],
            check=True,
        )
        if example:
            out.append(example)
    return out


def _calendar() -> list[Example]:
    items = [
        {
            "prompt": "2026-08-18 is a Tuesday. What weekday is 2026-08-25 (same calendar)?",
            "answer": "Tuesday",
            "solution": "Seven days later is the same weekday.",
            "key": "cal-plus7",
        },
        {
            "prompt": (
                "A project starts Monday 2026-08-17 and lasts 10 working days, skipping "
                "Saturday and Sunday, no holidays. What is the finish date YYYY-MM-DD?"
            ),
            "answer": "2026-08-28",
            "solution": (
                "Mon 17 through Fri 21 is 5 days; Mon 24 through Fri 28 is 5 more. Finish Friday 28."
            ),
            "key": "cal-work10",
        },
        {
            "prompt": (
                "From 2026-01-01 to 2026-03-01, how many calendar days elapse if we count "
                "the end date but not the start date (date difference)?"
            ),
            "answer": "59",
            "solution": "2026 is not a leap year: 31 days in Jan + 28 in Feb = 59 to March 1.",
            "key": "cal-janmar",
        },
        {
            "prompt": (
                "A 48-hour timer starts 2026-08-18 09:00. When does it end, local civil "
                "time with no DST change, as YYYY-MM-DD HH:MM?"
            ),
            "answer": "2026-08-20 09:00",
            "solution": "48 hours is exactly two days later at the same clock time.",
            "key": "cal-48h",
        },
    ]
    # verify jan-mar
    assert (date(2026, 3, 1) - date(2026, 1, 1)).days == 59
    out: list[Example] = []
    for spec in items:
        example = _emit(
            task_type="temporal_reasoning",
            prompt=spec["prompt"],
            answer=spec["answer"],
            solution=spec["solution"],
            observations=["Gregorian calendar", "No DST unless stated"],
            constraints=["Use the stated counting convention"],
            assumptions=["2026 is not a leap year"],
            plan=["Apply weekday or month-length arithmetic"],
            key=spec["key"],
            check=True,
        )
        if example:
            out.append(example)
    _ = timedelta
    return out


def _bills() -> list[Example]:
    items = [
        {
            "prompt": (
                "A bill is $90. Three people split equally, then one person covers a $12 "
                "tip on top of their share. How many dollars does that person pay in total?"
            ),
            "answer": "42",
            "solution": "Share 30, plus 12 tip = 42.",
            "key": "bill-tip",
        },
        {
            "prompt": (
                "Items cost 15, 25, and 10. A 10% coupon applies only to the most expensive "
                "item. What is the total after the coupon, in dollars?"
            ),
            "answer": "47.5",
            "solution": "25*0.9=22.5; 15+22.5+10=47.5.",
            "key": "bill-coupon",
        },
        {
            "prompt": (
                "Four people share a $80 bill. One paid $50 already as a deposit. How much "
                "does each of the other three still owe if the deposit counts toward the "
                "group total and remaining is split equally among the three?"
            ),
            "answer": "10",
            "solution": "Remaining 30, three people, 10 each.",
            "key": "bill-deposit",
        },
        {
            "prompt": (
                "A taxi is $18 plus $2 per extra rider. Three extra riders and a 15% tip "
                "on the pre-tip fare. What is the total, dollars (one decimal if needed)?"
            ),
            "answer": "27.6",
            "solution": "Fare 18+6=24; tip 3.6; total 27.6.",
            "key": "bill-taxi",
        },
    ]
    out: list[Example] = []
    for spec in items:
        example = _emit(
            task_type="quantitative_reasoning",
            prompt=spec["prompt"],
            answer=spec["answer"],
            solution=spec["solution"],
            observations=["Stated prices only"],
            constraints=["No hidden tax unless stated"],
            assumptions=["Exact decimal arithmetic"],
            plan=["Compute base", "Apply coupon/tip", "Add"],
            key=spec["key"],
            check=True,
        )
        if example:
            out.append(example)
    return out


def _syllogism() -> list[Example]:
    items = [
        {
            "prompt": (
                "All widgets are gadgets. Some gadgets are branded. Does it follow that "
                "some widgets are branded? Answer yes, no, or undetermined."
            ),
            "answer": "undetermined",
            "solution": (
                "The branded gadgets might all lie outside the widget subset."
            ),
            "key": "syl-undetermined",
        },
        {
            "prompt": (
                "No squares are circles. All tiles in set T are squares. Are any tiles in "
                "T circles? Answer yes, no, or undetermined."
            ),
            "answer": "no",
            "solution": "T ⊆ squares, squares ∩ circles = empty, so T ∩ circles = empty.",
            "key": "syl-no",
        },
        {
            "prompt": (
                "Every intern is a contractor. Maya is an intern. Is Maya a contractor? "
                "Answer yes, no, or undetermined."
            ),
            "answer": "yes",
            "solution": "Universal instantiation: intern ⇒ contractor.",
            "key": "syl-yes",
        },
        {
            "prompt": (
                "If the server is down then alerts fire. Alerts fired. Is the server down? "
                "Answer yes, no, or undetermined."
            ),
            "answer": "undetermined",
            "solution": "Affirming the consequent. Alerts can fire for other reasons.",
            "key": "syl-converse",
        },
    ]
    out: list[Example] = []
    for spec in items:
        example = _emit(
            task_type="argument_analysis",
            prompt=spec["prompt"],
            answer=spec["answer"],
            solution=spec["solution"],
            observations=["Classical categorical/propositional reading"],
            constraints=["Do not import extra world knowledge"],
            assumptions=["Premises are given as true"],
            plan=["Translate to set inclusion or implication", "Check validity"],
            key=spec["key"],
            check=True,
        )
        if example:
            out.append(example)
    return out


def _protocol() -> list[Example]:
    items = [
        {
            "prompt": (
                "A handshake is: SYN, SYN-ACK, ACK. Packet 2 is lost and the client "
                "retries SYN. What is the next packet the server should send if it had "
                "not seen the first SYN complete?"
            ),
            "answer": "SYN-ACK",
            "solution": "A new SYN starts the handshake; server replies SYN-ACK.",
            "key": "proto-syn",
        },
        {
            "prompt": (
                "Two-phase commit: coordinator sent PREPARE and got YES from both "
                "workers, then crashed before COMMIT. Workers are waiting. After restart, "
                "what must the coordinator send to remain consistent if it had logged the "
                "decision to commit?"
            ),
            "answer": "COMMIT",
            "solution": "If the commit decision was logged, replay COMMIT, not ABORT.",
            "key": "proto-2pc",
        },
        {
            "prompt": (
                "A mutex is locked by thread A. Thread B waits. A unlocks. Who may run "
                "the critical section next: only B, only A, or either depending on the "
                "scheduler?"
            ),
            "answer": "either depending on the scheduler",
            "solution": "Unlock does not donate the lock to B unless the API says so.",
            "key": "proto-mutex",
        },
        {
            "prompt": (
                "HTTP GET is retried after a timeout with no response. The original GET "
                "was side-effect free. Is the retry safe with respect to duplicate "
                "effects? Answer yes or no."
            ),
            "answer": "yes",
            "solution": "GET is specified as safe/idempotent; duplicate GET should not create extra effects.",
            "key": "proto-get",
        },
    ]
    out: list[Example] = []
    for spec in items:
        example = _emit(
            task_type="troubleshooting",
            prompt=spec["prompt"],
            answer=spec["answer"],
            solution=spec["solution"],
            observations=["Protocol rules as stated"],
            constraints=["Defensive systems behaviour, not exploits"],
            assumptions=["Standard textbook protocol"],
            plan=["Name the protocol step", "Apply the recovery rule"],
            key=spec["key"],
            check=True,
        )
        if example:
            out.append(example)
    return out


def _shortest_named() -> list[Example]:
    items = [
        {
            "prompt": (
                "Cities: Oslo-Bergen 5, Oslo-Trondheim 7, Bergen-Trondheim 4, "
                "Bergen-Stavanger 2. Shortest Oslo to Stavanger length?"
            ),
            "answer": "7",
            "solution": "Oslo-Bergen-Stavanger = 5+2 = 7. Via Trondheim is longer.",
            "key": "path-oslo",
        },
        {
            "prompt": (
                "Grid: A connected to B and D; B to C; D to C. All edges cost 1. "
                "How many distinct shortest A-C paths (as vertex sequences)?"
            ),
            "answer": "2",
            "solution": "A-B-C and A-D-C, both length 2.",
            "key": "path-grid",
        },
        {
            "prompt": (
                "Directed edges A→B 3, A→C 9, B→C 4, B→D 1, C→D 1. Shortest A to D?"
            ),
            "answer": "4",
            "solution": "A-B-D = 3+1 = 4. A-B-C-D = 8. A-C-D = 10.",
            "key": "path-dir",
        },
        {
            "prompt": (
                "An undirected star with center H and leaves A,B,C. Edge weights 1. "
                "Distance A to B?"
            ),
            "answer": "2",
            "solution": "Must go A-H-B.",
            "key": "path-star",
        },
    ]
    out: list[Example] = []
    for spec in items:
        example = _emit(
            task_type="decision_analysis",
            prompt=spec["prompt"],
            answer=spec["answer"],
            solution=spec["solution"],
            observations=["Nonnegative edge weights"],
            constraints=["Simple paths", "Given graph only"],
            assumptions=["No negative edges"],
            plan=["Enumerate short routes", "Take the minimum"],
            key=spec["key"],
            check=True,
        )
        if example:
            out.append(example)
    return out
