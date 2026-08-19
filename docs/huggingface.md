# Publishing to Hugging Face

GitHub is the **engineering source of truth**. Hugging Face is **distribution**
for research artifacts (Parquet shards and the dataset card). Do not turn the
GitHub git tree into a Parquet dump, and do not sync the whole repository to
the Hub.

| Role | Repository |
| --- | --- |
| Pipeline, schemas, registry, tests, docs, samples, release manifests | GitHub [`theworker02/open-reason`](https://github.com/theworker02/open-reason) (branch `main`) |
| Dataset card + published shards | Hugging Face dataset [`theworker02/open-reason`](https://huggingface.co/datasets/theworker02/open-reason) |
| Small CPU model (not 1B) | Hugging Face model [`theworker02/open-reason-small`](https://huggingface.co/theworker02/open-reason-small) |
| Medium CPU model (13,867,008, not 1B) | Hugging Face model [`theworker02/open-reason-medium`](https://huggingface.co/theworker02/open-reason-medium) |
| Large CPU model (91,544,064, not 1B) | Hugging Face model [`theworker02/open-reason-large`](https://huggingface.co/theworker02/open-reason-large) |

## What is synced

Only `distribution/dataset/` is mirrored to the Hub. That directory holds:

- `README.md` — copy of [`DATA_CARD.md`](../DATA_CARD.md)
- `sample/preview.jsonl` — a few illustrative rows
- `data/release/README.md` — pointer to where shards will live on the Hub
- `.gitattributes` — Parquet LFS hint for later shard uploads

Generated `data/release/*.parquet` and `*.jsonl` stay **local** (gitignored).
Maintainers attach those files to a GitHub Release and upload them to the Hub
`data/release/` path when ready. CI does not rebuild the full coding sandbox
dataset.

## Trusted publisher form (Hugging Face UI)

Official Hub docs call these **claims** (exact match, no regex):
[Trusted Publishers](https://huggingface.co/docs/hub/trusted-publishers).

On the dataset repo: **Settings → Trusted Publishers**. Provider: **GitHub Actions**.

| Claim (docs name) | Value to type | Notes |
| --- | --- | --- |
| `repository` | `theworker02/open-reason` | GitHub owner/name as one string |
| `workflow` | `sync-huggingface.yml` | **Filename** of `.github/workflows/sync-huggingface.yml`, not the YAML `name:` |
| `branch` | *(leave blank)* | Workflow runs on `release: published` and `workflow_dispatch`, not a pinned branch |

If the form splits owner and repository:

- GitHub org/user: `theworker02`
- Repository name: `open-reason`

YAML display name (GitHub Actions tab only; **not** the Hub `workflow` claim):

```text
Sync Open Reason to Hugging Face
```

Official docs do not list an **environment** claim. This workflow has no
`environment:` key. If the UI shows Environment, leave it blank.

Do not type `ci.yml`. Do not type the display name into `workflow`.

## GitHub Action

[`.github/workflows/sync-huggingface.yml`](../.github/workflows/sync-huggingface.yml)
runs on **release published** and `workflow_dispatch` only — never on every
push to `main`. It uses [`huggingface/hub-sync@v0.1.0`](https://huggingface.co/docs/hub/repositories-github-actions):

- `huggingface_repo_id`: `theworker02/open-reason`
- `repo_type`: `dataset`
- `subdirectory`: `distribution/dataset`
- `hf_token`: `${{ secrets.HF_TOKEN }}`

Add a GitHub Actions secret named `HF_TOKEN` (fine-grained Hub write token)
before the first real publish. Creating the trusted publisher does **not**
upload anything by itself.

Until you are ready to publish: do not run this workflow, do not
`huggingface-cli upload`, and do not tag a release solely to trigger Hub sync.

v1.0.1 parquet and the dataset card were published from a logged-in `hf` CLI
session to https://huggingface.co/datasets/theworker02/open-reason . GitHub
remains the engineering source of truth.

## Load

```python
from datasets import load_dataset
ds = load_dataset("theworker02/open-reason", "coding")
education = load_dataset("theworker02/open-reason", "education")
core = load_dataset("theworker02/open-reason", "core")
```

Nested Parquet fields are JSON strings. Parse `quality`, `provenance`,
`verification`, `context`, and list fields with `json.loads`.
