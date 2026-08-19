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
    examples.extend(_checkable_v101())
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


def _checkable_v101() -> list[Example]:
    """Education items with numeric/sympy checks. Teaching rows stay unverified."""
    items: list[Example] = []
    specs = [
        (
            "math.arithmetic",
            EducationLevel.K5,
            "simple_exercise",
            "What is 17 - 9?",
            "8",
            "17-9=8.",
            verify_numeric(8.0, 8.0),
            "edu-v101-sub",
        ),
        (
            "math.arithmetic",
            EducationLevel.K5,
            "simple_exercise",
            "What is 6 × 7?",
            "42",
            "6*7=42.",
            verify_numeric(42.0, 42.0),
            "edu-v101-mul",
        ),
        (
            "math.algebra",
            EducationLevel.HIGH_SCHOOL,
            "simple_exercise",
            "Solve 3x - 6 = 9. What is x?",
            "5",
            "3x=15, x=5.",
            verify_math_answer("5", "5"),
            "edu-v101-lin",
        ),
        (
            "math.geometry",
            EducationLevel.HIGH_SCHOOL,
            "simple_exercise",
            "A rectangle is 5 by 8. What is the area?",
            "40",
            "A=lw=40.",
            verify_numeric(40.0, 40.0),
            "edu-v101-rect",
        ),
        (
            "math.probability",
            EducationLevel.HIGH_SCHOOL,
            "simple_exercise",
            "A fair six-sided die. P(rolling a 5) as a reduced fraction a/b. Report a/b.",
            "1/6",
            "One favorable face of six.",
            verify_numeric(1 / 6, 1 / 6),
            "edu-v101-die",
        ),
        (
            "math.statistics",
            EducationLevel.HIGH_SCHOOL,
            "simple_exercise",
            "Mean of 2, 4, 6, 8?",
            "5",
            "(2+4+6+8)/4=5.",
            verify_numeric(5.0, 5.0),
            "edu-v101-mean",
        ),
        (
            "science.circuits",
            EducationLevel.HIGH_SCHOOL,
            "numerical",
            "Two 10 ohm resistors in parallel. Equivalent resistance in ohms?",
            "5",
            "1/R=1/10+1/10; R=5.",
            verify_numeric(5.0, 5.0),
            "edu-v101-par",
        ),
        (
            "science.waves",
            EducationLevel.HIGH_SCHOOL,
            "numerical",
            "A wave travels 12 m in 3 s. Speed in m/s?",
            "4",
            "v=d/t=4.",
            verify_numeric(4.0, 4.0),
            "edu-v101-speed",
        ),
        (
            "science.stoichiometry",
            EducationLevel.HIGH_SCHOOL,
            "numerical",
            "How many grams in 2 mol of a 12 g/mol element?",
            "24",
            "m=nM=24 g.",
            verify_numeric(24.0, 24.0),
            "edu-v101-mass",
        ),
        (
            "science.energy",
            EducationLevel.HIGH_SCHOOL,
            "numerical",
            "mgh with m=2 kg, g=10 m/s², h=3 m. Potential energy in J?",
            "60",
            "E=60 J.",
            verify_numeric(60.0, 60.0),
            "edu-v101-pe",
        ),
        (
            "cs.complexity",
            EducationLevel.UNDERGRADUATE,
            "simple_exercise",
            "A loop runs n=5 times, each time doing 3 constant steps. How many steps?",
            "15",
            "5*3=15.",
            verify_numeric(15.0, 15.0),
            "edu-v101-steps",
        ),
        (
            "math.discrete",
            EducationLevel.UNDERGRADUATE,
            "simple_exercise",
            "How many 2-element subsets of {a,b,c,d}?",
            "6",
            "C(4,2)=6.",
            verify_numeric(6.0, 6.0),
            "edu-v101-c42",
        ),
        (
            "math.linear_algebra",
            EducationLevel.UNDERGRADUATE,
            "simple_exercise",
            "Dot product of (1,2) and (3,4)?",
            "11",
            "1*3+2*4=11.",
            verify_numeric(11.0, 11.0),
            "edu-v101-dot",
        ),
        (
            "math.number_theory",
            EducationLevel.HIGH_SCHOOL,
            "simple_exercise",
            "What is 29 mod 7?",
            "1",
            "28+1.",
            verify_numeric(1.0, 1.0),
            "edu-v101-mod",
        ),
        (
            "science.genetics",
            EducationLevel.HIGH_SCHOOL,
            "numerical",
            "Aa × Aa, P(aa) as a decimal 0.25 or fraction 1/4. Report 0.25.",
            "0.25",
            "One of four Punnett cells.",
            verify_numeric(0.25, 0.25),
            "edu-v101-aa",
        ),
        (
            "math.sequences",
            EducationLevel.HIGH_SCHOOL,
            "simple_exercise",
            "Arithmetic sequence 4, 7, 10. What is the 5th term?",
            "16",
            "a_n=4+3(n-1); n=5 gives 16.",
            verify_numeric(16.0, 16.0),
            "edu-v101-arith5",
        ),
        (
            "science.optics",
            EducationLevel.HIGH_SCHOOL,
            "numerical",
            "Magnification m=-v/u with v=10, u=5 (same units). What is m?",
            "-2",
            "m=-10/5=-2.",
            verify_numeric(-2.0, -2.0),
            "edu-v101-mag",
        ),
        (
            "science.thermo",
            EducationLevel.HIGH_SCHOOL,
            "numerical",
            "Convert 10 °C of temperature change to kelvin difference.",
            "10",
            "ΔT in K equals ΔT in °C.",
            verify_numeric(10.0, 10.0),
            "edu-v101-dt",
        ),
    ]
    domain_for = {
        "math.arithmetic": Domain.MATHEMATICS,
        "math.algebra": Domain.MATHEMATICS,
        "math.geometry": Domain.MATHEMATICS,
        "math.probability": Domain.MATHEMATICS,
        "math.statistics": Domain.MATHEMATICS,
        "math.discrete": Domain.MATHEMATICS,
        "math.linear_algebra": Domain.MATHEMATICS,
        "math.number_theory": Domain.MATHEMATICS,
        "math.sequences": Domain.MATHEMATICS,
        "science.circuits": Domain.SCIENCE,
        "science.waves": Domain.SCIENCE,
        "science.stoichiometry": Domain.SCIENCE,
        "science.energy": Domain.SCIENCE,
        "science.genetics": Domain.SCIENCE,
        "science.optics": Domain.SCIENCE,
        "science.thermo": Domain.SCIENCE,
        "cs.complexity": Domain.CODING,
    }
    for concept_id, level, task_type, prompt, answer, solution, verification, key in specs:
        if verification.passed is not True:
            continue
        method = verification.method or "numeric"
        quality = verified_quality("sympy" if method == "sympy" else "numeric")
        context = {"curriculum": True, "concept_id": concept_id, "checkable": True}
        if domain_for[concept_id] is Domain.CODING:
            context["language"] = "python"
        items.append(
            _emit(
                domain=domain_for[concept_id],
                task_type=task_type,
                prompt=prompt,
                answer=answer,
                solution=solution,
                concept_id=concept_id,
                education_level=level,
                observations=["Independently checked education item"],
                constraints=["Exact value as specified"],
                plan=["Apply the definition", "Compute", "Record the number"],
                quality=quality,
                verification=verification,
                source_key=key,
                context=context,
            )
        )
    return items
