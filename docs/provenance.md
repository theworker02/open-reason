# Provenance

Every example includes a `provenance` object. Fabricating repository names, commits, URLs, or citations is a pipeline bug.

## Source types

| `source_type` | Meaning |
| --- | --- |
| `human_authored` | Written by Open Reason contributors for this dataset |
| `synthetic` | Produced by a named generator and version |
| `open_source` | Extracted from a commit-pinned repository |
| `documentation` | Extracted from version-pinned docs |
| `specification` | Standard or RFC with redistribution rights |
| `scientific` | Open scientific source |
| `educational` | Structured educational source after license review |
| `community` | Community evidence (for example Stack Exchange); not ground truth |
| `unknown` | Allowed only with `unknown_reason`; rejected in `--strict` and forbidden for tier S |

## Synthetic records

Must set `generator` and `generator_version`. Optional `derived_from` if a parent example id exists.

## Checks

- Reddit URL / source / dataset fingerprints → reject ([why-not-reddit.md](why-not-reddit.md))
- Missing SPDX on non-unknown records → reject (default policy)
- Tier S forbids unknown provenance

See `src/open_reason/provenance/`.
