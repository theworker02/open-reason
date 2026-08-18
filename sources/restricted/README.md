# Restricted / review-required sources

Sources here are **not fetched**. Public web pages are not a redistribution
grant. Khan Academy, MIT OCW, MDN, Stack Overflow, and similar sites stay
off the crawler.

Original Open Reason tasks tagged `inspired_by` a source may exist only after
the policy engine sets `AUTO_APPROVED` with `verbatim: false`.

## Files

| File | What it is |
| --- | --- |
| `catalog.yaml` | Review-required and metadata-only registry rows |
| `fetch_denylist.yaml` | Hosts and source ids the pipeline must never download |

Refresh:

```bash
open-reason catalogs --apply
```
