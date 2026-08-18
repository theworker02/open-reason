# Release shards (not in git)

Parquet and JSONL files for `theworker02/open-reason` are **published on a GitHub
Release**, then uploaded to this path on Hugging Face. They are not stored in
the GitHub git tree.

Local rebuild:

```bash
open-reason build --config all --seed 42 --out data/release
```

Hub layout (after a later publish, not this commit):

```text
data/release/coding.parquet
data/release/reasoning.parquet
data/release/science.parquet
data/release/mathematics.parquet
data/release/human.parquet
data/release/education.parquet
data/release/core.parquet
data/release/verified.parquet
data/release/all.parquet
```

Do not scrape Khan Academy, MIT OCW, MDN, or Stack Overflow. Open Reason does
not use Reddit as a data source.
