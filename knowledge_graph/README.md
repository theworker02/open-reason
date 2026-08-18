# Open Reason knowledge graph

Concepts, documented misconceptions, and learning trajectories used by
education coverage and `open-reason analyze-coverage`.

These files are original curriculum structure. They are not copies of Khan
Academy, MIT OCW, CS50, or MDN outlines.

## Files

| File | Role |
| --- | --- |
| `concepts.yaml` | Concept ids, prerequisites, education levels |
| `misconceptions.yaml` | Diagnostic items linked from `common_mistakes` |
| `trajectories.yaml` | Ordered learning paths |

Load via `open_reason.knowledge.load_knowledge_graph()`. The graph rejects
missing links and prerequisite cycles.

Coverage is **not** one task type per concept: generators emit explanations,
exercises, debugging items, and diagnostics per concept where they exist.
