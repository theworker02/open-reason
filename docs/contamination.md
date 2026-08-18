# Contamination control

The denylist in `configs/denylist.yaml` stores **fingerprints** (prompt prefixes and distinctive needles) for evaluation sets such as HumanEval, MBPP, GSM8K, MATH, MMLU, SWE-bench, and LiveCodeBench. It does not store benchmark answers.

`open-reason build` writes hit counts into `data/release/manifest.yaml`. Hits are **reported**. `--strict` fails the build if any hit remains.

Training users should still hold out `benchmarks/` and any external eval they care about. Open Reason's own eval items in `benchmarks/` are not copied into training JSONL.
