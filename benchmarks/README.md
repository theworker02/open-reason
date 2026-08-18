# Open Reason evaluation suite

Held-out items live in `items.jsonl`. **Do not mix this file into training exports.**

`open-reason build` writes training/release data under `data/release/` only.

## Metrics

| Area | Metric |
| --- | --- |
| Coding | execution success, tests passed, pass@k |
| Reasoning | exact match on the structured answer, constraint satisfaction |
| Mathematics | exact/symbolic match, numeric tolerance |
| Science | numeric tolerance, interpretation labels |

v0.1 ships a small held-out JSONL generated from a **different seed** than the training split (`seed=2026`).
