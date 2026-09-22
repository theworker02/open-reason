# Buyer evaluation â€” or: theworker02/open-reason-large / theworker02/open-reason-medium / theworker02/open-reason-small

## Goal

In 15â€“45 minutes, verify the Product builds or runs as documented and that proprietary notices are present.

## Steps

1. Confirm root `LICENSE` is proprietary and `ACQUISITION.md` exists.
2. Skim `README.md` install/run claims.
3. Execute:

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

4. Run tests if present (`npm test`, `pytest`, `cargo test`, `go test ./...`, etc.).
5. Record README vs observed behavior gaps in workpapers.

## Pass criteria

- [ ] Clone succeeds
- [ ] Documented happy path works **or** failure is explained
- [ ] Minimal path needs no surprise secrets
- [ ] License notices intact

*Updated: 2026-09-22*
