# Contributing

Thanks for helping build Open Reason.

## Rules that do not yield

- **No Reddit.** Posts, comments, dumps, APIs, archives, or Reddit-derived datasets will be rejected.
- **No fabricated provenance**, licenses, or citations.
- **No verified label without a check** that this repository can re-run.
- **No prompt paraphrases** whose only purpose is to inflate row counts.
- **No private chain-of-thought** collection.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src tests
open-reason build --config mathematics --seed 42
```

Default branch is `main`. Do not commit generated `data/release/*.parquet` or
`*.jsonl`. Rebuild locally; publish shards on a GitHub Release / Hugging Face.

## Adding examples

1. Prefer executable tests (coding) or independent computation (math/science).
2. Set `provenance` honestly (`human_authored` vs `synthetic`).
3. Run `open-reason validate --strict` on the files you add.

## Adding a source connector

1. Add a row to `sources/registry.yaml` with `enabled: false` and `status: review_required`.
2. Implement `open_reason.ingestion.Connector` with a complete `SourcePolicy`.
3. Do not set `enabled: true` until license, redistribution, and attribution are reviewed.
4. Discovery scores must never ingest. Reddit cannot be enabled. Quora is not a primary source of truth.
5. Incomplete connectors must yield nothing. Community votes never set `quality.verified`.

## Pull requests

Small, focused PRs against `main`. Describe source, license, and verification in the PR body.
