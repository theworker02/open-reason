# Approved sources

This directory is the **machine-readable catalog** of sources the policy engine
may enable for **original Open Reason tasks** (`curriculum_use: true`,
`verbatim: false`).

It is not a scrape dump. Third-party lesson text is not stored here.

## Files

| File | What it is |
| --- | --- |
| `catalog.yaml` | Source ids, SPDX, decision, enabled flag (from the live registry + policy) |
| `license_report.yaml` | SPDX rows; `relicensed_to_cc_by_4_0` is always false for third-party text |
| `original_tasks.sample.jsonl` | Metadata only (source id, task type, concept, prompt hash prefix) |

Refresh after registry changes:

```bash
open-reason catalogs --apply
```

Never approved: Reddit, Quora.
