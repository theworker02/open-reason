# Architecture

Open Reason is a **dataset infrastructure** project. The v0.2 release adds a license-gated source registry, knowledge graph, and curriculum split on top of the v0.1 verified seed.

## Design principles

1. **Provenance is mandatory.** Unknown origin is an explicit `source_type: unknown` with a reason, never an omitted field.
2. **Verification is empirical.** `quality.verified=true` is only set after a check actually ran and passed.
3. **Reddit is forbidden.** Connectors, validators, and contamination scans reject Reddit URLs, dumps, and known Reddit-derived datasets.
4. **Unreviewed sources emit nothing.** The registry must mark a source `approved`/`conditionally_approved` and `enabled: true` before ingestion.
5. **Determinism.** Generators take a seed. Identifiers are hashes of canonical payloads. JSONL is written with sorted keys.
6. **Streaming I/O.** JSONL and Parquet writers do not require the full release in RAM.
7. **Extensible configurations.** New domains register in `configs/datasets.yaml` and a generator module.

## Pipeline stages

```text
High-quality source
        ↓
Source validation
        ↓
License validation
        ↓
Content extraction
        ↓
Normalization
        ↓
Knowledge representation
        ↓
Task generation
        ↓
Verification
        ↓
Deduplication
        ↓
Quality scoring
        ↓
Contamination checks
        ↓
Dataset release
```

`open-reason build` runs this sequence for one configuration or for `all`.

Phase II CLI: `discover`, `evaluate-sources`, `ingest`, `build`, `verify`, `analyze-coverage`, `train`, `evaluate-model`, `release`. Discovery never ingests Reddit. `release` does not upload to Hugging Face.

## Distribution

GitHub holds the pipeline and catalogs. Hugging Face holds published shards.
`distribution/dataset/` is the Hub subdirectory (synced on GitHub Release, not
on every commit). Generated Parquet/JSONL under `data/release/` is local-only.

## Modules

| Package | Role |
| --- | --- |
| `open_reason.models` | Pydantic core schema |
| `open_reason.sources` | Registry, admission policy, discovery scores |
| `open_reason.ingestion` | Source connectors with a required `SourcePolicy` |
| `open_reason.generation` | Deterministic example factories |
| `open_reason.knowledge` | Curriculum graph loader |
| `open_reason.verification.sandbox` | Isolated execution (Docker if present, else limited subprocess) |
| `open_reason.deduplication` | Exact, normalized, and simhash near-duplicate detection |
| `open_reason.contamination` | Benchmark denylist scan (report, do not hide) |
| `open_reason.statistics` | Release tables for the dataset card |
| `open_reason.cli` | `open-reason` commands |

## Configurations

Current: `coding`, `reasoning`, `science`, `mathematics`, `human`, `education`, `core`, `verified`, `all`.

`all` is the validated union keyed by example `id`. `core` is tiers S and A. `verified` is tier S only.

Future names (`systems`, `languages`, `research`, `planning`, `technical`, `multilingual`) are reserved in `configs/datasets.yaml`.

## What is incomplete

- Live GitHub / documentation / educational / Stack Exchange crawlers (`enabled: false` in `sources/registry.yaml`). They define license contracts but emit no rows.
- Docker-based sandbox is implemented but unused unless `docker` is on `PATH`.
- Languages other than Python, SQL, and JavaScript are not in the verified coding split; we do not fabricate unverified multilingual dumps.

See [data-sources.md](data-sources.md), [knowledge-graph.md](knowledge-graph.md), [verification.md](verification.md), and [sandbox.md](sandbox.md).
