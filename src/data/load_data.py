"""Data loading utilities for smartwatch and health monitoring inputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_data(source_path: str) -> pd.DataFrame:
    """Load wearable data from CSV, JSON, or Parquet.

    Parameters
    ----------
    source_path
        Path to source file.
    """
    path = Path(source_path)
    if not path.exists():
        raise FileNotFoundError(f"Data source does not exist: {source_path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path)
    elif suffix == ".json":
        df = pd.read_json(path)
    elif suffix in {".parquet", ".pq"}:
        df = pd.read_parquet(path)
    else:
        raise ValueError("Unsupported file format. Use CSV, JSON, or Parquet.")

    if df.empty:
        raise ValueError("Loaded dataframe is empty.")

    return df