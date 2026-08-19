# Licensing

## Software and dataset

The Open Reason pipeline, schemas, tests, original examples, and published
dataset rows are licensed under **Apache License 2.0** (`LICENSE`). This is
the only project license.

## Per-example SPDX

`provenance.license_spdx` is the license that applies to that row's content.
Users who redistribute a filtered subset must honor the licenses of the rows
they keep (for example MIT/BSD/Apache GitHub snippets, or CC-BY-SA if a short
attributed Stack Overflow quote is present).

## Allowlist

Permissive SPDX identifiers live in `configs/licenses.yaml` and
`open_reason.provenance.licenses`. Unknown or proprietary identifiers are
rejected. Copyleft identifiers require an explicit source-policy exception and
are **not** silently converted to Apache-2.0.

## Attribution

Cite the dataset (see `CITATION.cff`). Preserve `id`, `provenance`, and
`license_spdx` when republishing rows.
