---
pretty_name: Open Reason
license: apache-2.0
task_categories:
  - text-generation
  - question-answering
language:
  - en
tags:
  - reasoning
  - coding
  - mathematics
  - science
  - education
  - provenance
  - evaluation
size_categories:
  - 1K<n<10K
configs:
  - config_name: coding
    data_files:
      - split: train
        path: data/release/coding.parquet
  - config_name: reasoning
    data_files:
      - split: train
        path: data/release/reasoning.parquet
  - config_name: science
    data_files:
      - split: train
        path: data/release/science.parquet
  - config_name: mathematics
    data_files:
      - split: train
        path: data/release/mathematics.parquet
  - config_name: human
    data_files:
      - split: train
        path: data/release/human.parquet
  - config_name: education
    data_files:
      - split: train
        path: data/release/education.parquet
  - config_name: core
    data_files:
      - split: train
        path: data/release/core.parquet
  - config_name: verified
    data_files:
      - split: train
        path: data/release/verified.parquet
  - config_name: all
    data_files:
      - split: train
        path: data/release/all.parquet
---

# Dataset Card for Open Reason

**An open, verified dataset for coding, science, mathematics, and human reasoning.**

- Dataset: https://huggingface.co/datasets/theworker02/open-reason
- Small model: https://huggingface.co/theworker02/open-reason-small (~1.3M CPU causal LM; not 1B)
- Medium model: https://huggingface.co/theworker02/open-reason-medium (13,867,008 CPU causal LM; not 1B)
- Large model: https://huggingface.co/theworker02/open-reason-large (91,544,064 CPU causal LM; not 1B)
- XL model: https://huggingface.co/theworker02/open-reason-xl (443,719,680 CPU causal LM; not 1B)
- GitHub: https://github.com/theworker02/open-reason
- Site: https://theworker02.github.io/open-reason/

Open Reason is a provenance-aware corpus plus a reproducible pipeline. It is intended for training and evaluating systems on coding, mathematics, science, structured decision-making, and human problem solving.

**Open Reason does not use Reddit as a data source.** Quora is not a primary source of truth. Case study: [docs/why-not-reddit.md](docs/why-not-reddit.md).

## Supported tasks

- Code generation, debugging, SQL, systems simulations, packaging, and defensive validation
- Structured reasoning (planning, constraints, causal and temporal problems)
- Mathematical problem solving with symbolic or integer checks
- Scientific calculation, modeling, and experimental-design counts
- Teaching, explanation, and synthesis (human-authored)
- Curriculum-aligned education tasks with concept ids and education levels

## Languages

Prompts and solutions are English. Verified coding languages in v1.4.0: Python, SQL, JavaScript (when the sandbox can run them). Other languages appear as original concept tasks and are not marked verified.

## Source information

| Kind | How to recognize | v1.4.0 |
| --- | --- | --- |
| Human-authored | `provenance.source_type = human_authored` | Teaching, synthesis, qualitative items |
| Synthetic | `provenance.source_type = synthetic` plus `generator` | Math, science, most reasoning/coding, curriculum |
| Source-derived | `open_source` / `community` with provenance URL/commit | GitHub-permissive original tasks; Stack Overflow *seeds* (`verbatim=false`) |
| Verified | `quality.verified = true` and `verification.passed = true` | Coding sandbox, sympy, numeric, constraint checks |
| Unverified | `quality.verified = false` | Reviewed teaching and misconception items (tier A) |

Never treat synthetic rows as human-authored. Never treat unverified rows as executed.

## Licensing

Original dataset content and pipeline: [Apache 2.0](LICENSE). Per-row `provenance.license_spdx` is authoritative for upstream GitHub/SO snippets.

## Provenance

See [docs/provenance.md](docs/provenance.md). Unknown origin requires `unknown_reason`.

## Preprocessing

Unicode NFKC, newline normalization, trimmed lists, `task_type` slugging. Meaning is not paraphrased.

## Deduplication

Exact SHA-256 of canonical fields, normalized prompt/answer hashes, 64-bit simhash. Stats in the release manifest.

## Contamination controls

`configs/denylist.yaml` fingerprints known eval sets. Hits are reported, not silently deleted. `--strict` fails the build on hits. Hold out `benchmarks/` from training.

## Quality controls

Schema, SPDX allowlist, Reddit rejection, Quora-as-source rejection, PII heuristics, sandbox/sympy/numeric checks, community-votes-are-not-verification. Tiers S/A/B/C: [docs/quality.md](docs/quality.md). Reddit case study: [docs/why-not-reddit.md](docs/why-not-reddit.md). `evidence_confidence` is not a claim of truth.

## Intended uses

Research on reasoning and code models; filtering by domain, language, tier, and license; evaluation using the separate `benchmarks/` suite.

## Limitations

Small v1.4.0 corpus (~3.2K rows); still English-centric; verified coding languages limited to sandbox runtimes; teaching items are not executable oracles unless a numeric/sympy/sandbox check exists; third-party educational sites are registered but not scraped; denylists cannot be complete.

## Bias considerations

Synthetic generators encode the authors' choice of topics (software engineering, STEM calculations, operational triage). They under-represent many human domains and languages.

## Ethical considerations

No Reddit/social dumps. Case study: [docs/why-not-reddit.md](docs/why-not-reddit.md). Defensive security only. Minimize PII. Do not present this as a universal "human reasoning" sample.

## Maintenance

Issues and PRs: https://github.com/theworker02/open-reason  
Hugging Face dataset: https://huggingface.co/datasets/theworker02/open-reason  
Small CPU model (~1.3M): https://huggingface.co/theworker02/open-reason-small  
Medium CPU model (13,867,008): https://huggingface.co/theworker02/open-reason-medium  
Large CPU model (91,544,064): https://huggingface.co/theworker02/open-reason-large  
XL CPU model (443,719,680): https://huggingface.co/theworker02/open-reason-xl  
Releases are immutable; GitHub tags map to Hub revisions. Fixes ship in a new version. Shards are not stored in the GitHub git tree.

## Citation

See `CITATION.cff` and the README BibTeX entry.

## v1.4.0 snapshot

<!-- BEGIN_RELEASE_SNAPSHOT -->
Pipeline version **1.4.0**.

| Configuration | Examples | Verified | Human-authored |
| --- | ---: | ---: | ---: |
| coding | 400 | 386 | 0 |
| reasoning | 580 | 580 | 0 |
| science | 527 | 527 | 0 |
| mathematics | 1050 | 1050 | 0 |
| human | 289 | 261 | 28 |
| education | 345 | 111 | 0 |
| core | 3175 | 2899 | 28 |
| verified | 2899 | 2899 | 0 |
| all | 3175 | 2899 | 28 |

Rebuild with `open-reason build --config all --seed 42 --out data/release`.
Full tables: `data/release/statistics.md`.
<!-- END_RELEASE_SNAPSHOT -->

