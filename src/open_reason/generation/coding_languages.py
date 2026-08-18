"""Original language-concept tasks. Not executed unless a sandbox exists.

These stay quality tier A: they are not marked verified.
"""

from __future__ import annotations

from open_reason.constants import PIPELINE_VERSION
from open_reason.generation.base import build_example, reviewed_quality
from open_reason.models import Domain, EducationLevel, Example
from open_reason.provenance import synthetic_provenance

SPECS: list[dict] = [
    {
        "slug": "js-this-arrow",
        "language": "javascript",
        "concept_id": "javascript.closures",
        "task_type": "concept_explanation",
        "prompt": "Why does an arrow function not get its own `this`, and when is that useful in a method callback?",
        "answer": "Arrow functions close over lexical this. Method callbacks keep the instance instead of becoming undefined or the global object.",
        "solution": "function methods get this from the call site. Nested function(){} loses it. An arrow keeps the method's this.",
    },
    {
        "slug": "ts-narrowing",
        "language": "typescript",
        "concept_id": "javascript.closures",
        "task_type": "concept_explanation",
        "prompt": "In TypeScript, why does `if (typeof x === 'string')` let you call x.toUpperCase() inside the block?",
        "answer": "Control-flow narrowing: the compiler treats x as string in that branch.",
        "solution": "typeof guards refine union types. Outside the block x may still be number | string.",
    },
    {
        "slug": "c-stack-vs-heap",
        "language": "c",
        "concept_id": "python.variables",
        "task_type": "concept_explanation",
        "prompt": "In C, why is returning the address of a local array undefined behavior?",
        "answer": "Automatic storage ends at return, so the pointer dangles.",
        "solution": "Use caller-owned buffers, malloc with documented free, or a static object with a clear lifetime.",
    },
    {
        "slug": "sql-null-eq",
        "language": "sql",
        "concept_id": "cs.sql",
        "task_type": "debugging_exercise",
        "prompt": "A query `WHERE name = NULL` returns no rows even when name is null. Why, and what should you write?",
        "answer": "SQL three-valued logic: NULL = NULL is unknown, not true. Use `IS NULL`.",
        "solution": "Unknown filters out of WHERE. IS NULL is the null test.",
    },
    {
        "slug": "rust-clone-escape",
        "language": "rust",
        "concept_id": "rust.ownership",
        "task_type": "applied_exercise",
        "prompt": "When is Clone a legitimate way to keep using a value after a move, and when is it a smell?",
        "answer": "Clone is correct when you need two owned values. It is a smell when a borrow or redesign would suffice and copies are large.",
        "solution": "Prefer borrowing. Clone documents an extra allocation or deep copy.",
    },
    {
        "slug": "go-defer-unlock",
        "language": "go",
        "concept_id": "go.concurrency",
        "task_type": "applied_exercise",
        "prompt": "Why is `defer mu.Unlock()` after Lock a common mutex pattern in Go?",
        "answer": "Defer runs on every return path, so the lock is released after panics and early returns.",
        "solution": "Manual unlock on each return is easy to miss. Defer pairs with Lock at the start of the critical section.",
    },
]


def generate_language_concept_tasks() -> list[Example]:
    out: list[Example] = []
    for spec in SPECS:
        out.append(
            build_example(
                domain=Domain.CODING,
                task_type=spec["task_type"],
                prompt=spec["prompt"],
                answer=spec["answer"],
                solution=spec["solution"],
                constraints=["Original Open Reason wording. Not copied from vendor docs."],
                plan=["Name the language rule", "State the consequence", "Give the repair or use"],
                provenance=synthetic_provenance(
                    generator="open_reason.generation.coding_languages",
                    generator_version=PIPELINE_VERSION,
                    transformation="language_concept_task",
                    trust_tier="tier7_synthetic",
                ),
                quality=reviewed_quality(["language concept; not sandbox-executed"]),
                source_key=f"lang-{spec['slug']}",
                education_level=EducationLevel.UNDERGRADUATE,
                concept_id=spec["concept_id"],
                context={"language": spec["language"], "executed": False},
                metadata={"language": spec["language"], "verified_execution": False},
            )
        )
    return out
