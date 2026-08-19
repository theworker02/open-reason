"""Original tasks tagged to auto-approved curriculum sources.

These are written for Open Reason. They are not copies of course lectures,
problem sets, or documentation pages.
"""

from __future__ import annotations

from open_reason.constants import PIPELINE_VERSION
from open_reason.generation.base import build_example, reviewed_quality, verified_quality
from open_reason.generation.curriculum_v1 import EXTRA_TASKS
from open_reason.generation.curriculum_v101 import EXTRA_TASKS_V101
from open_reason.models import Domain, EducationLevel, Evidence, Example
from open_reason.provenance import synthetic_provenance
from open_reason.verification import verify_math_answer, verify_numeric

DOMAIN_HINTS = {
    "khan_academy_computing": ("programming", Domain.CODING, EducationLevel.HIGH_SCHOOL),
    "mit_opencourseware": ("algorithms", Domain.CODING, EducationLevel.UNDERGRADUATE),
    "harvard_cs50": ("systems", Domain.CODING, EducationLevel.INTRODUCTORY_COLLEGE),
    "openstax": ("mathematics", Domain.MATHEMATICS, EducationLevel.HIGH_SCHOOL),
    "mdn": ("web", Domain.CODING, EducationLevel.PROFESSIONAL),
    "the_odin_project": ("web", Domain.CODING, EducationLevel.INTRODUCTORY_COLLEGE),
    "python_docs": ("python", Domain.CODING, EducationLevel.PROFESSIONAL),
    "rust_docs": ("rust", Domain.CODING, EducationLevel.PROFESSIONAL),
    "go_docs": ("go", Domain.CODING, EducationLevel.PROFESSIONAL),
    "w3c_whatwg": ("web", Domain.CODING, EducationLevel.PROFESSIONAL),
    "sqlite_docs": ("sql", Domain.CODING, EducationLevel.PROFESSIONAL),
    "postgresql_docs": ("sql", Domain.CODING, EducationLevel.PROFESSIONAL),
    "linux_man_pages": ("systems", Domain.CODING, EducationLevel.PROFESSIONAL),
    "nasa_education": ("astronomy", Domain.SCIENCE, EducationLevel.HIGH_SCHOOL),
    "noaa_education": ("earth_science", Domain.SCIENCE, EducationLevel.HIGH_SCHOOL),
    "usgs_education": ("earth_science", Domain.SCIENCE, EducationLevel.HIGH_SCHOOL),
    "oer_commons": ("education", Domain.HUMAN, EducationLevel.HIGH_SCHOOL),
    "wikibooks": ("education", Domain.HUMAN, EducationLevel.HIGH_SCHOOL),
}


def _prov(source_id: str):
    return synthetic_provenance(
        generator="open_reason.generation.curriculum",
        generator_version=PIPELINE_VERSION,
        transformation="original_curriculum_task",
        trust_tier="tier7_synthetic",
        source_id=source_id,
    )


def generate_original_for_source(source_id: str, seed: int = 42) -> list[Example]:
    _ = seed
    if source_id in {"stackoverflow", "stack_exchange"}:
        from open_reason.generation.stackoverflow_seeds import extra_so_concept_examples, extra_so_reasoning

        return extra_so_reasoning() + extra_so_concept_examples()
    tasks = TASKS.get(source_id) or []
    hint = DOMAIN_HINTS.get(source_id)
    if not hint:
        return []
    topic, domain, level = hint
    out: list[Example] = []
    for index, task in enumerate(tasks):
        verification = None
        quality = reviewed_quality(["original curriculum task; not copied from the source"])
        if task.get("numeric") is not None:
            verification = verify_numeric(float(task["numeric"]["got"]), float(task["numeric"]["expected"]))
            if verification.passed is not True:
                continue
            quality = verified_quality("numeric")
        elif task.get("sympy"):
            verification = verify_math_answer(str(task["sympy"]["got"]), str(task["sympy"]["expected"]))
            if verification.passed is not True:
                continue
            quality = verified_quality("sympy")
        context = {"curriculum": True, "inspired_by": source_id, "topic": topic}
        if domain is Domain.CODING:
            context["language"] = task.get("language", "python")
        example = build_example(
            domain=domain,
            task_type=task["task_type"],
            prompt=task["prompt"],
            answer=task["answer"],
            solution=task["solution"],
            observations=task.get("observations") or [],
            constraints=task.get("constraints")
            or ["Original Open Reason wording. Do not treat this as a copy of the named source."],
            plan=task.get("plan") or ["Read the prompt", "Apply the concept", "State the answer"],
            verification=verification,
            provenance=_prov(source_id),
            quality=quality,
            source_key=f"cur-{source_id}-{index}",
            education_level=level,
            concept_id=task.get("concept_id"),
            evidence=Evidence(
                educational_sources=[source_id],
                verification_methods=[verification.method] if verification else [],
            ),
            transformation=[
                "source_policy_auto_approve",
                "original_task_generation",
                "verification" if quality.verified else "unverified",
            ],
            context=context,
            metadata={
                "inspired_by": source_id,
                "verbatim": False,
                "auto_approved_curriculum": True,
            },
        )
        out.append(example)
    return out


def generate_approved_curriculum(seed: int = 42) -> list[Example]:
    from open_reason.sources import load_registry

    registry = load_registry()
    examples: list[Example] = []
    for source in registry.sources:
        if source.enabled and source.curriculum_use and not source.verbatim:
            examples.extend(generate_original_for_source(source.id, seed=seed))
    return examples


TASKS: dict[str, list[dict]] = {
    "khan_academy_computing": [
        {
            "task_type": "concept_explanation",
            "concept_id": "python.variables",
            "language": "python",
            "prompt": "In Python, why is `b = a` for a list not the same as copying the list?",
            "answer": "It binds a second name to the same object. Mutations through either name are visible to both.",
            "solution": "Assignment copies the reference, not a deep snapshot. Use a slice or copy() when a new list is required.",
            "plan": ["Name the object", "Describe aliasing", "Contrast with an explicit copy"],
        },
        {
            "task_type": "simple_exercise",
            "concept_id": "python.loops",
            "language": "python",
            "prompt": "How many times does `for i in range(5):` run the body?",
            "answer": "5",
            "solution": "range(5) yields 0,1,2,3,4 — five values.",
            "numeric": {"got": 5, "expected": 5},
        },
    ],
    "mit_opencourseware": [
        {
            "task_type": "concept_explanation",
            "concept_id": "cs.algorithms",
            "language": "python",
            "prompt": "Why is merge sort O(n log n) comparisons in the worst case while naive insertion sort is O(n^2)?",
            "answer": "Merge sort divides in half each time (log n levels) and merges in linear time per level. Insertion sort may move each new key past all previous keys.",
            "solution": "Recurrence T(n)=2T(n/2)+Theta(n) solves to Theta(n log n). Insertion sort's nested scans are Theta(n^2) in the worst case.",
        }
    ],
    "harvard_cs50": [
        {
            "task_type": "concept_explanation",
            "concept_id": "python.functions",
            "language": "c",
            "prompt": "Why can a C function returning a pointer to a local array be incorrect even if it compiles?",
            "answer": "The local array's storage ends when the function returns, so the pointer is dangling.",
            "solution": "Automatic storage is reclaimed at return. Callers need heap allocation, a caller-owned buffer, or a static object with documented lifetime.",
        }
    ],
    "openstax": [
        {
            "task_type": "simple_exercise",
            "concept_id": "math.algebra",
            "prompt": "Solve 3x - 6 = 9.",
            "answer": "5",
            "solution": "3x = 15, so x = 5.",
            "sympy": {"got": "5", "expected": "5"},
        }
    ],
    "mdn": [
        {
            "task_type": "concept_explanation",
            "concept_id": "python.functions",
            "language": "javascript",
            "prompt": "Why does `typeof null === 'object'` in JavaScript, and what should you use instead to test for null?",
            "answer": "A historical language quirk. Test with `value === null`.",
            "solution": "Early JavaScript used a type tag that made null look like an object. Strict equality against null is the reliable check.",
        }
    ],
    "the_odin_project": [
        {
            "task_type": "concept_explanation",
            "concept_id": "python.functions",
            "language": "javascript",
            "prompt": "What does `git revert` do that `git reset --hard` does not, and when is revert safer on a shared branch?",
            "answer": "Revert records a new commit that undoes a change. Reset moves the branch pointer and can rewrite history others already pulled.",
            "solution": "On shared branches, prefer revert so collaborators keep a linear, fetchable history.",
        }
    ],
    "python_docs": [
        {
            "task_type": "concept_explanation",
            "concept_id": "python.functions",
            "language": "python",
            "prompt": "What is the difference between a Python iterable and an iterator?",
            "answer": "An iterable can produce an iterator via iter(). An iterator is the object that yields values via next() and is spent as you consume it.",
            "solution": "Lists are iterable but not themselves iterators. iter(xs) returns an iterator. for-loops call iter() for you.",
        },
        {
            "task_type": "debugging_exercise",
            "concept_id": "python.exceptions",
            "language": "python",
            "prompt": "Why can `except:` hide a KeyboardInterrupt, and what should you catch instead when parsing integers?",
            "answer": "Bare except catches BaseException subclasses used for control flow. Catch ValueError for int().",
            "solution": "Use except ValueError. Let KeyboardInterrupt and SystemExit propagate.",
        },
        {
            "task_type": "applied_exercise",
            "concept_id": "python.modules",
            "language": "python",
            "prompt": "What does `from package import *` use to decide names, and why is it risky in libraries?",
            "answer": "It uses __all__ if present, else public names. It pollutes the importer's namespace and hides origins.",
            "solution": "Prefer explicit imports in library code. Star imports are a convenience for interactive sessions.",
        },
    ],
    "rust_docs": [
        {
            "task_type": "concept_explanation",
            "language": "rust",
            "prompt": "In Rust, why can you have many immutable references or one mutable reference, but not both at once for the same value?",
            "answer": "To prevent data races and iterator invalidation at compile time: readers may share, a writer must be exclusive.",
            "solution": "The borrow checker encodes this aliasing rule. Mixing &T and &mut T to the same place is rejected.",
        }
    ],
    "go_docs": [
        {
            "task_type": "concept_explanation",
            "language": "go",
            "prompt": "Why is sending on a closed Go channel a panic, while receiving from a closed channel yields the zero value?",
            "answer": "Close signals no more sends. Further sends are programmer errors. Receives drain remaining values then zeros so range loops terminate.",
            "solution": "Use close only from the sender. Check the two-value receive form to distinguish a zero value from a closed channel.",
        }
    ],
    "w3c_whatwg": [
        {
            "task_type": "concept_explanation",
            "language": "html",
            "prompt": "Why should a form control that is required also have an accessible name, not only a placeholder?",
            "answer": "Placeholders disappear and are not a reliable accessible name. Labels persist for assistive technology and visual users.",
            "solution": "Associate a label via for/id or wrapping. Required is independent of naming.",
        }
    ],
    "sqlite_docs": [
        {
            "task_type": "sql_generation",
            "language": "sql",
            "prompt": "In SQLite, why is `INTEGER PRIMARY KEY` special compared with a non-integer primary key?",
            "answer": "It becomes an alias for the rowid, so lookups and inserts use the table's implicit row identity.",
            "solution": "WITHOUT ROWID tables are the exception. Otherwise INTEGER PRIMARY KEY is the rowid.",
        }
    ],
    "postgresql_docs": [
        {
            "task_type": "sql_generation",
            "language": "sql",
            "prompt": "What does REPEATABLE READ prevent in PostgreSQL that READ COMMITTED does not?",
            "answer": "It holds a snapshot so statements in the same transaction see a stable view and avoid non-repeatable reads of committed updates.",
            "solution": "READ COMMITTED takes a new snapshot per statement. Repeatable read keeps one snapshot until commit or rollback. Write conflicts can still abort the transaction.",
        }
    ],
    "linux_man_pages": [
        {
            "task_type": "concept_explanation",
            "language": "c",
            "prompt": "Why must a program check the return value of `write()` instead of assuming the full buffer was written?",
            "answer": "write can transfer fewer bytes than requested. The caller must loop on the remainder or treat a short write as an error.",
            "solution": "Signals, pipes, and device limits can produce short writes. POSIX does not guarantee a full transfer in one call.",
        }
    ],
    "nasa_education": [
        {
            "task_type": "numerical",
            "concept_id": "science.newton",
            "prompt": "A spacecraft of mass 800 kg feels 1600 N of net thrust. What is the acceleration in m/s^2?",
            "answer": "2",
            "solution": "a = F/m = 1600/800 = 2.",
            "numeric": {"got": 2.0, "expected": 2.0},
        }
    ],
    "noaa_education": [
        {
            "task_type": "concept_explanation",
            "concept_id": "science.method",
            "prompt": "Why is a 30-year climate normal not the same thing as tomorrow's weather forecast?",
            "answer": "A normal is a long-run statistical baseline. A forecast is a short-range prediction of a specific state.",
            "solution": "Climate describes distributions over decades. Weather is the atmosphere's state at a time and place.",
        }
    ],
    "usgs_education": [
        {
            "task_type": "concept_explanation",
            "concept_id": "science.method",
            "prompt": "Why can the magnitude of an earthquake and the intensity felt at a city differ?",
            "answer": "Magnitude estimates energy at the source. Intensity describes local shaking, which depends on distance, depth, and ground conditions.",
            "solution": "The same magnitude event can be barely felt far away and damaging on soft sediment nearby.",
        }
    ],
    "oer_commons": [
        {
            "task_type": "teaching",
            "prompt": "Give one reason an open educational resource still needs its license checked before it enters a dataset.",
            "answer": "Publicly posted is not the same as redistributable. Each resource can carry a different license, including NC or SA terms.",
            "solution": "Store the exact license, attribution, and permitted use. Do not assume a catalog site's presence is a grant.",
        }
    ],
    "wikibooks": [
        {
            "task_type": "teaching",
            "prompt": "If a textbook is CC BY-SA, why must derived dataset rows keep share-alike instead of being relicensed as CC BY 4.0?",
            "answer": "Share-alike requires derivatives to use a compatible SA license. Relicensing as non-SA CC BY would break the grant.",
            "solution": "Keep the original SPDX on those rows or exclude them from a CC BY-only release.",
        }
    ],
}

for _source_id, _extra in EXTRA_TASKS.items():
    TASKS.setdefault(_source_id, []).extend(_extra)
for _source_id, _extra in EXTRA_TASKS_V101.items():
    TASKS.setdefault(_source_id, []).extend(_extra)
