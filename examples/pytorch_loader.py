"""Turn prompts/answers into tensors once a tokenizer is available."""

import json

from datasets import load_dataset


def encode(tokenizer, row):
    quality = json.loads(row["quality"])
    if not quality.get("verified"):
        return None
    return tokenizer(row["prompt"], text_target=row["answer"] or row["solution"] or "")


def main() -> None:
    ds = load_dataset("theworker02/open-reason", "mathematics", split="train")
    print("rows", len(ds), "— pass these through your tokenizer, then torch.utils.data.DataLoader")


if __name__ == "__main__":
    main()
