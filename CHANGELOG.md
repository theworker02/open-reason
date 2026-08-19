# Changelog

## v1.0.1 — 2026-08-18

Coverage expansion: more original verified tasks across coding languages, CS
topics, math branches, science, reasoning, and checkable education items.
Teaching/explanation rows remain unverified without a numeric/sympy/sandbox
check. Third-party course sites are still not scraped.

### Dataset

- New Python sandbox tracks (graphs, DP, sorting, hashing, systems) plus
  error-diagnosis items with failing baselines
- Additional SQLite and JavaScript executable tasks
- Language-concept tasks for Java, C++, Kotlin, Haskell, shell, C# (not marked
  verified without a sandbox)
- New math families (complex modulus, binomial, modular inverse, composition)
  and science families (pendulum, gravity, molarity, Snell, interpretation)
- Distinct causal/planning/matching reasoning scenarios (not paraphrases)
- Coverage and curriculum banks grew with multiple task types per concept

### Policy (unchanged)

- Reddit forbidden; no KA/OCW/CS50/OpenStax/MDN/SO scrapes
- NC/SA never relicensed into CC BY 4.0 copies
- Hugging Face remains distribution; GitHub remains source of truth

## v1.0.0 — 2026-08-18

First 1.0 line: complete catalogs in every previously README-only section,
broader original task banks, and a rebuildable local dataset.

### Expanded directories

- `sources/approved|restricted|prohibited` — YAML catalogs, license report, fetch denylist, Reddit/Quora matchers, original-task metadata samples
- `evaluation/` — holdout metrics, fixtures, `open-reason score`
- `training/` — smoke config, SFT prepare script, eval protocol (still no fake 1B upload)
- `knowledge_graph/` — more concepts, misconceptions, trajectories, README
- `taxonomy/` — verification methods and license policy YAML
- `schemas/education.schema.json`
- `benchmarks/v1.jsonl` extra holdout items

### Dataset

- Coverage tasks cover multiple types per concept, not a single paraphrase
- Curriculum banks have several original items per auto-approved source
- New coding, math, science, reasoning, and human generators (checks still required for `quality.verified`)

### Policy

- Unchanged: Reddit forbidden; no KA/OCW/MDN/SO scrapes; NC/SA never relicensed to CC BY 4.0 copies
- `open-reason catalogs --apply` refreshes source directories from the policy engine

## v0.4.0 — 2026-08-18

Phase II: policy engine, coverage-driven original tasks, and a real (not faked) training pipeline.

### Audit (why v0.3 was thin)

- Knowledge graph had ~15 concepts; education emitted a handful of hand items plus ~1–2 tasks per curriculum source
- Auto-approve enabled sources but did not expand banks or scrape (correct: no KA/OCW/MDN/SO copies)
- Discovery scored nothing unless called; it never fed generation
- Mixed Parquet schema could fail on `all`; nullable-string schema is required

### Added

- `configs/source_policy.yaml` + `open_reason.policy` (AUTO_APPROVED / AUTO_REJECTED / METADATA_ONLY / REVIEW_REQUIRED)
- `open-reason discover`, `evaluate-sources`, `analyze-coverage`, `train`, `evaluate-model`, `release`
- Coverage task bank (concept × distinct task type) and expanded knowledge graph
- Training configs and smoke trainer; no Hugging Face model upload

### Policy

- Python/Rust/Go/SQL docs auto-approve **original tasks only**
- Khan/OCW/MDN auto-approve original tasks; `verbatim` stays false
- Stack Overflow / Stack Exchange: metadata only
- Reddit still AUTO_REJECTED

## v0.3.0 — 2026-08-18

Curriculum auto-approve so the dataset can be built without scraping, plus a professional README, mark, and usage GIFs.

### Added

- `open-reason sources --approve [--apply]` — deterministic license-policy auto-approve
- `open-reason build --auto-approve` — apply policy, then generate
- Original curriculum task banks for auto-approved educational and documentation sources
- Demo GIFs under `assets/demo/`

### Source policy

- Auto-approve enables **original Open Reason tasks** inspired by a source's public structure
- `verbatim` stays false; NC and share-alike licenses never enter the CC BY 4.0 release as copies
- Reddit and Quora cannot be approved
- Stack Exchange remains skipped (community evidence only, not ground truth)

### Dataset

- Education split now includes original tasks tagged `inspired_by` auto-approved sources
- Full `all` build publishes `core` and `verified` with matching `manifest.yaml` / `statistics.md` atomically
- Stable nullable-string Parquet schema so mixed `all` splits cannot change Arrow types mid-file
- GitHub vs Hugging Face split: shards gitignored; `distribution/dataset/` synced on GitHub Release only
- Rebuild with `open-reason sources --approve --apply` then `open-reason build --config all --seed 42`

## v0.2.0 — 2026-08-18

Source registry, knowledge graph, and curriculum split. Third-party sources remain disabled until license review.

### Added

- Machine-readable `sources/registry.yaml` with admission states and trust tiers 0–7
- Source-policy engine: unreviewed, prohibited, and metadata-only sources cannot emit examples
- Source discovery scores that never ingest and never set `enabled: true`
- Knowledge graph, misconceptions, and learning trajectories
- `education`, `core`, and `verified` dataset configurations
- Evidence graph fields, `education_level`, transformation history, `evidence_confidence`
- CLI: `sources`, `extract`, `transform`, `generate`, `benchmark`
- High-risk domain policy and human review queue
- Quora-as-authority rejection

### Source changes

- Active: Open Reason authors and Open Reason generators (CC BY 4.0)
- Review required / disabled: Khan Academy, MIT OCW, CS50, OpenStax, MDN, The Odin Project, official docs, Stack Exchange, OpenAlex metadata, and others listed in the registry
- Prohibited: Reddit (absolute), Quora as a primary source of truth

### Schema

- Core example model `0.2.0` (education level, evidence, transformation, temporal validity, runtime context)

### Validation

- Unreviewed sources fail closed; community votes cannot verify; high-risk domains cannot auto-enter tier S

### Known limitations

- No third-party websites are downloaded in this release
- Small corpus; verified coding languages limited; subprocess sandbox is not Docker

### Contamination

- Denylist scan enabled; training JSONL does not include `benchmarks/`

### Licensing

- Apache-2.0 software, CC BY 4.0 original data
- Future share-alike sources would keep their original SPDX and would not be relicensed as CC-BY-4.0

## v0.1.0 — 2026-08-18

Initial public pipeline and seed dataset.

### Added

- Core schema, CLI, validation, deduplication, contamination reporting, statistics
- Sandboxed verification for Python, SQLite, and Node
- Seeded generators for coding, reasoning, science, mathematics, and human splits
- Hugging Face configuration layout (`coding`, `reasoning`, `science`, `mathematics`, `human`, `all`)
- Reddit exclusion policy and automated checks
