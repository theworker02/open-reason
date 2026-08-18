"""Executable verification for coding, mathematics, and science examples."""

from __future__ import annotations

import ast
import json
import math
import re
from typing import Any

import sympy as sp

from open_reason.models import Example, Verification
from open_reason.verification.sandbox import PYTHON_HARNESS, Sandbox, SandboxResult


def parse_harness_payload(stdout: str) -> dict[str, Any] | None:
    for line in stdout.splitlines():
        if line.startswith("OPEN_REASON_RESULT "):
            return json.loads(line[len("OPEN_REASON_RESULT ") :])
    return None


def verify_python_files(
    files: dict[str, str],
    sandbox: Sandbox | None = None,
    extra_files: dict[str, str] | None = None,
) -> tuple[SandboxResult, dict[str, Any] | None]:
    sandbox = sandbox or Sandbox()
    payload_files = dict(files)
    payload_files.setdefault("harness.py", PYTHON_HARNESS)
    if extra_files:
        payload_files.update(extra_files)
    result = sandbox.run_python(payload_files, [sandbox.python_executable, "harness.py"])
    return result, parse_harness_payload(result.stdout)


def verification_from_sandbox(result: SandboxResult, payload: dict[str, Any] | None) -> Verification:
    tests_passed = None
    tests_failed = None
    if payload:
        run = int(payload.get("tests_run") or 0)
        failed = int(payload.get("failures") or 0) + int(payload.get("errors") or 0)
        tests_failed = failed
        tests_passed = max(run - failed, 0)
    return Verification(
        method=f"sandbox:{result.backend}",
        passed=result.ok and (payload or {}).get("passed", result.ok) is True,
        result="passed" if result.ok else "failed",
        command="python harness.py",
        tests_passed=tests_passed,
        tests_failed=tests_failed,
        stdout=result.stdout,
        stderr=result.stderr,
        details={"timed_out": result.timed_out, "payload": payload or {}},
    )


def verify_math_answer(expression: str, expected: str) -> Verification:
    """Independently evaluate a sympy-compatible expression or equality."""
    try:
        left = sp.simplify(sp.sympify(expression))
        right = sp.simplify(sp.sympify(expected))
        ok = bool(sp.Eq(left, right)) or bool(sp.simplify(left - right) == 0)
        if not ok:
            try:
                ok = math.isclose(float(left), float(right), rel_tol=1e-9, abs_tol=1e-9)
            except (TypeError, ValueError):
                ok = False
        return Verification(
            method="sympy",
            passed=ok,
            result=str(left),
            details={"expected": str(right), "got": str(left)},
        )
    except (sp.SympifyError, TypeError, ValueError) as exc:
        return Verification(method="sympy", passed=False, result="error", details={"error": str(exc)})


def verify_numeric(got: float, expected: float, *, rel_tol: float = 1e-6, abs_tol: float = 1e-8) -> Verification:
    ok = math.isclose(got, expected, rel_tol=rel_tol, abs_tol=abs_tol)
    return Verification(
        method="numeric",
        passed=ok,
        result=str(got),
        details={"expected": expected, "got": got},
    )


SAFE_MATH_NAMES = {
    "abs": abs,
    "min": min,
    "max": max,
    "round": round,
    "pow": pow,
    "math": math,
}


def eval_numeric_formula(formula: str, variables: dict[str, float]) -> float:
    """Evaluate a restricted arithmetic formula."""
    tree = ast.parse(formula, mode="eval")
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id not in variables and node.id not in SAFE_MATH_NAMES:
            raise ValueError(f"disallowed name: {node.id}")
        if isinstance(node, ast.Attribute) and getattr(node.value, "id", None) != "math":
            raise ValueError("only math.* attributes are allowed")
        if isinstance(
            node,
            (
                ast.Call,
                ast.BinOp,
                ast.UnaryOp,
                ast.Expression,
                ast.Load,
                ast.Name,
                ast.Constant,
                ast.Attribute,
                ast.Pow,
                ast.Add,
                ast.Sub,
                ast.Mult,
                ast.Div,
                ast.Mod,
                ast.USub,
                ast.UAdd,
                ast.FloorDiv,
            ),
        ):
            continue
        if isinstance(node, (ast.List, ast.Tuple, ast.Dict, ast.Subscript)):
            raise ValueError("compound values are not allowed")
    merged = dict(SAFE_MATH_NAMES)
    merged.update(variables)
    value = eval(compile(tree, "<numeric>", "eval"), {"__builtins__": {}}, merged)
    return float(value)


ANSWER_TOKEN_RE = re.compile(r"^-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$")
