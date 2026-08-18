"""Keep only verified (tier S) rows."""

import json

from datasets import load_dataset

ds = load_dataset("theworker02/open-reason", "all", split="train")
verified = ds.filter(lambda row: json.loads(row["quality"])["verified"] is True)
print(len(verified), "verified rows")
