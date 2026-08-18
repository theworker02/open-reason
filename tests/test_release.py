from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from open_reason.constants import CURRENT_CONFIGS, PIPELINE_VERSION
from open_reason.export.huggingface import (
    SNAPSHOT_START,
    replace_marked_section,
    snapshot_table,
    sync_distribution_card,
    write_release_catalog,
)
from open_reason.pipeline import assert_release_complete


def _reports() -> dict:
    reports = {}
    for name in CURRENT_CONFIGS:
        reports[name] = {
            "kept": 3 if name == "all" else 1,
            "statistics": {
                "config": name,
                "total_examples": 3 if name == "all" else 1,
                "verified_examples": 1,
                "human_authored_examples": 0,
                "synthetic_examples": 1,
                "source_derived_examples": 0,
            },
        }
    return reports


def test_catalog_writes_complete_manifest(tmp_path: Path) -> None:
    reports = _reports()
    write_release_catalog(tmp_path, reports)
    for name in CURRENT_CONFIGS:
        (tmp_path / f"{name}.jsonl").write_text("{}\n", encoding="utf-8")
        (tmp_path / f"{name}.parquet").write_bytes(b"PAR1")
    assert_release_complete(tmp_path)
    payload = yaml.safe_load((tmp_path / "manifest.yaml").read_text(encoding="utf-8"))
    assert payload["pipeline_version"] == PIPELINE_VERSION
    assert payload["complete"] is True
    assert payload["configs"] == list(CURRENT_CONFIGS)
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert f"v{PIPELINE_VERSION}" in readme
    assert "`core.*`" in readme
    assert "education" in snapshot_table(reports)


def test_assert_release_complete_rejects_stale_version(tmp_path: Path) -> None:
    reports = _reports()
    write_release_catalog(tmp_path, reports)
    for name in CURRENT_CONFIGS:
        (tmp_path / f"{name}.jsonl").write_text("{}\n", encoding="utf-8")
        (tmp_path / f"{name}.parquet").write_bytes(b"PAR1")
    manifest = yaml.safe_load((tmp_path / "manifest.yaml").read_text(encoding="utf-8"))
    manifest["pipeline_version"] = "0.1.0"
    (tmp_path / "manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    with pytest.raises(RuntimeError, match="pipeline_version"):
        assert_release_complete(tmp_path)


def test_assert_release_complete_rejects_missing_core(tmp_path: Path) -> None:
    reports = _reports()
    write_release_catalog(tmp_path, reports)
    for name in CURRENT_CONFIGS:
        (tmp_path / f"{name}.jsonl").write_text("{}\n", encoding="utf-8")
        (tmp_path / f"{name}.parquet").write_bytes(b"PAR1")
    (tmp_path / "core.jsonl").unlink()
    with pytest.raises(RuntimeError, match="core.jsonl"):
        assert_release_complete(tmp_path)


def test_repo_docs_have_snapshot_markers() -> None:
    from open_reason.config import repo_root

    root = repo_root()
    for name in ("README.md", "DATA_CARD.md"):
        text = (root / name).read_text(encoding="utf-8")
        assert SNAPSHOT_START in text
        assert "<!-- END_RELEASE_SNAPSHOT -->" in text


def test_replace_marked_section() -> None:
    text = "before\n<!-- BEGIN_RELEASE_SNAPSHOT -->\nold\n<!-- END_RELEASE_SNAPSHOT -->\nafter\n"
    updated = replace_marked_section(text, "new table")
    assert "new table" in updated
    assert "old" not in updated
    assert SNAPSHOT_START in updated


def test_gitignore_excludes_release_shards() -> None:
    from open_reason.config import repo_root

    text = (repo_root() / ".gitignore").read_text(encoding="utf-8")
    assert "data/release/*.parquet" in text
    assert "data/release/*.jsonl" in text


def test_hf_sync_workflow_identity_is_pinned() -> None:
    from open_reason.config import repo_root

    path = repo_root() / ".github" / "workflows" / "sync-huggingface.yml"
    text = path.read_text(encoding="utf-8")
    trigger, _, _ = text.partition("jobs:")
    assert path.name == "sync-huggingface.yml"
    assert "name: Sync Open Reason to Hugging Face" in text
    assert "types: [published]" in trigger
    assert "workflow_dispatch:" in trigger
    assert "push:" not in trigger
    assert "subdirectory: distribution/dataset" in text
    assert "repo_type: dataset" in text
    assert "huggingface_repo_id: theworker02/open-reason" in text
    assert "huggingface/hub-sync@v0.1.0" in text
    assert "environment:" not in text


def test_sync_distribution_card_copies_data_card(tmp_path: Path) -> None:
    (tmp_path / "DATA_CARD.md").write_text("# card\n", encoding="utf-8")
    sync_distribution_card(tmp_path)
    copied = (tmp_path / "distribution" / "dataset" / "README.md").read_text(encoding="utf-8")
    assert copied == "# card\n"
