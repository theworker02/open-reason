# Releases

Versions follow `vMAJOR.MINOR.PATCH`. Default branch is `main`.

Each release must include:

- changelog
- statistics
- `core` and `verified` splits alongside domain configs
- source / schema / validation notes
- contamination report
- license reminder
- known limitations

`open-reason build --config all` writes the full catalog (`manifest.yaml`,
`statistics.md`, `README.md`) only after every configuration exists, then
publishes the directory atomically so a partial run cannot leave a stale
manifest next to newer JSONL.

## GitHub tag → Hugging Face revision

1. Rebuild locally: `open-reason build --config all --seed 42 --out data/release`.
2. Tag GitHub (`v0.3.0`, …). Attach `data/release/*.parquet` (and JSONL if needed)
   as **release assets**. Do not commit those shards to git.
3. Publishing a GitHub Release runs `.github/workflows/sync-huggingface.yml`,
   which syncs **only** `distribution/dataset/` (card, sample, pointers) to
   Hugging Face dataset `theworker02/open-reason`.
4. Upload the attached Parquet files to Hub `data/release/` so they match the
   dataset card `configs.data_files` paths. Hub-sync uses `--delete="*"`, so
   shards that live only on the Hub (outside that subdirectory) must be
   re-uploaded after a card sync, or copied into `distribution/dataset/data/release/`
   at publish time (still gitignored).

Published Parquet/JSONL for a tag is immutable. Fixes go in a new version; do
not silently rewrite published objects.

Reproduce:

```bash
pip install -e .
open-reason build --config all --seed 42 --out data/release
```

`metadata.pipeline_version` and `provenance.generator_version` record the code
that produced each row.
