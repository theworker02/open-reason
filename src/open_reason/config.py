"""Pipeline and dataset configuration loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from open_reason.constants import CURRENT_CONFIGS, DEFAULT_SEED, PIPELINE_VERSION


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists() and (parent / "configs").exists():
            return parent
    return Path.cwd()


class PipelineConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str = PIPELINE_VERSION
    seed: int = DEFAULT_SEED
    configs: list[str] = Field(default_factory=lambda: list(CURRENT_CONFIGS))
    reddit_block: bool = True
    verification_timeout_s: int = 12
    verification_memory_mb: int = 512
    max_near_duplicate_similarity: float = 0.92
    require_license: bool = True
    strict: bool = False


class DatasetConfigFile(BaseModel):
    model_config = ConfigDict(extra="allow")

    configs: dict[str, Any] = Field(default_factory=dict)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a mapping")
    return data


def load_pipeline_config(root: Path | None = None) -> PipelineConfig:
    root = root or repo_root()
    path = root / "configs" / "pipeline.yaml"
    if not path.exists():
        return PipelineConfig()
    return PipelineConfig.model_validate(load_yaml(path))


def resolve_config_name(name: str) -> str:
    normalized = name.strip().lower()
    if normalized not in CURRENT_CONFIGS and normalized not in {"all"}:
        # Allow registered future names from datasets.yaml without breaking.
        return normalized
    return normalized
