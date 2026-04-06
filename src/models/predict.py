"""Inference helpers for batch and API prediction workflows."""

from __future__ import annotations

from pathlib import Path

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