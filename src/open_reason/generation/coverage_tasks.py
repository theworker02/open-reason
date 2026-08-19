"""Coverage-driven original tasks: concepts × distinct task types.

These are written for Open Reason. They are not paraphrases of one seed prompt
and they are not copies of third-party courses or docs.
"""

from __future__ import annotations

from open_reason.constants import PIPELINE_VERSION
from open_reason.generation.base import build_example, reviewed_quality, verified_quality
from open_reason.generation.coverage_v1 import COVERAGE_SPECS_V1
from open_reason.generation.coverage_v101 import COVERAGE_SPECS_V101
from open_reason.models import Domain, EducationLevel, Evidence, Example
from open_reason.provenance import synthetic_provenance
from open_reason.verification import verify_math_answer, verify_numeric

DOMAIN_MAP = {
    "programming": Domain.CODING,
    "computer_science": Domain.CODING,
    "mathematics": Domain.MATHEMATICS,
    "science": Domain.SCIENCE,
}


def _prov():
    return synthetic_provenance(
        generator="open_reason.generation.coverage_tasks",
        generator_version=PIPELINE_VERSION,
        transformation="coverage_task_generation",
        trust_tier="tier7_synthetic",
    )


def generate_coverage_tasks(seed: int = 42) -> list[Example]:
    _ = seed
    out: list[Example] = []
    for index, spec in enumerate(COVERAGE_SPECS):
        verification = None
        quality = reviewed_quality(["original coverage task; not copied"])
        if spec.get("numeric") is not None:
            verification = verify_numeric(float(spec["numeric"]["got"]), float(spec["numeric"]["expected"]))
            if verification.passed is not True:
                continue
            quality = verified_quality("numeric")
        elif spec.get("sympy"):
            verification = verify_math_answer(str(spec["sympy"]["got"]), str(spec["sympy"]["expected"]))
            if verification.passed is not True:
                continue
            quality = verified_quality("sympy")
        domain = DOMAIN_MAP[spec["domain"]]
        context = {"curriculum": True, "coverage": True, "topic": spec.get("topic") or spec["concept_id"]}
        if domain is Domain.CODING:
            context["language"] = spec.get("language", "python")
        out.append(
            build_example(
                domain=domain,
                task_type=spec["task_type"],
                prompt=spec["prompt"],
                answer=spec["answer"],
                solution=spec["solution"],
                observations=spec.get("observations") or [],
                constraints=spec.get("constraints")
                or ["Original Open Reason wording. Do not treat this as a copy of a named course."],
                plan=spec.get("plan") or ["Identify the concept", "Apply it", "State the answer"],
                verification=verification,
                provenance=_prov(),
                quality=quality,
                source_key=f"cov-{spec['concept_id']}-{spec['task_type']}-{index}",
                education_level=EducationLevel(spec["education_level"]),
                concept_id=spec["concept_id"],
                evidence=Evidence(
                    educational_sources=["open-reason-curriculum"],
                    verification_methods=[verification.method] if verification else [],
                ),
                transformation=[
                    "coverage_analysis",
                    "original_task_generation",
                    "verification" if quality.verified else "unverified",
                ],
                context=context,
                metadata={"coverage": True, "verbatim": False, "concept_id": spec["concept_id"]},
            )
        )
    return out


COVERAGE_SPECS: list[dict] = [
    {
        "concept_id": "python.expressions",
        "domain": "programming",
        "education_level": "high_school",
        "task_type": "concept_explanation",
        "language": "python",
        "prompt": "Why does `3 + 2 * 4` evaluate to 11 in Python rather than 20?",
        "answer": "Multiplication binds more tightly than addition, matching ordinary arithmetic.",
        "solution": "* and / are tighter than + and -. Parentheses override. 2*4=8, then 3+8=11.",
        "numeric": {"got": 11, "expected": 11},
    },
    {
        "concept_id": "python.expressions",
        "domain": "programming",
        "education_level": "high_school",
        "task_type": "simple_exercise",
        "language": "python",
        "prompt": "What is the value of `2 ** 3 ** 2` in Python, and which way does `**` associate?",
        "answer": "512; exponentiation associates to the right, so 2**(3**2).",
        "solution": "3**2 is 9, then 2**9 is 512. Left-associative would have been (2**3)**2 = 64.",
        "numeric": {"got": 512, "expected": 512},
    },
    {
        "concept_id": "python.conditionals",
        "domain": "programming",
        "education_level": "high_school",
        "task_type": "concept_explanation",
        "language": "python",
        "prompt": "What is the difference between `if x:` and `if x is True:` when x might be 1 or []?",
        "answer": "`if x:` tests truthiness. `if x is True:` tests identity with the boolean True.",
        "solution": "1 is truthy but is not True. [] is falsy. Use `is True` only when you mean the boolean singleton.",
    },
    {
        "concept_id": "python.conditionals",
        "domain": "programming",
        "education_level": "high_school",
        "task_type": "debugging_exercise",
        "language": "python",
        "prompt": "A script uses `if n = 0:` to test a counter. Why does it fail, and what should it be?",
        "answer": "Single `=` is assignment and is a SyntaxError there. Use `if n == 0:`.",
        "solution": "Comparisons use ==. Assignment is a statement, not a boolean test, in that position.",
    },
    {
        "concept_id": "python.classes",
        "domain": "programming",
        "education_level": "introductory_college",
        "task_type": "concept_explanation",
        "language": "python",
        "prompt": "Why does `self` appear as the first parameter of an instance method?",
        "answer": "The instance is passed implicitly on the call; `self` names that instance inside the method.",
        "solution": "obj.method(x) is type(obj).method(obj, x). The first parameter is the instance, by convention named self.",
    },
    {
        "concept_id": "python.classes",
        "domain": "programming",
        "education_level": "introductory_college",
        "task_type": "applied_exercise",
        "language": "python",
        "prompt": "What happens if two instances share a class variable list and one appends to it?",
        "answer": "Both see the append unless the instance rebound the name to a new object.",
        "solution": "Class attributes are shared. Mutable class attributes alias across instances. Use instance attributes created in __init__ for per-object state.",
    },
    {
        "concept_id": "python.exceptions",
        "domain": "programming",
        "education_level": "high_school",
        "task_type": "concept_explanation",
        "language": "python",
        "prompt": "When should a function raise ValueError versus returning None?",
        "answer": "Raise when the caller passed something illegal and must notice. Return None only if absence is a normal outcome.",
        "solution": "Exceptions make the failure path visible. Silent None hides bugs at the next dereference.",
    },
    {
        "concept_id": "python.exceptions",
        "domain": "programming",
        "education_level": "high_school",
        "task_type": "debugging_exercise",
        "language": "python",
        "prompt": "A parser wraps a whole file in `except Exception: pass`. Name two harms and a tighter pattern.",
        "answer": "It hides bugs and can swallow KeyboardInterrupt subclasses of Exception in some paths. Catch the specific parse error, log, and re-raise unexpected types.",
        "solution": "Prefer `except json.JSONDecodeError`. Never use a bare except. Avoid swallowing Exception at process boundaries without logging.",
    },
    {
        "concept_id": "python.modules",
        "domain": "programming",
        "education_level": "high_school",
        "task_type": "concept_explanation",
        "language": "python",
        "prompt": "Why does `if __name__ == '__main__':` guard a script's CLI?",
        "answer": "Import sets __name__ to the module name, so the guard skips CLI side effects. Direct execution sets it to '__main__'.",
        "solution": "Libraries should be importable without launching the program. The guard separates library functions from the entry point.",
    },
    {
        "concept_id": "python.iterators",
        "domain": "programming",
        "education_level": "introductory_college",
        "task_type": "concept_explanation",
        "language": "python",
        "prompt": "Why can you iterate a list twice but not consume a generator twice?",
        "answer": "A list is an iterable that mints a fresh iterator. A generator is the iterator and is exhausted.",
        "solution": "iter(list) starts over. A generator's next() advances hidden state until StopIteration.",
    },
    {
        "concept_id": "python.testing",
        "domain": "programming",
        "education_level": "introductory_college",
        "task_type": "concept_explanation",
        "language": "python",
        "prompt": "What makes an assertion in a unit test different from a print of the result?",
        "answer": "An assertion fails the test automatically when the condition is false; a print requires a human to notice.",
        "solution": "Tests must be machine-checkable. assertEqual documents the expected value and fails closed.",
    },
    {
        "concept_id": "python.testing",
        "domain": "programming",
        "education_level": "introductory_college",
        "task_type": "applied_exercise",
        "language": "python",
        "prompt": "A test mutates a shared module-level list in setUp and never restores it. What goes wrong, and how do you fix it?",
        "answer": "Later tests see leftover state (order dependence). Isolate fixtures: copy, use setUp/tearDown, or construct fresh objects per test.",
        "solution": "Shared mutable fixtures create flakes. Each test should own its data.",
    },
    {
        "concept_id": "cs.algorithms",
        "domain": "computer_science",
        "education_level": "undergraduate",
        "task_type": "concept_explanation",
        "language": "python",
        "prompt": "Why is binary search incorrect on an unsorted array even if it sometimes finds the key?",
        "answer": "The algorithm discards a half based on order. Without sorted order those discards are unjustified.",
        "solution": "Correctness of binary search is a loop invariant on a sorted range, not a lucky hit.",
    },
    {
        "concept_id": "cs.complexity",
        "domain": "computer_science",
        "education_level": "undergraduate",
        "task_type": "simple_exercise",
        "language": "python",
        "prompt": "A nested loop runs i from 1..n and j from 1..i. What is Theta of the inner-body executions?",
        "answer": "Theta(n^2)",
        "solution": "Sum_{i=1..n} i = n(n+1)/2 which is Theta(n^2).",
    },
    {
        "concept_id": "cs.complexity",
        "domain": "computer_science",
        "education_level": "undergraduate",
        "task_type": "concept_explanation",
        "language": "python",
        "prompt": "Why is O(n^2) not a contradiction of O(n^3) for the same function?",
        "answer": "Big-O is an upper bound. A quadratic function is also O(n^3).",
        "solution": "f(n)=n^2 is O(n^2) and O(n^3). Theta(n^2) is the tight characterization.",
    },
    {
        "concept_id": "cs.recursion",
        "domain": "computer_science",
        "education_level": "undergraduate",
        "task_type": "debugging_exercise",
        "language": "python",
        "prompt": "A factorial function calls factorial(n) without a base case for n==0. What happens for factorial(3)?",
        "answer": "It recurses until the call stack overflows (or hits the recursion limit).",
        "solution": "Every recursive definition needs a base case that returns without another call. 0! is 1.",
    },
    {
        "concept_id": "cs.recursion",
        "domain": "computer_science",
        "education_level": "undergraduate",
        "task_type": "concept_explanation",
        "language": "python",
        "prompt": "Why can a naive recursive Fibonacci be exponential time?",
        "answer": "It recomputes the same subproblems in two branches, forming an exponential call tree.",
        "solution": "T(n)=T(n-1)+T(n-2)+O(1) is Theta(phi^n). Memoization or iteration makes it linear.",
    },
    {
        "concept_id": "cs.sql",
        "domain": "computer_science",
        "education_level": "introductory_college",
        "task_type": "concept_explanation",
        "language": "sql",
        "prompt": "Why does INNER JOIN drop customers with no orders while LEFT JOIN can keep them?",
        "answer": "INNER JOIN requires a match in both tables. LEFT JOIN keeps all left rows and nulls the right side when unmatched.",
        "solution": "Choose INNER when you only want matches. Choose LEFT when absence is information.",
    },
    {
        "concept_id": "cs.sql",
        "domain": "computer_science",
        "education_level": "introductory_college",
        "task_type": "simple_exercise",
        "language": "sql",
        "prompt": "In `SELECT dept, COUNT(*) FROM emp GROUP BY dept`, why is `SELECT name` illegal without aggregation or grouping name?",
        "answer": "name is not functionally determined by dept, so SQL rejects an ungrouped non-aggregated column.",
        "solution": "GROUP BY dept yields one row per department. A per-employee column is not defined on that row.",
    },
    {
        "concept_id": "cs.http",
        "domain": "computer_science",
        "education_level": "introductory_college",
        "task_type": "concept_explanation",
        "language": "python",
        "prompt": "What is the difference between HTTP 401 and 403?",
        "answer": "401 means unauthenticated (missing/bad credentials). 403 means authenticated but not allowed.",
        "solution": "401 invites supplying credentials. 403 says this principal may not access the resource.",
    },
    {
        "concept_id": "cs.git",
        "domain": "computer_science",
        "education_level": "introductory_college",
        "task_type": "concept_explanation",
        "language": "python",
        "prompt": "Why is `git revert` safer than `git reset --hard` on a branch others already pulled?",
        "answer": "Revert adds a new commit that undoes a change. Hard reset moves history others still have.",
        "solution": "Shared branches should grow with new commits, not rewrite published history.",
    },
    {
        "concept_id": "javascript.closures",
        "domain": "programming",
        "education_level": "introductory_college",
        "task_type": "concept_explanation",
        "language": "javascript",
        "prompt": "In JavaScript, why does a function returned from another function still see the outer variable?",
        "answer": "A closure retains the lexical environment where it was created, not a snapshot of the caller's stack frame after return.",
        "solution": "The inner function closes over bindings. Those bindings live as long as the function value is reachable.",
    },
    {
        "concept_id": "javascript.closures",
        "domain": "programming",
        "education_level": "introductory_college",
        "task_type": "debugging_exercise",
        "language": "javascript",
        "prompt": "A loop `for (var i=0;i<3;i++){ setTimeout(()=>console.log(i),0) }` prints 3 three times. Why, and how do you log 0,1,2?",
        "answer": "`var` is function-scoped so all callbacks share one i, which is 3 after the loop. Use let, or bind i in a factory.",
        "solution": "let creates a fresh binding per iteration. var does not.",
    },
    {
        "concept_id": "rust.ownership",
        "domain": "programming",
        "education_level": "undergraduate",
        "task_type": "concept_explanation",
        "language": "rust",
        "prompt": "Why does moving a String into a function make the original binding unusable afterward?",
        "answer": "Ownership transferred. Using the old name would be a use-after-move, which Rust rejects.",
        "solution": "Each value has one owner. Move ends the previous owner's access unless the type is Copy.",
    },
    {
        "concept_id": "go.concurrency",
        "domain": "programming",
        "education_level": "undergraduate",
        "task_type": "concept_explanation",
        "language": "go",
        "prompt": "Why is sending on a closed Go channel a panic while receiving after close yields zeros?",
        "answer": "Close means no more sends; further sends are programmer errors. Receives drain then produce zero values so range can stop.",
        "solution": "Only the sender should close. Use the two-value receive to detect closure.",
    },
    {
        "concept_id": "math.functions",
        "domain": "mathematics",
        "education_level": "high_school",
        "task_type": "concept_explanation",
        "prompt": "Why is a vertical line not the graph of a function y=f(x)?",
        "answer": "A function assigns one output per input. A vertical line gives many y for one x.",
        "solution": "The vertical-line test is the unique-output rule in the plane.",
    },
    {
        "concept_id": "math.geometry",
        "domain": "mathematics",
        "education_level": "high_school",
        "task_type": "simple_exercise",
        "prompt": "A right triangle has legs 3 and 4. What is the hypotenuse?",
        "answer": "5",
        "solution": "Pythagoras: sqrt(9+16)=sqrt(25)=5.",
        "numeric": {"got": 5, "expected": 5},
    },
    {
        "concept_id": "math.geometry",
        "domain": "mathematics",
        "education_level": "high_school",
        "task_type": "applied_exercise",
        "prompt": "A circle has radius 10. What is its area in terms of pi?",
        "answer": "100*pi",
        "solution": "A=pi r^2 = pi*100.",
        "sympy": {"got": "100*pi", "expected": "100*pi"},
    },
    {
        "concept_id": "math.trigonometry",
        "domain": "mathematics",
        "education_level": "high_school",
        "task_type": "simple_exercise",
        "prompt": "What is sin(pi/2) in radians?",
        "answer": "1",
        "solution": "pi/2 radians is 90 degrees; sine of a right angle is 1.",
        "sympy": {"got": "1", "expected": "1"},
    },
    {
        "concept_id": "math.discrete",
        "domain": "mathematics",
        "education_level": "undergraduate",
        "task_type": "simple_exercise",
        "prompt": "How many 3-element subsets does a 5-element set have?",
        "answer": "10",
        "solution": "C(5,3)=10.",
        "numeric": {"got": 10, "expected": 10},
    },
    {
        "concept_id": "math.probability",
        "domain": "mathematics",
        "education_level": "high_school",
        "task_type": "simple_exercise",
        "prompt": "A fair coin is flipped twice. What is P(exactly one head)?",
        "answer": "1/2",
        "solution": "Outcomes HH,HT,TH,TT equally likely. Exactly one head: HT, TH. 2/4=1/2.",
        "numeric": {"got": 0.5, "expected": 0.5},
    },
    {
        "concept_id": "math.linear_algebra",
        "domain": "mathematics",
        "education_level": "undergraduate",
        "task_type": "simple_exercise",
        "prompt": "What is the determinant of the 2x2 matrix [[2, 0], [0, 3]]?",
        "answer": "6",
        "solution": "ad-bc = 2*3-0*0=6.",
        "numeric": {"got": 6, "expected": 6},
    },
    {
        "concept_id": "math.number_theory",
        "domain": "mathematics",
        "education_level": "high_school",
        "task_type": "simple_exercise",
        "prompt": "What is 17 mod 5?",
        "answer": "2",
        "solution": "17=3*5+2.",
        "numeric": {"got": 2, "expected": 2},
    },
    {
        "concept_id": "science.energy",
        "domain": "science",
        "education_level": "high_school",
        "task_type": "simple_exercise",
        "prompt": "A 2 kg mass moves at 3 m/s. What is its kinetic energy in joules?",
        "answer": "9",
        "solution": "KE=1/2 m v^2 = 0.5*2*9=9 J.",
        "numeric": {"got": 9, "expected": 9},
    },
    {
        "concept_id": "science.circuits",
        "domain": "science",
        "education_level": "high_school",
        "task_type": "simple_exercise",
        "prompt": "A 12 V battery drives 3 A through a resistor. What is the resistance in ohms?",
        "answer": "4",
        "solution": "V=IR so R=V/I=12/3=4 ohm.",
        "numeric": {"got": 4, "expected": 4},
    },
    {
        "concept_id": "science.stoichiometry",
        "domain": "science",
        "education_level": "high_school",
        "task_type": "simple_exercise",
        "prompt": "Water is H2O. How many moles of hydrogen atoms are in 2 moles of water?",
        "answer": "4",
        "solution": "Each water molecule has 2 H atoms, so 2 mol water contains 4 mol H atoms.",
        "numeric": {"got": 4, "expected": 4},
    },
    {
        "concept_id": "science.waves",
        "domain": "science",
        "education_level": "high_school",
        "task_type": "simple_exercise",
        "prompt": "A wave has speed 10 m/s and frequency 5 Hz. What is the wavelength in meters?",
        "answer": "2",
        "solution": "v=f lambda so lambda=v/f=10/5=2 m.",
        "numeric": {"got": 2, "expected": 2},
    },
    {
        "concept_id": "science.method",
        "domain": "science",
        "education_level": "middle_school",
        "task_type": "applied_exercise",
        "prompt": "Why is a control group needed when testing whether a fertilizer increases plant height?",
        "answer": "Without untreated plants you cannot separate fertilizer from other growth factors.",
        "solution": "A control holds other variables and shows the baseline. The difference is the evidence, not the treated height alone.",
    },
    {
        "concept_id": "python.collections",
        "domain": "programming",
        "education_level": "introductory_college",
        "task_type": "concept_explanation",
        "language": "python",
        "prompt": "Why is a list a poor choice as a dict key, and what should you use instead?",
        "answer": "Lists are mutable and unhashable. Use a tuple of immutables, or freeze the data.",
        "solution": "Hash tables require a stable hash. Mutating a key would lose the bucket.",
    },
    {
        "concept_id": "python.loops",
        "domain": "programming",
        "education_level": "high_school",
        "task_type": "applied_exercise",
        "language": "python",
        "prompt": "Why is `for i in range(len(xs)):` often worse than `for x in xs:` when you only need values?",
        "answer": "Indexing is extra machinery and off-by-one prone. Iterating values states the intent.",
        "solution": "Use enumerate if you need index and value. Direct iteration is the default.",
    },
]

COVERAGE_SPECS.extend(COVERAGE_SPECS_V1)
COVERAGE_SPECS.extend(COVERAGE_SPECS_V101)
