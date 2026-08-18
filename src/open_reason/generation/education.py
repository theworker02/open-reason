"""Original curriculum tasks driven by the Open Reason knowledge graph.

These examples are written for Open Reason. They are inspired by typical
learning progressions, not copied from Khan Academy, MIT OCW, CS50, or MDN.
"""

from __future__ import annotations

import sympy as sp

from open_reason.constants import PIPELINE_VERSION
from open_reason.generation.base import build_example, reviewed_quality, verified_quality
from open_reason.knowledge import load_knowledge_graph
from open_reason.models import Domain, EducationLevel, Evidence, Example, Verification
from open_reason.provenance import synthetic_provenance
from open_reason.verification import verify_math_answer, verify_numeric


def _prov():
    return synthetic_provenance(
        generator="open_reason.generation.education",
        generator_version=PIPELINE_VERSION,
        transformation="curriculum_task_generation",
        trust_tier="tier7_synthetic",
    )


def _evidence(*methods: str) -> Evidence:
    return Evidence(
        educational_sources=["open-reason-curriculum"],
        verification_methods=list(methods),
    )


def generate_education(seed: int = 42) -> list[Example]:
    _ = seed  # Curriculum gold items are deterministic without sampling.
    graph = load_knowledge_graph()
    examples: list[Example] = []
    examples.extend(_programming())
    examples.extend(_mathematics())
    examples.extend(_science())
    examples.extend(_misconceptions(graph))
    from open_reason.generation.coverage_tasks import generate_coverage_tasks

    examples.extend(generate_coverage_tasks(seed=seed))
    return examples


def _emit(
    *,
    domain: Domain,
    task_type: str,
    prompt: str,
    answer: str,
    solution: str,
    concept_id: str,
    education_level: EducationLevel,
    observations: list[str],
    constraints: list[str],
    plan: list[str],
    quality,
    verification: Verification | None = None,
    context: dict | None = None,
    source_key: str,
) -> Example:
    return build_example(
        domain=domain,
        task_type=task_type,
        prompt=prompt,
        answer=answer,
        solution=solution,
        observations=observations,
        constraints=constraints,
        plan=plan,
        strategy=plan,
        verification=verification,
        provenance=_prov(),
        quality=quality,
        source_key=source_key,
        education_level=education_level,
        concept_id=concept_id,
        evidence=_evidence(*((verification.method,) if verification else ())),
        transformation=[
            "source",
            "concept_extraction",
            "knowledge_normalization",
            "task_generation",
            "difficulty_assignment",
            "verification" if quality.verified else "unverified",
        ],
        context=context or {"curriculum": True, "concept_id": concept_id},
        metadata={"concept_id": concept_id, "curriculum": True},
    )


def _programming() -> list[Example]:
    items: list[Example] = []
    items.append(
        _emit(
            domain=Domain.CODING,
            task_type="concept_explanation",
            prompt=(
                "A learner writes `a = [1, 2]; b = a; a = [3]`. Explain whether `b` "
                "changes, using name-binding rather than a box metaphor."
            ),
            answer="b still refers to [1, 2]. Rebinding a does not mutate or rebind b.",
            solution=(
                "`a = [1, 2]` binds the name `a` to a list object. `b = a` binds `b` to "
                "that same object. `a = [3]` creates a new list and rebinds only `a`. "
                "`b` still refers to `[1, 2]`."
            ),
            concept_id="python.variables",
            education_level=EducationLevel.HIGH_SCHOOL,
            observations=["Python names are bindings to objects."],
            constraints=["Do not treat assignment as always copying."],
            plan=["Identify the objects", "Track which names are rebound", "State b's referent"],
            quality=reviewed_quality(["original curriculum explanation"]),
            source_key="edu-py-variables-explain",
            context={"language": "python", "curriculum": True},
        )
    )
    items.append(
        _emit(
            domain=Domain.CODING,
            task_type="simple_exercise",
            prompt="What does `list(range(4))` evaluate to, and why is 4 missing?",
            answer="[0, 1, 2, 3]",
            solution=(
                "range(n) is a half-open interval [0, n). The endpoint n is excluded, "
                "matching valid indices of a length-n sequence."
            ),
            concept_id="python.loops",
            education_level=EducationLevel.HIGH_SCHOOL,
            observations=["range uses a half-open interval."],
            constraints=["Give the concrete list."],
            plan=["Recall range(n)", "List the integers", "Explain the missing endpoint"],
            quality=reviewed_quality(["original curriculum exercise"]),
            source_key="edu-py-loops-range",
            context={"language": "python", "curriculum": True},
        )
    )
    items.append(
        _emit(
            domain=Domain.CODING,
            task_type="debugging_exercise",
            prompt=(
                "A function is defined as "
                "`def collect(item, bucket=[]): bucket.append(item); return bucket`. "
                "A second call with a new item returns a list containing both items. "
                "Diagnose the defect and describe the standard repair."
            ),
            answer=(
                "The default list is created once at definition time. "
                "Use None and create a new list in the body."
            ),
            solution=(
                "Default argument objects are evaluated once. The same list is reused and mutated. "
                "Write `def collect(item, bucket=None):` and `if bucket is None: bucket = []`."
            ),
            concept_id="python.functions",
            education_level=EducationLevel.INTRODUCTORY_COLLEGE,
            observations=["The unexpected sharing happens across calls with no explicit bucket."],
            constraints=["Repair must keep the convenient default of an empty list per call."],
            plan=[
                "Identify the shared object",
                "Explain definition-time evaluation",
                "State the None pattern",
            ],
            quality=reviewed_quality(["original curriculum debugging"]),
            source_key="edu-py-functions-default",
            context={"language": "python", "curriculum": True},
        )
    )
    items.append(
        _emit(
            domain=Domain.CODING,
            task_type="applied_exercise",
            prompt=(
                "Why can a hash table that is O(1) average-case become linear in a single lookup, "
                "and name one mitigation used in production runtimes?"
            ),
            answer=(
                "Collisions concentrate keys in one bucket, so lookup walks a chain. "
                "Mitigations include randomized hash seeds and treeified buckets."
            ),
            solution=(
                "Average-case O(1) assumes a bounded load factor and well-spread hashes. "
                "If many keys collide, a bucket degrades to a list (or similar) "
                "and that lookup is O(n). "
                "CPython randomizes hash seeds and treeifies large colliding dict buckets."
            ),
            concept_id="cs.data_structures",
            education_level=EducationLevel.UNDERGRADUATE,
            observations=["Average-case bounds hide adversarial or highly skewed keys."],
            constraints=["Stay at data-structure behaviour, not a CVE writeup."],
            plan=[
                "State the average-case assumption",
                "Describe collision chains",
                "Name a mitigation",
            ],
            quality=reviewed_quality(["original curriculum application"]),
            source_key="edu-cs-hashtable",
            context={"language": "python", "curriculum": True},
        )
    )
    return items


def _mathematics() -> list[Example]:
    items: list[Example] = []
    arith = 2 + 3 * 4
    v_arith = verify_numeric(float(arith), 14.0)
    if v_arith.passed:
        items.append(
            _emit(
                domain=Domain.MATHEMATICS,
                task_type="simple_exercise",
                prompt="Evaluate 2 + 3 * 4 using standard arithmetic precedence.",
                answer="14",
                solution="Multiplication binds first: 3 * 4 = 12, then 2 + 12 = 14.",
                concept_id="math.arithmetic",
                education_level=EducationLevel.K5,
                observations=["Multiplication precedes addition."],
                constraints=["Do not insert extra parentheses that change meaning."],
                plan=["Apply precedence", "Compute the product", "Add"],
                quality=verified_quality("numeric"),
                verification=v_arith,
                source_key="edu-math-precedence",
            )
        )

    x = sp.symbols("x")
    eq = sp.Eq(x + 5, 2)
    solved = sp.solve(eq, x)[0]
    v_alg = verify_math_answer(str(solved), "-3")
    if v_alg.passed:
        items.append(
            _emit(
                domain=Domain.MATHEMATICS,
                task_type="simple_exercise",
                prompt="Solve for x: x + 5 = 2.",
                answer="-3",
                solution="Subtract 5 from both sides: x = 2 - 5 = -3.",
                concept_id="math.algebra",
                education_level=EducationLevel.HIGH_SCHOOL,
                observations=["The equation is linear."],
                constraints=["Give the exact integer solution."],
                plan=["Isolate x", "Simplify", "Check by substitution"],
                quality=verified_quality("sympy"),
                verification=v_alg,
                source_key="edu-math-linear",
            )
        )

    expr = sp.sin(x) / x
    limit = sp.limit(expr, x, 0)
    v_lim = verify_math_answer(str(limit), "1")
    if v_lim.passed:
        items.append(
            _emit(
                domain=Domain.MATHEMATICS,
                task_type="applied_exercise",
                prompt=(
                    "Compute lim_{x -> 0} (sin x)/x. Direct substitution is undefined; "
                    "still give the limit."
                ),
                answer="1",
                solution=(
                    "The two-sided limit is 1. A 0/0 form at a point does not by itself "
                    "imply the limit is missing."
                ),
                concept_id="math.calculus",
                education_level=EducationLevel.INTRODUCTORY_COLLEGE,
                observations=["f(0) is undefined.", "Nearby values approach 1."],
                constraints=["Use radians."],
                plan=[
                    "Recognize the indeterminate form",
                    "Recall or compute the standard limit",
                    "State 1",
                ],
                quality=verified_quality("sympy"),
                verification=v_lim,
                source_key="edu-math-limit-sinc",
            )
        )
    return items


def _science() -> list[Example]:
    force = 12.0  # N
    mass = 3.0  # kg
    accel = force / mass
    verification = verify_numeric(accel, 4.0)
    items = [
        _emit(
            domain=Domain.SCIENCE,
            task_type="concept_explanation",
            prompt="What makes a scientific hypothesis different from an untestable slogan?",
            answer="It must be testable and potentially falsifiable by observation or experiment.",
            solution=(
                "A hypothesis is a claim that could fail a well-designed test. Experiments can "
                "disconfirm it; they do not provide mathematical proof. "
                "Controls and replication matter."
            ),
            concept_id="science.method",
            education_level=EducationLevel.MIDDLE_SCHOOL,
            observations=["Slogans that cannot be tested are not scientific hypotheses."],
            constraints=["Do not claim experiments prove hypotheses in the mathematical sense."],
            plan=["Define testability", "Mention falsifiability", "Mention controls"],
            quality=reviewed_quality(["original curriculum science"]),
            source_key="edu-sci-method",
        )
    ]
    if verification.passed:
        items.append(
            _emit(
                domain=Domain.SCIENCE,
                task_type="numerical",
                prompt=(
                    "A net force of 12 N acts on a 3 kg mass. "
                    "What is the acceleration magnitude in m/s^2?"
                ),
                answer="4",
                solution="Newton's second law: a = F/m = 12/3 = 4 m/s^2.",
                concept_id="science.newton",
                education_level=EducationLevel.HIGH_SCHOOL,
                observations=["Net force and mass are given in SI units."],
                constraints=["Assume a particle model and constant mass."],
                plan=["Write a = F/m", "Substitute", "Report 4"],
                quality=verified_quality("numeric"),
                verification=verification,
                source_key="edu-sci-newton",
            )
        )
    return items


def _misconceptions(graph) -> list[Example]:
    items: list[Example] = []
    for mid, item in graph.misconceptions.items():
        concept = graph.concepts[item.concept_id]
        domain = {
            "programming": Domain.CODING,
            "computer_science": Domain.CODING,
            "mathematics": Domain.MATHEMATICS,
            "science": Domain.SCIENCE,
        }[concept.domain]
        context = {"curriculum": True, "misconception_id": mid}
        if domain is Domain.CODING:
            context["language"] = "python"
        items.append(
            _emit(
                domain=domain,
                task_type="diagnostic_misconception",
                prompt=item.diagnostic_prompt or item.statement,
                answer=(item.diagnostic_answer or item.correct_explanation).strip(),
                solution=(
                    f"Misconception: {item.statement.strip()} "
                    f"Why it is wrong: {item.why_it_is_wrong.strip()} "
                    f"Correct: {item.correct_explanation.strip()}"
                ),
                concept_id=item.concept_id,
                education_level=EducationLevel(concept.education_level),
                observations=[item.statement.strip()],
                constraints=["Correct the misconception; do not invent a new error."],
                plan=["Name the false belief", "Explain the mechanism", "State the correction"],
                quality=reviewed_quality(["documented learner difficulty"]),
                source_key=f"edu-misc-{mid}",
                context=context,
            )
        )
    return items
