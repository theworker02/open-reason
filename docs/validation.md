# Validation

```bash
open-reason validate
open-reason validate data/release
open-reason validate --config coding
open-reason validate --strict
```

Checks include:

- JSON / Pydantic schema
- `id` prefix `or-`
- solution or answer present
- Reddit exclusion
- Quora-as-source rejection
- SPDX allowlist
- PII heuristics (emails, phones, SSN-shaped tokens)
- coding `context.language`
- `quality.verified` implies `verification.passed is true`
- community votes cannot be a verification method
- high-risk domains cannot auto-enter tier S
- `--strict`: unknown provenance and contamination hits fail the build

Deduplication and contamination are separate stages but run during `open-reason build`.
