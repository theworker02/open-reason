# Licensing

## Software

The Open Reason pipeline, schemas, and tests are licensed under **Apache License 2.0** (`LICENSE`).

## Dataset

Original examples (human-authored and synthetic) are licensed under **CC BY 4.0** (`LICENSE-DATA`).

## Per-example SPDX

`provenance.license_spdx` is the license that applies to that row's content. Users who redistribute a filtered subset must honor the licenses of the rows they keep.

## Allowlist

Permissive SPDX identifiers live in `configs/licenses.yaml` and `open_reason.provenance.licenses`. Unknown or proprietary identifiers are rejected. Copyleft identifiers require an explicit source-policy exception and are **not** silently converted to CC-BY-4.0.

## Attribution

Cite the dataset (see `CITATION.cff`). Preserve `id`, `provenance`, and `license_spdx` when republishing rows.
