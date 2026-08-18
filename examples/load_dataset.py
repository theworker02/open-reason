"""Load and filter Open Reason locally."""

from datasets import load_dataset

ds = load_dataset("theworker02/open-reason", "coding", split="train")
print(ds)
print(ds[0]["id"], ds[0]["task_type"])
