# Prohibited sources

These sources cannot be enabled.

- **Reddit** — absolute exclusion (posts, comments, dumps, APIs, derived datasets). Case study: [docs/why-not-reddit.md](../../docs/why-not-reddit.md).
- **Quora** — not a primary source of truth

## Files

| File | What it is |
| --- | --- |
| `catalog.yaml` | Prohibited registry rows |
| `matchers.yaml` | Host and substring matchers used in tests and validators |

Refresh:

```bash
open-reason catalogs --apply
```

Open Reason does not use Reddit as a data source.
