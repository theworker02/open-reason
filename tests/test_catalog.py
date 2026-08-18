from __future__ import annotations

from open_reason.constants import PIPELINE_VERSION
from open_reason.knowledge import load_knowledge_graph
from open_reason.sources.catalog import NEVER_FETCH_HOSTS, partition_sources, write_source_catalogs


def test_catalogs_partition_reddit() -> None:
    buckets = partition_sources()
    prohibited_ids = {row["id"] for row in buckets["prohibited"]}
    assert "reddit" in prohibited_ids
    assert "quora" in prohibited_ids
    approved_ids = {row["id"] for row in buckets["approved"]}
    assert "reddit" not in approved_ids
    assert all(row["verbatim"] is False for row in buckets["approved"])


def test_write_source_catalogs(tmp_path) -> None:
    written = write_source_catalogs(root=tmp_path)
    assert written["approved_catalog"].exists()
    text = written["approved_catalog"].read_text(encoding="utf-8")
    assert PIPELINE_VERSION in text
    samples = written["approved_samples"].read_text(encoding="utf-8")
    assert '"verbatim": false' in samples
    denylist = written["restricted_denylist"].read_text(encoding="utf-8")
    assert "khanacademy.org" in denylist
    assert "reddit.com" in denylist
    assert "stackoverflow.com" in denylist
    matchers = written["prohibited_matchers"].read_text(encoding="utf-8")
    assert "reddit.com" in matchers


def test_never_fetch_hosts_include_forbidden_sites() -> None:
    hosts = " ".join(NEVER_FETCH_HOSTS)
    assert "reddit.com" in hosts
    assert "khanacademy.org" in hosts
    assert "ocw.mit.edu" in hosts
    assert "developer.mozilla.org" in hosts
    assert "stackoverflow.com" in hosts


def test_knowledge_graph_has_v1_concepts() -> None:
    graph = load_knowledge_graph()
    for cid in (
        "python.comprehensions",
        "cs.graphs",
        "math.statistics",
        "science.optics",
        "sql.indexes",
    ):
        assert cid in graph.concepts
    assert graph.misconceptions["python.typing.runtime"].concept_id == "python.typing"
    assert "python.language_depth" in graph.trajectories
