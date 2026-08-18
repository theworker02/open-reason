"""Filter verified coding rows and show how they plug into a training loop.

This example does not download weights; it only shows the dataset contract.
"""

import json

from datasets import load_dataset

ds = load_dataset("theworker02/open-reason", "coding", split="train")
verified = [row for row in ds if json.loads(row["quality"])["verified"]]
print(f"{len(verified)} verified coding examples")
print(verified[0]["prompt"][:200])
