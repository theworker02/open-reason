# Quality tiers

| Tier | Name | Requirements |
| --- | --- | --- |
| **S** | Verified | `quality.verified=true`, a passing `verification` object, known provenance, known SPDX, schema-valid, not a duplicate |
| **A** | Reviewed | Schema-valid, provenance-valid, human-authored or strongly checked, **not** claimed executed unless tests ran |
| **B** | Generated | Synthetic, structurally valid, automatic checks where they exist |
| **C** | Raw | Minimally processed; retained only if legal and useful (unused in v0.1) |

Filter:

```python
rows = [r for r in ds["train"] if json.loads(r["quality"])["tier"] == "S"]
```

Never mark an example verified because a model "looked correct." Community votes and accepted-answer flags **inform** `evidence_confidence`. They never set `quality.verified`.

`quality.evidence_confidence` is a weighted mix of authority, verification, cross-source support, community signals (capped), recency, and provenance completeness. It is not a claim of objective truth.

High-risk domains (medicine, law, finance, safety-critical engineering) cannot enter tier S without authoritative evidence **and** independent verification. Uncertain items go to the review queue.
