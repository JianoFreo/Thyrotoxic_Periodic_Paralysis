"""Tests for data loading and preprocessing logic."""

from __future__ import annotations

import pandas as pd

from src.data.load_data import load_data
from src.data.preprocess import preprocess_data


def test_load_data_csv(tmp_path):
    csv_file = tmp_path / "wearable.csv"
    csv_file.write_text("timestamp,heartRate,step_count\n2026-01-01T00:00:00Z,88,12\n", encoding="utf-8")

    data = load_data(str(csv_file))
    assert not data.empty
    assert "heartRate" in data.columns


def test_preprocess_data_normalizes_columns_and_time():
    raw = pd.DataFrame(
        {
            "timestamp": ["2026-01-01T00:00:00Z", "2026-01-01T00:01:00Z"],
            "heartRate": [90, 96],
            "step_count": [10, 16],
        }
    )

    processed = preprocess_data(raw)
    assert "heart_rate" in processed.columns
    assert "steps" in processed.columns
    assert "user_id" in processed.columns
    assert str(processed["timestamp"].dtype).startswith("datetime64")