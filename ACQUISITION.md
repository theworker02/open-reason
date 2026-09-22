# Acquisition Brief â€” or: theworker02/open-reason-large / theworker02/open-reason-medium / theworker02/open-reason-small

**Date:** 2026-09-22  
**Repository:** https://github.com/theworker02/open-reason  
**Default branch:** `main`  
**Primary language:** Python  
**Status:** Diligence briefing only. **No acquisition has occurred** by virtue of this file.  
**License:** Proprietary â€” sale, written commercial license, or completed asset transfer required (see root `LICENSE`).  
**Valuation:** Not stated.  
**Contact:** GitHub [@theworker02](https://github.com/theworker02) Â· [thanks.dev/u/gh/theworker02](https://thanks.dev/u/gh/theworker02)

> Cloning or forking this repository does **not** grant production, redistribution, SaaS, OEM, or commercial rights.

---

## 1. Executive thesis

<img src="assets/logo.svg" alt="Open Reason" width="120" height="120"> <strong>An open, verified dataset for coding, science, mathematics, and human reasoning.</strong><br> Provenance-aware. License-gated. Independently checked. Reproducible.

**Why a buyer cares:** or: theworker02/open-reason-large / theworker02/open-reason-medium / theworker02/open-reason-small packages transferable product IP â€” source, docs, in-repo brand assets, and a diligence room under `docs/acquisition/` â€” under a clear proprietary posture so diligence can proceed without mistaking the repo for open source.

---

## 2. Product snapshot

| Item | Detail |
|------|--------|
| Product | or: theworker02/open-reason-large / theworker02/open-reason-medium / theworker02/open-reason-small |
| Repo | `theworker02/open-reason` |
| Language | Python |
| Open source? | **No** â€” proprietary |
| Rightsholder | theworker02 |
| Diligence pack | `docs/acquisition/` |

### Capability highlights (from current materials)

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

---

## 3. Problem / opportunity

Teams evaluating or: theworker02/open-reason-large / theworker02/open-reason-medium / theworker02/open-reason-small typically need either (a) a commercial right to run or embed it, or (b) outright ownership of the Product IP for strategic build-out. Public GitHub visibility without a proprietary license creates false assumptions about free production use. This brief and the linked data room make the commercial path explicit.

---

## 4. What ships today

Honest maturity: treat repository contents, README claims, tests, and release tags as the source of truth. Do not assume production customers, ARR, filed patents, or SLAs unless separately evidenced in diligence.

Typical transferable surfaces:

- Source tree and build/test scripts present in-repo
- Documentation and design notes
- Acquisition / diligence markdown under `docs/acquisition/`
- Branding assets committed to the repository (if any)

---

## 5. Demo / evaluation path (buyer)

Minimal path (no secrets required unless README says otherwise):

```
```python
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

ds = load_dataset("theworker02/open-reason", "all")
tok = AutoTokenizer.from_pretrained("theworker02/open-reason-xl")
model = AutoModelForCausalLM.from_pretrained("theworker02/open-reason-xl")
# or: theworker02/open-reason-large / theworker02/open-reason-medium / theworker02/open-reason-small
```
```bash
git clone https://github.com/theworker02/open-reason.git
cd open-reason
pip install -e ".[dev]"
open-reason sources --approve --apply
open-reason build --config all --seed 42 --out data/release
```
```python
from datasets import load_dataset

coding = load_dataset("theworker02/open-reason", "coding")
math = load_dataset("theworker02/open-reason", "mathematics")
education = load_dataset("theworker02/open-reason", "education")
core = load_dataset("theworker02/open-reason", "core")
```
```bash
open-reason sources --approve          # dry run
open-reason sources --approve --apply  # write sources/registry.yaml
```
```bash
open-reason generate --domain education
open-reason ingest --source khan-academy   # original tasks, not copied lessons
open-reason ingest --source reddit         # rejected
```
```python
from datasets import load_dataset
ds = load_dataset("theworker02/open-reason", "coding", split="train", streaming=True)
for row in ds.take(3):
    print(row["id"], row["task_type"])
```
```text
```

Extended evaluation: `docs/acquisition/BUYER_EVALUATION.md`. Written NDA / evaluation grants may be required for private materials.

---

## 6. What a transaction typically includes

Subject to definitive schedules:

| Included (typical) | Excluded (typical) |
|--------------------|--------------------|
| Repo materials + asserted original IP | Seller personal accounts / unrelated repos |
| Docs + diligence room at closing | Third-party dependency source under separate licenses |
| In-repo brand marks as assigned | Secrets without rotation plan |
| Know-how captured in docs | Fabricated revenue, user, or adoption metrics |

---

## 7. Suggested deal structures

| Structure | When it fits |
|-----------|--------------|
| Non-exclusive commercial license | Deploy/run under seat or environment terms |
| Exclusive field-of-use license | Buyer wants exclusivity; seller may retain entity |
| Asset / IP assignment | Buyer wants ownership of Materials outright |
| OEM / redistribution | Separate agreement â€” not implied here |

Commercial terms (price, earnouts, escrow) are negotiated under NDA with counsel.

---

## 8. Buyer diligence checklist

- [ ] Confirm Rightsholder identity and authority to sell/license
- [ ] Inventory Materials (`docs/acquisition/ASSET_INVENTORY.md`)
- [ ] Review IP posture (`IP_PROVENANCE.md`) and dependencies (`DEPENDENCY_INVENTORY.md`)
- [ ] Run evaluation script (`BUYER_EVALUATION.md`)
- [ ] Review risks (`RISK_REGISTER.md`)
- [ ] Agree transfer scope (`TRANSFER_MANIFEST.md`) and handoff (`HANDOFF_CHECKLIST.md`)
- [ ] Supersede root `LICENSE` at closing via definitive agreement

---

## 9. Related documents

| Document | Purpose |
|----------|---------|
| `LICENSE` | Proprietary â€” no default grant |
| `docs/acquisition/README.md` | Data-room index |
| `docs/acquisition/EXECUTIVE_SUMMARY.md` | One-page thesis |
| `README.md` | Product overview |
| `SECURITY.md` | Vulnerability reporting |
| `COMMERCIAL.md` | Licensing contact path |
| `.github/FUNDING.yml` | Sponsors / thanks.dev |

---

## 10. Disclaimer

This package is informational and **does not** create a binding offer, grant of rights, or investment advice. Engage counsel for any transaction.

---

*Document version: 2.0.0 / 2026-09-22 Â· Classification: acquisition briefing*
