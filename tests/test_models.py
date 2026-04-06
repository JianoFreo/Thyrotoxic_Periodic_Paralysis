"""Tests for model training and inference logic."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.models.predict import predict_event, predict_risk_assessment
from src.models.train import train_model


def _synthetic_data(rows: int = 120) -> pd.DataFrame:
    timeline = pd.date_range("2026-01-01", periods=rows, freq="5min", tz="UTC")
    heart_rate = np.linspace(72, 130, rows)
    steps = np.random.default_rng(42).integers(0, 40, size=rows)
    activity = np.clip(steps / 40, 0, 1)
    sleep = np.where((timeline.hour >= 0) & (timeline.hour <= 6), 5.0, 0.0)

    risk_event = ((heart_rate > 108) | (activity < 0.15)).astype(int)

    return pd.DataFrame(
        {
            "timestamp": timeline,
            "user_id": "u1",
            "heart_rate": heart_rate,
            "steps": steps,
            "activity_intensity": activity,
            "sleep_duration_minutes": sleep,
            "risk_event": risk_event,
        }
    )


def test_train_model_saves_artifact(tmp_path):
    dataset = _synthetic_data()
    artifact_path = tmp_path / "trained_model.pkl"

    result = train_model(
        raw_timeseries_df=dataset,
        target_col="risk_event",
        timestamp_col="timestamp",
        val_fraction=0.2,
        artifact_path=str(artifact_path),
    )

    assert artifact_path.exists()
    assert "validation_metrics" in result
    assert "f1" in result["validation_metrics"]


def test_predict_pipeline_outputs_required_columns(tmp_path):
    dataset = _synthetic_data()
    artifact_path = tmp_path / "trained_model.pkl"
    train_model(dataset, target_col="risk_event", artifact_path=str(artifact_path))

    predictions = predict_event(dataset.tail(20), artifact_path=str(artifact_path))
    assert "risk_prediction" in predictions.columns
    assert "risk_probability" in predictions.columns

    assessment = predict_risk_assessment(dataset.tail(20), artifact_path=str(artifact_path))
    assert "risk_score" in assessment
    assert "severity_level" in assessment
    assert "predicted_timeline_window" in assessment