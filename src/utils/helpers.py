"""Shared utility helpers for the ML pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def ensure_directory(path: str | Path) -> Path:
    """Create a directory if it does not exist and return its Path."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML file as dictionary."""
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}