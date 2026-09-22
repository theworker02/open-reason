# Asset inventory â€” or: theworker02/open-reason-large / theworker02/open-reason-medium / theworker02/open-reason-small

## Repository surfaces

| Asset | Location / notes |
|-------|------------------|
| Source tree | Repository root / language packages |
| Tests | `test/`, `tests/`, CI workflows if present |
| Docs | `README.md`, `docs/` |
| Diligence room | `docs/acquisition/` |
| License / notices | `LICENSE`, transition notices if present |
| Funding | `.github/FUNDING.yml` |
| CI | `.github/workflows/` if present |
| Branding | logos/assets folders if present |

## Capability highlights

- **GitHub** [`theworker02/open-reason`](https://github.com/theworker02/open-reason) is the lab: pipeline, schemas, taxonomy, registry, tests, docs, configs, and small samples. Default branch is `main`. Full shards are **not** in git.
- **Hugging Face dataset** [`theworker02/open-reason`](https://huggingface.co/datasets/theworker02/open-reason) is distribution: Parquet shards and the dataset card.
- **Small CPU model** [`theworker02/open-reason-small`](https://huggingface.co/theworker02/open-reason-small) is a ~1.3M-parameter GPT-2-style causal LM.
- **Medium CPU model** [`theworker02/open-reason-medium`](https://huggingface.co/theworker02/open-reason-medium) is a 13,867,008-parameter GPT-2-style causal LM (CPU, not 1B).
- **Large CPU model** [`theworker02/open-reason-large`](https://huggingface.co/theworker02/open-reason-large) is a 91,544,064-parameter GPT-2-style causal LM (CPU, not 1B).
- **XL CPU model** [`theworker02/open-reason-xl`](https://huggingface.co/theworker02/open-reason-xl) is a 443,719,680-parameter GPT-2-style causal LM (CPU, not 1B). Weights are on the Hub, not in git.
- `open-reason build` writes local `data/release/`. Those `*.parquet` / `*.jsonl` shards are gitignored. A committed sample lives in `data/sample/`.
- Project: [Apache 2.0](LICENSE)
- Per-row `provenance.license_spdx` records upstream SPDX (GitHub MIT/BSD/Apache snippets, SO-inspired original rows)
- Share-alike and non-commercial third-party text is not relicensed into this release
- Quality over scale: this is a foundation, not a web dump
- Auto-approve does **not** download Khan Academy, MIT OCW, MDN, or Stack Overflow

## Usually excluded

Seller personal accounts, unrelated repos, and unreissued registry tokens â€” unless listed in the definitive agreement.

*Updated: 2026-09-22*
