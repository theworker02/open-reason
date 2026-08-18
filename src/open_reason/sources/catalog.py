"""Export machine-readable source catalogs from the live registry.

These files live under sources/approved, sources/restricted, and
sources/prohibited so those directories are not README-only stubs.
They never contain scraped third-party lesson text.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from open_reason.config import repo_root
from open_reason.constants import PIPELINE_VERSION
from open_reason.policy import evaluate_policy
from open_reason.sources import Registry, SourceRecord, load_registry

NEVER_FETCH_HOSTS = (
    "khanacademy.org",
    "www.khanacademy.org",
    "ocw.mit.edu",
    "cs50.harvard.edu",
    "openstax.org",
    "developer.mozilla.org",
    "stackoverflow.com",
    "stackexchange.com",
    "reddit.com",
    "www.reddit.com",
    "old.reddit.com",
    "redd.it",
    "www.quora.com",
    "quora.com",
)

PROHIBITED_MATCHERS = {
    "reddit": {
        "hosts": ["reddit.com", "www.reddit.com", "old.reddit.com", "np.reddit.com", "redd.it"],
        "url_substrings": ["/r/", "reddit.com", "redd.it"],
        "dataset_name_substrings": ["reddit", "pushshift", "subreddit"],
        "policy": "Open Reason does not use Reddit as a data source.",
    },
    "quora": {
        "hosts": ["quora.com", "www.quora.com"],
        "url_substrings": ["quora.com"],
        "dataset_name_substrings": ["quora"],
        "policy": "Quora is not a primary source of truth.",
    },
}


def _public_fields(source: SourceRecord, verdict) -> dict[str, Any]:
    return {
        "id": source.id,
        "name": source.name,
        "category": source.category,
        "license": source.license,
        "license_spdx": source.license_spdx,
        "status": verdict.status,
        "enabled": verdict.enabled,
        "curriculum_use": verdict.curriculum_use,
        "verbatim": False,
        "decision": verdict.decision,
        "rule_id": verdict.rule_id,
        "reason": verdict.reason,
        "auto_approval_mode": source.auto_approval_mode,
    }


def partition_sources(registry: Registry | None = None) -> dict[str, list[dict[str, Any]]]:
    registry = registry or load_registry()
    buckets: dict[str, list[dict[str, Any]]] = {
        "approved": [],
        "restricted": [],
        "prohibited": [],
        "metadata_only": [],
    }
    for source in registry.sources:
        verdict = evaluate_policy(source)
        row = _public_fields(source, verdict)
        if verdict.decision == "AUTO_REJECTED" or source.status == "prohibited":
            buckets["prohibited"].append(row)
        elif verdict.decision == "METADATA_ONLY" or source.status == "metadata_only":
            buckets["metadata_only"].append(row)
            buckets["restricted"].append(row)
        elif verdict.enabled and verdict.decision == "AUTO_APPROVED":
            buckets["approved"].append(row)
        else:
            buckets["restricted"].append(row)
    return buckets


def original_task_samples(*, root: Path | None = None) -> list[dict[str, Any]]:
    """Metadata-only samples of original curriculum tasks (not source copies)."""
    from open_reason.generation.curriculum import TASKS

    rows: list[dict[str, Any]] = []
    for source_id, tasks in TASKS.items():
        for index, task in enumerate(tasks[:2]):
            rows.append(
                {
                    "source_id": source_id,
                    "index": index,
                    "task_type": task.get("task_type"),
                    "concept_id": task.get("concept_id"),
                    "language": task.get("language"),
                    "verbatim": False,
                    "curriculum_use": True,
                    "inspired_by": source_id,
                    "copied_from_source": False,
                    "pipeline_version": PIPELINE_VERSION,
                    "prompt_sha_prefix": _prompt_prefix(task.get("prompt") or ""),
                }
            )
    return rows


def _prompt_prefix(prompt: str) -> str:
    import hashlib

    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return digest[:12]


def _dump_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def write_source_catalogs(*, root: Path | None = None) -> dict[str, Path]:
    root = root or repo_root()
    buckets = partition_sources()
    written: dict[str, Path] = {}

    approved_path = root / "sources" / "approved" / "catalog.yaml"
    _dump_yaml(
        approved_path,
        {
            "pipeline_version": PIPELINE_VERSION,
            "note": (
                "Auto-approved for original Open Reason tasks only. "
                "verbatim is always false. No third-party lesson text is stored here."
            ),
            "sources": buckets["approved"],
        },
    )
    written["approved_catalog"] = approved_path

    sample_path = root / "sources" / "approved" / "original_tasks.sample.jsonl"
    samples = original_task_samples(root=root)
    sample_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in samples),
        encoding="utf-8",
    )
    written["approved_samples"] = sample_path

    licenses_path = root / "sources" / "approved" / "license_report.yaml"
    _dump_yaml(
        licenses_path,
        {
            "pipeline_version": PIPELINE_VERSION,
            "rows": [
                {
                    "id": row["id"],
                    "license_spdx": row.get("license_spdx"),
                    "verbatim": False,
                    "relicensed_to_cc_by_4_0": False,
                }
                for row in buckets["approved"]
            ],
        },
    )
    written["approved_licenses"] = licenses_path

    restricted_path = root / "sources" / "restricted" / "catalog.yaml"
    _dump_yaml(
        restricted_path,
        {
            "pipeline_version": PIPELINE_VERSION,
            "note": (
                "Review-required or metadata-only. Do not fetch or copy these sites. "
                "Original tasks may exist only after AUTO_APPROVED curriculum_use."
            ),
            "sources": buckets["restricted"],
        },
    )
    written["restricted_catalog"] = restricted_path

    denylist_path = root / "sources" / "restricted" / "fetch_denylist.yaml"
    _dump_yaml(
        denylist_path,
        {
            "pipeline_version": PIPELINE_VERSION,
            "never_fetch_hosts": list(NEVER_FETCH_HOSTS),
            "never_scrape_source_ids": [
                "khan_academy_computing",
                "mit_opencourseware",
                "harvard_cs50",
                "openstax",
                "mdn",
                "stackoverflow",
                "stack_exchange",
                "the_odin_project",
            ],
            "reason": "Public pages are not a redistribution grant. Open Reason generates original tasks.",
        },
    )
    written["restricted_denylist"] = denylist_path

    prohibited_path = root / "sources" / "prohibited" / "catalog.yaml"
    _dump_yaml(
        prohibited_path,
        {
            "pipeline_version": PIPELINE_VERSION,
            "note": "These sources cannot be enabled. Reddit is an absolute exclusion.",
            "sources": buckets["prohibited"],
        },
    )
    written["prohibited_catalog"] = prohibited_path

    matchers_path = root / "sources" / "prohibited" / "matchers.yaml"
    _dump_yaml(
        matchers_path,
        {
            "pipeline_version": PIPELINE_VERSION,
            "matchers": PROHIBITED_MATCHERS,
        },
    )
    written["prohibited_matchers"] = matchers_path
    return written
