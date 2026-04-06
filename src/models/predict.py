"""Inference helpers for batch and API prediction workflows."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.features.build_features import build_features


def predict_event(
    raw_timeseries_df: pd.DataFrame,
    artifact_path: str = "models/risk_baseline_model.joblib",
) -> pd.DataFrame:
    """Run inference using a trained baseline artifact.

    Returns a dataframe with class prediction and risk probability.
    """
    artifact_file = Path(artifact_path)
    if not artifact_file.exists():
        raise FileNotFoundError(f"Model artifact not found: {artifact_path}")

    artifact = joblib.load(artifact_file)
    model = artifact["model"]
    feature_columns = artifact["feature_columns"]

    engineered = build_features(raw_timeseries_df)
    metadata_cols = [col for col in ("user_id", "timestamp") if col in engineered.columns]

    x = engineered.reindex(columns=feature_columns, fill_value=0.0)
    y_pred = model.predict(x)

    result = engineered[metadata_cols].copy() if metadata_cols else pd.DataFrame(index=engineered.index)
    result["risk_prediction"] = y_pred

    if hasattr(model, "predict_proba"):
        result["risk_probability"] = model.predict_proba(x)[:, 1]

    return result


def _severity_from_risk_score(risk_score: float) -> str:
    if risk_score >= 0.85:
        return "critical"
    if risk_score >= 0.65:
        return "high"
    if risk_score >= 0.35:
        return "moderate"
    return "low"


def _timeline_from_severity(severity: str) -> str:
    mapping = {
        "critical": "0-3 hours",
        "high": "3-12 hours",
        "moderate": "12-24 hours",
        "low": "24-72 hours",
    }
    return mapping.get(severity, "24-72 hours")


def predict_risk_assessment(
    raw_timeseries_df: pd.DataFrame,
    artifact_path: str = "models/trained_model.pkl",
) -> dict[str, Any]:
    """Predict TPP attack risk score, severity level, and timeline window.

    Uses the same engineered-feature pipeline as training and returns the
    latest record assessment for real-time API usage.
    """
    predictions = predict_event(raw_timeseries_df=raw_timeseries_df, artifact_path=artifact_path)
    if predictions.empty:
        raise ValueError("No predictions could be generated from incoming data.")

    latest = predictions.iloc[-1]
    risk_score = float(latest.get("risk_probability", float(latest.get("risk_prediction", 0))))
    severity = _severity_from_risk_score(risk_score)
    timeline = _timeline_from_severity(severity)

    return {
        "risk_score": risk_score,
        "severity_level": severity,
        "predicted_timeline_window": timeline,
        "predicted_class": int(latest.get("risk_prediction", int(risk_score >= 0.5))),
    }