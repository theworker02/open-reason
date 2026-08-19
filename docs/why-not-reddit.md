# Why Open Reason does not use Reddit

**Policy:** Open Reason does not use Reddit as a data source. The exclusion is absolute. It is not a preference, a backlog item, or a filter that can be relaxed for “high-quality subreddits.”

This document is the citable case study for that policy. It explains the research-infrastructure reasons (provenance, license, verification, contamination) and the project’s refusal to keep feeding a training loop that already exists at scale. It does not reproduce Reddit posts, comments, or dumps.

Related: [Data sources](data-sources.md), [Provenance](provenance.md), [Licensing](licensing.md), [Quality](quality.md), [Contamination](contamination.md), [Architecture](architecture.md). Public copy: [https://theworker02.github.io/open-reason/why-not-reddit.html](https://theworker02.github.io/open-reason/why-not-reddit.html).

## What Open Reason has to be able to claim

Every released row is supposed to answer three questions:

1. **Where did this come from?** (`provenance`, including source type, license, and generator or author).
2. **May a downstream user use it under the stated terms?** (`provenance.license_spdx` is authoritative per row).
3. **Was the answer actually checked?** (`quality.verified` is true only after a named check ran and passed).

A source that cannot support those claims cannot enter the corpus. Popularity, accessibility, and “everyone else trained on it” are not substitutes.

## The loop we are refusing to feed

It is widely known that a **large volume and variety of Reddit data** has been used to train contemporary AI systems: comment dumps, archives, third-party dataset releases, and scraped threads. That material is attractive because it is abundant, conversational, and already sitting in public crawls. Abundance is not a license, and it is not a verification protocol.

Those models often **absorb the personality of Reddit commenters**. The failure mode is not only factual error. It is a voice: performative certainty in place of knowledge, pile-ons in place of argument, mockery in place of correction, and a style of “listening” that is not actually advice. A great deal of that text **sounds like help and is not helpful**.

That is **dangerous**. Medical-, legal-, and financial-sounding chatter travels in the same streams as ordinary conversation. Harassment norms and unverifiable claims travel with them. A system that has ingested that register will reproduce it under the appearance of competence. At some point the loop has to be **stopped** — not by hoping a later alignment pass will wash it out, but by refusing the source.

Open Reason is a concrete refusal to keep feeding that loop. I am contributing what I can personally: this dataset and this pipeline do not use Reddit, **directly or indirectly**. There is no dump, no archive, no “Reddit-derived” mix, and no search-result workaround. If a candidate’s provenance includes Reddit, it is rejected.

A **very small trained model** is part of this project so the exclusion is not only a policy file. It is not a frontier LLM. This repository trains a GPT-2-style causal LM from scratch (a few million parameters) on Open Reason JSONL, on **CPU** — Docker image `open-reason-train:cpu` when Docker is available, otherwise host CPU. Checkpoints write to `training/work/open-reason-local/`. The dataset is [`theworker02/open-reason`](https://huggingface.co/datasets/theworker02/open-reason). If a Hub upload succeeds, the companion id is [`theworker02/open-reason-small`](https://huggingface.co/theworker02/open-reason-small). We do **not** claim a 1B-parameter model (`theworker02/open-reason-1b`) until a CUDA 1B job has actually been trained, evaluated, and uploaded. If people find the small model useful, development will continue.

## Provenance: Reddit posts cannot support the claims

Reddit items are not a stable, attributable research record in the sense Open Reason requires.

- **Identity.** Authors are typically pseudonymous. A username is not a reviewed publisher, an institution, or a pinned git identity. Open Reason cannot honestly fill `provenance` with a person or organization it cannot identify.
- **Stability.** Posts and comments are edited, deleted, removed by moderators, or pulled when accounts disappear. A snapshot is not a version-pinned document.
- **Authority.** A subreddit is a community venue, not an official specification, a reviewed textbook, or a commit-pinned repository. Trust-tier 0–7 in `sources/registry.yaml` has no slot that turns forum consensus into an oracle.
- **Traceability.** Fabricating URLs, thread ids, or “source: Reddit” as if that were a complete citation is a pipeline bug. Omitting the origin is also a bug. The only honest action is rejection.

Unknown origin is allowed only with `unknown_reason`, is forbidden for tier S, and is not a path to launder Reddit text as “unspecified web.”

## License: there is no clean redistributable grant

Open Reason ships pipeline and original dataset rows under **Apache-2.0** (`LICENSE`). That is the only project license. Per-row `provenance.license_spdx` must still be a real grant, not a guess.

User content on Reddit is posted under the platform’s terms. That arrangement is **not** a clean downstream license to Open Reason, and it is **not** a grant to relicense the text as Apache-2.0. We do not treat “it was publicly readable” as “it is redistributable in this corpus.”

The following remain Reddit-derived and are forbidden, even when they arrive with a different filename or host:

| Channel | Why it is still excluded |
| --- | --- |
| Official or unofficial API pulls | Access terms are not a dataset license for this project |
| Subreddit dumps and comment archives | Same user content, different packaging |
| Pushshift and successor archives | Archive ≠ permission; provenance is still Reddit |
| Third-party “Reddit datasets” on Hugging Face or elsewhere | Secondary distribution does not create a new grant |
| Sites whose primary purpose is republishing Reddit | Mirrors do not change the source |
| Search results that reproduce Reddit threads | The snippet is still Reddit text |

There is **no secondary-dataset workaround**. Share-alike, non-commercial, unknown, or platform-encumbered text is never silently converted to Apache-2.0. Copyleft identifiers require an explicit source-policy exception and still would not admit Reddit.

This document is research-infrastructure policy, not legal advice to third parties. The operational rule for this repository is simpler: Reddit-derived material does not enter the tree or the release.

## Quality: votes are not verification

`quality.verified` is set only after a check this repository can re-run: coding sandbox (unittest / SQLite / Node), sympy or exact integer arithmetic, independent numeric science checks, or a named constraint checker. If a check was not run, the flag stays false. There is no “probably correct” bit.

Karma, awards, upvote ratios, and “best comment” rankings measure **engagement**, not correctness. They cannot support the claims Open Reason makes about verified rows.

`evidence.community_evidence` may, for **other** reviewed community sources, inform a **capped** component of `evidence_confidence`. That score is not a claim of truth. **`community_evidence` must never set `quality.verified`.** Reddit is not admitted as community evidence at all. A record that looks Reddit-derived is dropped before scoring.

High-risk domains (medicine, law, finance, safety-critical engineering) cannot enter tier S without authoritative evidence **and** independent verification. Forum chatter that merely *sounds* like those domains is exactly the register described above. It is not a shortcut into the `verified` configuration.

## Contamination and evaluation leakage

Reddit is heavily represented in web crawls and in instruction-tuning mixes. Contest problems, exam questions, benchmark snippets, and homework statements have been posted there for years. Ingesting Reddit would be an uncontrolled mixing channel between “training text” and “evaluation items.”

Open Reason already fingerprints known eval sets in `configs/denylist.yaml` (prompt prefixes and distinctive needles — not answers). Hits are **reported**, not silently deleted; `--strict` fails the build. Hold out `benchmarks/` from training. A Reddit dump would bypass that discipline: the same item can appear as a casual comment with no benchmark name attached.

Using Reddit would also contaminate **style**. Models trained on that register learn to imitate it. Open Reason’s generators and human-authored items are labeled as such; they are not a paraphrase farm for forum threads.

## Indirect use is forbidden

The exclusion is on **provenance**, not on a single hostname. All of the following are rejected:

- Hosts and short links in the prohibited matchers, including `reddit.com`, `www.reddit.com`, `old.reddit.com`, `np.reddit.com`, and `redd.it`, plus related media hosts used in URL checks
- Pushshift (`pushshift`) and similarly derived archives
- Subreddit dumps, comment dumps, and API exports
- Hugging Face or other third-party datasets whose provenance includes Reddit (including names the inspector already fingerprints, such as common Reddit TL;DR / TIFU / Pushshift dumps and substantially Reddit-derived webtext corpora)
- Websites whose primary purpose is republishing Reddit
- Search-engine results, caches, or “reader” views that reproduce Reddit
- Paraphrases, “inspired by a thread,” or synthetic rewrites whose `derived_from` / `source` still points at Reddit
- Discovery candidates whose id or URL matches Reddit

`open_reason.provenance.reddit.inspect_record` is conservative on purpose. It flags obvious Reddit provenance so examples can be **rejected**, not so Reddit can be laundered through a secondary dataset. If a corpus is materially Reddit-derived, do not import it.

## What Open Reason uses instead

| Kind | Role in this project |
| --- | --- |
| Official documentation | Version-pinned, license-reviewed docs (language references, man pages, standards) inspire **original** tasks. Auto-approve is a license policy, not a scrape. `verbatim` stays false without a reviewed crawler. |
| Permissive GitHub | Original tasks inspired by commit-pinned MIT/BSD/Apache-2.0 public snapshots (`url`, SPDX, commit; `verbatim=false`). Not a scrape of the internet, and not Reddit-derived. |
| Stack Overflow / Stack Exchange | **User-approved seed only**: original rewrites and short attributed snippets, not copies of threads, and **not Reddit mirrors**. CC BY-SA on any quoted snippet must be preserved; votes never verify. |
| Original verified tasks | Human-authored Open Reason items and deterministic synthetic generators (Apache-2.0 project license), always labeled `provenance.source_type`. `quality.verified` only after sandbox, sympy, numeric, or named checkers. |
| Curriculum auto-approve | Public course and OER catalogs may inspire original tasks (`curriculum_use: true`). Lectures are not copied. NC/SA/unknown licenses never become Apache-2.0 verbatim rows. |

Quora is not a primary source of truth. Educational sites such as Khan Academy, MIT OCW, CS50, OpenStax, and MDN are registered for original curriculum tasks and are **not scraped**.

Reddit cannot be approved, auto-approved, discovered, or ingested. `reddit_allowed` is required to be false on every registry row.

## Enforcement

The ban is implemented, not merely documented.

| Mechanism | What it does |
| --- | --- |
| `sources/registry.yaml` | `reddit` is `prohibited`, `enabled: false`. Policy requires `reddit: prohibited`. |
| `configs/source_policy.yaml` | `reddit: prohibited`; rule `forbidden` AUTO_REJECTS `reddit`. |
| `sources/prohibited/catalog.yaml` and `matchers.yaml` | Catalog row plus host / substring / dataset-name matchers. |
| `open_reason.provenance.reddit.inspect_record` | Rejects Reddit URLs, source strings, known dataset names, and obvious Reddit-derived text in record fields. |
| Pipeline (`open_reason.pipeline`) | Increments `reddit_rejected` and drops the row. |
| `scripts/check_no_reddit.py` | CI grep: `reddit.com`, `redd.it`, and `pushshift` must not appear outside documented policy and matcher files. |
| GitHub Actions `CI` | Job step “Reddit grep” runs that script on `main` and pull requests. |
| Discovery / auto-approve / CLI | Reddit cannot be a discovery candidate. `open-reason ingest --source reddit` is rejected. Auto-approve never enables it. |

Contributors: see [CONTRIBUTING.md](../CONTRIBUTING.md). Do not add Reddit samples to tests beyond the existing rejection fixtures (URL and source strings used to prove the inspector fails closed).

## What this policy does not do

- It does not admit “old” dumps, research fair-use arguments, or anonymized comments as exceptions.
- It does not distinguish posts from comments, NSFW from SFW, or one subreddit from another.
- It does not treat Common Crawl slices, OpenWebText-style corpora, or search snippets as clean if their provenance includes Reddit.
- It does not set `quality.verified` from community scores anywhere in the pipeline.

The exclusion is not weakened by this case study. If a future contributor wants Reddit in the corpus, the answer is no.

## How to cite

Cite the repository (`CITATION.cff`) and this document:

- Source tree: [`docs/why-not-reddit.md`](https://github.com/theworker02/open-reason/blob/main/docs/why-not-reddit.md)
- Project site: [https://theworker02.github.io/open-reason/why-not-reddit.html](https://theworker02.github.io/open-reason/why-not-reddit.html)
- Dataset: [https://huggingface.co/datasets/theworker02/open-reason](https://huggingface.co/datasets/theworker02/open-reason)
- Small companion model (if uploaded): [https://huggingface.co/theworker02/open-reason-small](https://huggingface.co/theworker02/open-reason-small)
