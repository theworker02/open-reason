"""CLI tests that do not require a full coding sandbox run."""

from __future__ import annotations

from typer.testing import CliRunner

from open_reason.cli import app

runner = CliRunner()


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "validate" in result.stdout
    assert "discover" in result.stdout
    assert "evaluate-sources" in result.stdout
    assert "analyze-coverage" in result.stdout
    assert "train" in result.stdout
    assert "catalogs" in result.stdout
    assert "score" in result.stdout
    assert "Reddit" in result.stdout or "reddit" in result.stdout.lower()


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "open-reason" in result.stdout


def test_sources_help() -> None:
    result = runner.invoke(app, ["sources", "--help"])
    assert result.exit_code == 0
    assert "matrix" in result.stdout.lower() or "source" in result.stdout.lower()


def test_generate_help() -> None:
    result = runner.invoke(app, ["generate", "--help"])
    assert result.exit_code == 0
    assert "domain" in result.stdout.lower()


def test_ingest_unreviewed_source_fails() -> None:
    result = runner.invoke(app, ["ingest", "--source", "stack-exchange"])
    assert result.exit_code != 0
    combined = (result.stdout or "") + (result.stderr or "")
    assert "not enabled" in combined.lower() or "forbids" in combined.lower()


def test_sources_approve_help() -> None:
    result = runner.invoke(app, ["sources", "--help"])
    assert result.exit_code == 0
    assert "approve" in result.stdout.lower()
