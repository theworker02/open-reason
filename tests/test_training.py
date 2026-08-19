import yaml

from open_reason.config import repo_root
from open_reason.training import prepare_sft_rows


def test_prepare_sft_rows_skips_empty() -> None:
    rows = prepare_sft_rows(
        [
            {"id": "or-a", "prompt": "What is 2+2?", "answer": "4", "quality": {"verified": True}},
            {"id": "or-b", "prompt": "", "answer": "x"},
            {"id": "or-c", "prompt": "hello there", "solution": "world"},
        ]
    )
    assert [r["id"] for r in rows] == ["or-a", "or-c"]
    assert rows[0]["completion"] == "4"
    assert rows[1]["completion"] == "world"


def test_local_training_config_is_cpu_small() -> None:
    path = repo_root() / "training" / "configs" / "open-reason-local.yaml"
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert spec["hub_model_id"] == "theworker02/open-reason-small"
    assert spec["device"] == "cpu"
    assert "1b" not in str(spec["model_name"]).lower() or spec["model_name"] != "open-reason-1b"
    assert spec["model_name"] == "open-reason-small"
    assert spec.get("n_layer", 0) <= 8


def test_medium_training_config_is_cpu_larger() -> None:
    path = repo_root() / "training" / "configs" / "open-reason-medium.yaml"
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert spec["hub_model_id"] == "theworker02/open-reason-medium"
    assert spec["device"] == "cpu"
    assert spec["model_name"] == "open-reason-medium"
    assert "1b" not in spec["model_name"].lower()
    assert int(spec["n_embd"]) >= 256
    assert int(spec["n_layer"]) >= 6
    assert spec.get("n_layer", 0) <= 12


def test_large_training_config_is_cpu_larger_than_medium() -> None:
    path = repo_root() / "training" / "configs" / "open-reason-large.yaml"
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    medium = yaml.safe_load(
        (repo_root() / "training" / "configs" / "open-reason-medium.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert spec["hub_model_id"] == "theworker02/open-reason-large"
    assert spec["device"] == "cpu"
    assert spec["model_name"] == "open-reason-large"
    assert "1b" not in spec["model_name"].lower()
    assert int(spec["n_embd"]) >= 512
    assert int(spec["n_layer"]) >= 8
    assert int(spec["n_layer"]) <= 12
    assert int(spec["n_embd"]) * int(spec["n_layer"]) > int(medium["n_embd"]) * int(
        medium["n_layer"]
    )


def test_xl_training_config_is_about_450m() -> None:
    path = repo_root() / "training" / "configs" / "open-reason-xl.yaml"
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    large = yaml.safe_load(
        (repo_root() / "training" / "configs" / "open-reason-large.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert spec["hub_model_id"] == "theworker02/open-reason-xl"
    assert spec["device"] == "cpu"
    assert spec["model_name"] == "open-reason-xl"
    assert "1b" not in spec["model_name"].lower()
    assert int(spec["n_embd"]) >= 1024
    assert int(spec["n_layer"]) >= 16
    assert int(spec["vocab_size"]) == 8192
    assert int(spec["max_seq_len"]) == 256
    assert int(spec["batch_size"]) == 1
    assert spec.get("gradient_checkpointing") is True
    assert int(spec["n_embd"]) * int(spec["n_layer"]) > int(large["n_embd"]) * int(
        large["n_layer"]
    )


def test_dockerfile_is_cpu_only() -> None:
    text = (repo_root() / "training" / "Dockerfile").read_text(encoding="utf-8")
    assert "python:3.12-slim" in text
    assert "OPEN_REASON_DISABLE_CUDA=1" in text
    assert "nvidia" not in text.lower()
    assert "rocm" not in text.lower()
