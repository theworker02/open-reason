# Verification

## Coding

Python tasks run `unittest` inside `open_reason.verification.sandbox.Sandbox`. SQL tasks execute against in-memory SQLite. JavaScript tasks run under Node when `node` is on `PATH`.

A debugging example is kept only if:

1. the buggy files **fail** the tests
2. the fixed files **pass** the tests

Failure output is stored on the example. Passing output is stored in `verification`.

## Mathematics

Answers are recomputed with sympy or exact integer arithmetic. Failed checks are dropped.

## Science

Numeric formulas are recomputed independently (`math.isclose` with documented tolerances).

## Reasoning / human

Where a checker exists (capacity, constraints, EMV, integer identities), `verification.method` names it. Teaching items are tier A and are **not** marked verified.

## Honesty rule

If a check was not run, `quality.verified` remains false. There is no "probably correct" flag.
