"""Preprocessing routines for wearable time-series data."""

from __future__ import annotations

import pandas as pd


_COLUMN_ALIASES = {
    "heartRate": "heart_rate",
    "hr": "heart_rate",
    "bpm": "heart_rate",
    "step_count": "steps",
    "sleep_duration": "sleep_duration_minutes",
}


def preprocess_data(data: pd.DataFrame, timestamp_col: str = "timestamp") -> pd.DataFrame:
    """Clean, normalize, and align smartwatch signals for feature extraction."""
    if data is None or data.empty:
        raise ValueError("Input data is empty.")

    frame = data.copy()
    frame = frame.rename(columns={k: v for k, v in _COLUMN_ALIASES.items() if k in frame.columns})

    if timestamp_col not in frame.columns:
        raise ValueError(f"Missing required time column: {timestamp_col}")

    frame[timestamp_col] = pd.to_datetime(frame[timestamp_col], utc=True, errors="coerce")
    frame = frame.dropna(subset=[timestamp_col]).sort_values(timestamp_col).reset_index(drop=True)

    if "user_id" not in frame.columns:
        frame["user_id"] = "global"

    numeric_candidates = [
        "heart_rate",
        "steps",
        "activity_intensity",
        "sleep_duration_minutes",
        "event_severity",
        "risk_event",
    ]
    for col in numeric_candidates:
        if col in frame.columns:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")

    return frame