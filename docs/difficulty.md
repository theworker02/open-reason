# Difficulty

Difficulty is **not** sampled uniformly.

`open_reason.generation.difficulty.score_example` accumulates a numeric score from:

- number of constraints, observations, and plan steps
- prompt length
- domain keywords (proof, concurrency, compiler, …)
- code size and test counts when present
- mathematical operator density

The score is bucketed:

| Score | Level |
| --- | --- |
| < 2.5 | introductory |
| < 4.5 | beginner |
| < 7.5 | intermediate |
| < 11 | advanced |
| < 15 | expert |
| ≥ 15 | research |

The breakdown is stored in `metadata.difficulty_score` so users can audit or re-bucket.
