# Knowledge graph

Open Reason keeps an internal curriculum graph under `knowledge_graph/`.

The graph is **original structure** for this project. It is inspired by common learning progressions (variables before loops, arithmetic before algebra) and is **not** a copy of Khan Academy, MIT OCW, CS50, or MDN lesson text.

## Files

| File | Role |
| --- | --- |
| `knowledge_graph/concepts.yaml` | Concepts, prerequisites, education level |
| `knowledge_graph/misconceptions.yaml` | Documented learner difficulties |
| `knowledge_graph/trajectories.yaml` | Ordered learning paths |
| `taxonomy/task_types.yaml` | Task taxonomy |
| `taxonomy/domains.yaml` | Domains, education levels, difficulty |

## Relationships

```text
concept → prerequisite → skill → exercise → application → verification
```

Difficulty and `education_level` are independent. A high-school concept can still be an advanced exercise.

## Evidence graph

High-confidence examples should accumulate independent edges:

```text
CLAIM
 ├── educational_source
 ├── authoritative_source
 ├── community_evidence
 ├── implementation_evidence
 └── verification
```

Community votes never set `quality.verified`. That flag requires an actual check.

Conflicts are recorded on `evidence.conflicts` and sent to the review queue instead of being silently resolved.

See `src/open_reason/knowledge/` and `open-reason generate --domain education`.
