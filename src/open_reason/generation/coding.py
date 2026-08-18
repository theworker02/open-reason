"""Build verified coding examples from task banks."""

from __future__ import annotations

import json
import shutil
from typing import Any

from open_reason.constants import PIPELINE_VERSION
from open_reason.generation.base import build_example, verified_quality
from open_reason.generation.coding_extra import extra_python_tasks
from open_reason.generation.coding_languages import generate_language_concept_tasks
from open_reason.generation.coding_micro import micro_python_tasks
from open_reason.generation.coding_python import all_python_tasks
from open_reason.generation.coding_sql_js import JS_TASKS, SQL_TASKS
from open_reason.generation.coding_v1 import v1_python_tasks
from open_reason.models import Domain, Example, Verification
from open_reason.provenance import synthetic_provenance
from open_reason.verification import parse_harness_payload, verification_from_sandbox
from open_reason.verification.sandbox import PYTHON_HARNESS, Sandbox


def _prov() -> Any:
    return synthetic_provenance(
        generator="open_reason.generation.coding",
        generator_version=PIPELINE_VERSION,
    )


def _python_files(code: str, tests: str) -> dict[str, str]:
    return {"solution.py": code, "test_solution.py": tests, "harness.py": PYTHON_HARNESS}


def _mutate_code(code: str) -> str | None:
    """Introduce a small defect so debugging tasks have a real failing baseline."""
    replacements = (
        ("return True", "return False"),
        ("return False", "return True"),
        ("return not ", "return "),
        (" <= ", " < "),
        (" >= ", " > "),
        (" == ", " != "),
        (" + ", " - "),
        (" // ", " / "),
    )
    for old, new in replacements:
        if old in code:
            mutated = code.replace(old, new, 1)
            if mutated != code:
                return mutated
    return None


def generate_coding(seed: int = 42, sandbox: Sandbox | None = None) -> list[Example]:
    sandbox = sandbox or Sandbox()
    examples: list[Example] = []
    examples.extend(_python_examples(sandbox))
    examples.extend(_sql_examples(sandbox))
    if shutil.which("node"):
        examples.extend(_js_examples(sandbox))
    examples.extend(generate_language_concept_tasks())
    return examples


def _python_examples(sandbox: Sandbox) -> list[Example]:
    out: list[Example] = []
    for task in [*all_python_tasks(), *extra_python_tasks(), *micro_python_tasks(), *v1_python_tasks()]:
        files = _python_files(task["code"], task["tests"])
        result, payload = _run_python(sandbox, files)
        verification = verification_from_sandbox(result, payload)
        if verification.passed is not True:
            continue
        tests_passed = verification.tests_passed or 0
        context = {
            "language": "python",
            "repository": {"files": {"solution.py": task["code"], "test_solution.py": task["tests"]}},
            "topic": task["topic"],
        }
        example = build_example(
            domain=Domain.CODING,
            task_type=task["task_type"],
            prompt=task["prompt"],
            solution=task["code"],
            answer=task["code"],
            context=context,
            constraints=[
                "Use only the Python standard library unless the prompt says otherwise.",
                "The hidden tests in test_solution.py must pass.",
            ],
            plan=["Read the specification", "Implement the function or class", "Satisfy the tests"],
            verification=verification,
            provenance=_prov(),
            quality=verified_quality("sandbox:python"),
            source_key=f"py-{task['slug']}",
            metadata={"language": "python", "topic": task["topic"], "slug": task["slug"]},
        )
        out.append(example)

        if not task.get("bug"):
            mutated = _mutate_code(task["code"])
            if mutated and mutated != task["code"]:
                task = dict(task)
                task["bug"] = mutated
                task["bug_note"] = "Seeded mutation of the reference implementation."
        if not task.get("bug"):
            continue
        fail_files = _python_files(task["bug"], task["tests"])
        fail_result, fail_payload = _run_python(sandbox, fail_files)
        if fail_result.ok:
            continue
        fail_ver = verification_from_sandbox(fail_result, fail_payload)
        debug_context = {
            "language": "python",
            "repository": {"files": {"solution.py": task["bug"], "test_solution.py": task["tests"]}},
            "failure": {
                "command": "python harness.py",
                "output": (fail_result.stdout + "\n" + fail_result.stderr)[-4000:],
            },
            "topic": task["topic"],
        }
        debug = build_example(
            domain=Domain.CODING,
            task_type="debugging",
            prompt=(
                "The following Python module fails its tests. Produce a corrected "
                "solution.py that preserves the intended behaviour.\n\n"
                f"{task['prompt']}\n\n"
                f"--- solution.py (buggy) ---\n{task['bug']}\n"
                f"--- test_solution.py ---\n{task['tests']}\n"
                f"--- failure ---\n{debug_context['failure']['output'][:1500]}"
            ),
            solution=task["code"],
            answer=task["code"],
            context=debug_context,
            observations=[task.get("bug_note") or "Tests fail on the provided implementation."],
            constraints=["Do not weaken or delete tests", "Keep the public API"],
            plan=["Reproduce the failure", "Identify the defect", "Apply a minimal fix", "Re-run tests"],
            verification=verification,
            provenance=_prov(),
            quality=verified_quality("sandbox:python"),
            source_key=f"py-debug-{task['slug']}",
            metadata={
                "language": "python",
                "topic": task["topic"],
                "slug": task["slug"],
                "failure_verification": fail_ver.model_dump(mode="json"),
                "tests_passed_after_fix": tests_passed,
            },
        )
        out.append(debug)
    return out


def _run_python(sandbox: Sandbox, files: dict[str, str]):
    result = sandbox.run_python(files)
    return result, parse_harness_payload(result.stdout)


def _sql_examples(sandbox: Sandbox) -> list[Example]:
    out: list[Example] = []
    for task in SQL_TASKS:
        runner = _SQL_RUNNER.format(
            schema=task["schema"],
            query=task["query"],
            expected=json.dumps(task["expected"]),
        )
        result = sandbox.run_python({"run.py": runner, "harness.py": "import run\n"}, [sandbox.python_executable, "run.py"])
        payload = parse_harness_payload(result.stdout)
        passed = bool(payload and payload.get("passed"))
        verification = Verification(
            method=f"sandbox:{result.backend}:sqlite",
            passed=passed and result.ok,
            result="passed" if passed else "failed",
            command="python run.py",
            stdout=result.stdout,
            stderr=result.stderr,
            details={"payload": payload or {}},
        )
        if verification.passed is not True:
            continue
        out.append(
            build_example(
                domain=Domain.CODING,
                task_type="sql",
                prompt=task["prompt"] + "\n\nSchema and seed data:\n" + task["schema"].strip(),
                solution=task["query"].strip(),
                answer=task["query"].strip(),
                context={
                    "language": "sql",
                    "repository": {"files": {"schema.sql": task["schema"], "query.sql": task["query"]}},
                    "expected_rows": task["expected"],
                    "topic": "sql",
                },
                constraints=["SQLite dialect", "Return exactly the specified columns and order"],
                plan=["Read the schema", "Write a query", "Check row order and values"],
                verification=verification,
                provenance=_prov(),
                quality=verified_quality("sandbox:sqlite"),
                source_key=f"sql-{task['slug']}",
                metadata={"language": "sql", "slug": task["slug"]},
            )
        )
    return out


_SQL_RUNNER = '''\
import json
import sqlite3

schema = """{schema}"""
query = """{query}"""
expected = {expected}

conn = sqlite3.connect(":memory:")
conn.executescript(schema)
rows = [list(r) for r in conn.execute(query)]
exp = [list(r) for r in expected]
payload = {{"passed": rows == exp, "rows": rows, "expected": exp, "tests_run": 1, "failures": 0 if rows == exp else 1, "errors": 0}}
print("OPEN_REASON_RESULT " + json.dumps(payload))
raise SystemExit(0 if rows == exp else 1)
'''


def _js_examples(sandbox: Sandbox) -> list[Example]:
    out: list[Example] = []
    node = shutil.which("node")
    if not node:
        return out
    for task in JS_TASKS:
        files = {"solution.js": task["code"].strip() + "\n", "test.js": task["tests"].strip() + "\n"}
        result = sandbox.run(files, [node, "test.js"])
        payload = parse_harness_payload(result.stdout)
        passed = result.ok and (payload or {}).get("passed", result.ok) is True
        verification = Verification(
            method=f"sandbox:{result.backend}:node",
            passed=passed,
            result="passed" if passed else "failed",
            command="node test.js",
            tests_passed=(payload or {}).get("tests_run") if passed else 0,
            tests_failed=0 if passed else 1,
            stdout=result.stdout,
            stderr=result.stderr,
            details={"payload": payload or {}, "timed_out": result.timed_out},
        )
        if verification.passed is not True:
            continue
        out.append(
            build_example(
                domain=Domain.CODING,
                task_type="code_generation",
                prompt=task["prompt"],
                solution=task["code"].strip(),
                answer=task["code"].strip(),
                context={
                    "language": "javascript",
                    "repository": {"files": files},
                    "topic": task["topic"],
                },
                constraints=["Node.js standard library only", "CommonJS module.exports"],
                plan=["Implement the exported function", "Keep the public API", "Pass the assertions"],
                verification=verification,
                provenance=_prov(),
                quality=verified_quality("sandbox:node"),
                source_key=f"js-{task['slug']}",
                metadata={"language": "javascript", "slug": task["slug"]},
            )
        )
    return out
