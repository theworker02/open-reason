# Data sources

Open Reason does not scrape indiscriminately. Every connector declares source, license, terms, collection method, allowed usage, retention, and attribution. The machine-readable registry is `sources/registry.yaml`. **Discovery is not ingestion.**

`open-reason sources --approve --apply` runs a license-policy auto-approve. It enables **original Open Reason tasks** (`curriculum_use: true`, `verbatim: false`). It does not download third-party websites and it does not copy lesson text.

**Open Reason does not use Reddit as a data source.** See [why Open Reason does not use Reddit](why-not-reddit.md).

Quora is not a primary source of truth. Popularity is not verification.

## Active

| Source | Type | License | Notes |
| --- | --- | --- | --- |
| Open Reason authors | `human_authored` | Apache-2.0 | Teaching, synthesis, and explanation items written for this project |
| Open Reason generators | `synthetic` | Apache-2.0 | Deterministic factories; always labeled `provenance.source_type=synthetic` |
| Auto-approved curriculum sources | original tasks | Apache-2.0 rows | Inspired by public structure; not copied; see `open-reason sources --approve` |
| GitHub (permissive) | `open_source` | per-repo MIT/BSD/Apache-2.0 | Original tasks with url, license, commit; `verbatim=false` |
| Stack Overflow | community seeds | Apache-2.0 on original rewrites | Inspired-by tasks; not verbatim dumps; not Reddit mirrors |

Synthetic examples are **not** represented as human-authored.

## Curriculum auto-approve (original tasks, not copies)

Educational and documentation sources can be conditionally approved for original task generation. MIT OCW NC-SA and MDN share-alike block verbatim copying. Stack Overflow is user-approved for **original rewritten seeds** (not HTML scrapes, not Reddit mirrors). Reddit cannot be approved.

`open-reason ingest --source khan-academy` after auto-approve emits original Open Reason items, not Khan lesson text.

## Forbidden

**Open Reason does not use Reddit as a data source.** Case study: [why-not-reddit.md](why-not-reddit.md).

Rejected: Reddit posts and comments, subreddit dumps, Reddit APIs, archives, Pushshift, Reddit-derived datasets, websites whose primary purpose is republishing Reddit, and third-party corpora whose provenance includes Reddit. There is no secondary-dataset workaround.

Quora is prohibited as an authority. If it is ever reconsidered, it needs the same licensing and provenance review as every other source.

## Source of truth model

Open Reason does not treat a website, vote count, or accepted answer as automatically correct.

```text
source authority
+ community validation
+ independent corroboration
+ execution / experimentation
+ cross-source agreement
+ recency
+ expert review
= evidence_confidence
```

That score is **not** a claim of philosophical truth. `quality.verified` is only set after a check actually ran.

Trusted-source tiers are documented in `sources/registry.yaml` (`trust_tiers` 0–7). Open Reason must not become dependent on any single site.

## Licensing of mixed releases

- Pipeline software and original dataset content: Apache-2.0 (`LICENSE`)
- Any source-derived row keeps its original `license_spdx`. Open Reason does not relicense copyleft or share-alike material as Apache-2.0.

See `open-reason sources` and `open-reason sources --matrix`.
