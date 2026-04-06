"""Training entry points for the wearable health monitoring model."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.evaluation.metrics import evaluate_predictions
from src.features.build_features import FeatureConfig, build_features
from src.models.model import RiskModel, build_baseline_model


def _sort_for_time_split(dataframe: pd.DataFrame, timestamp_col: str, user_col: str = "user_id") -> pd.DataFrame:
    ordered = dataframe.copy()
    ordered[timestamp_col] = pd.to_datetime(ordered[timestamp_col], utc=True, errors="coerce")
    ordered = ordered.dropna(subset=[timestamp_col])

    sort_cols = [timestamp_col]
    if user_col in ordered.columns:
        sort_cols = [user_col, timestamp_col]

    return ordered.sort_values(sort_cols).reset_index(drop=True)


def time_based_split(
    dataframe: pd.DataFrame,
    val_fraction: float,
    timestamp_col: str = "timestamp",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split data into train/validation using chronological ordering."""
    if not 0 < val_fraction < 1:
        raise ValueError("val_fraction must be between 0 and 1.")

    ordered = dataframe.sort_values(timestamp_col).reset_index(drop=True)
    split_idx = int(len(ordered) * (1 - val_fraction))

    if split_idx <= 0 or split_idx >= len(ordered):
        raise ValueError("Time-based split produced an empty train or validation set.")

    return ordered.iloc[:split_idx].copy(), ordered.iloc[split_idx:].copy()


def train_model(
    raw_timeseries_df: pd.DataFrame,
    target_col: str = "risk_event",
    timestamp_col: str = "timestamp",
    val_fraction: float = 0.2,
    artifact_path: str = "models/risk_baseline_model.joblib",
    feature_config: FeatureConfig | None = None,
) -> dict[str, Any]:
    """Train a baseline risk model from raw time-series dataframe.

    Pipeline:
    1) Chronological ordering
    2) Feature engineering
    3) Time-based train/validation split
    4) Fit baseline classifier (log-loss objective)
    5) Evaluate and persist artifact
    """
    if target_col not in raw_timeseries_df.columns:
        raise ValueError(f"Missing target column: {target_col}")

    ordered_raw = _sort_for_time_split(raw_timeseries_df, timestamp_col=timestamp_col)

    # Keep target aligned with feature rows by engineering on the same ordered frame.
    y = ordered_raw[target_col].astype(int).reset_index(drop=True)
    features = build_features(ordered_raw, config=feature_config)

    if timestamp_col not in features.columns:
        raise ValueError("Feature matrix must contain timestamp for time-based validation.")

    dataset = features.copy()
    dataset[target_col] = y

    train_df, val_df = time_based_split(dataset, val_fraction=val_fraction, timestamp_col=timestamp_col)

    id_cols = [col for col in ("user_id", timestamp_col) if col in train_df.columns]
    feature_cols = [col for col in train_df.columns if col not in id_cols + [target_col]]

    x_train = train_df[feature_cols]
    y_train = train_df[target_col].astype(int)
    x_val = val_df[feature_cols]
    y_val = val_df[target_col].astype(int)

    pipeline = build_baseline_model()
    pipeline.fit(x_train, y_train)

    y_pred = pipeline.predict(x_val)
    y_proba = pipeline.predict_proba(x_val)
    metrics = evaluate_predictions(y_true=y_val, y_pred=y_pred, y_proba=y_proba)

    model = RiskModel(model=pipeline, feature_columns=feature_cols, task_type="classification")

    artifact = {
        "model": model.model,
        "feature_columns": model.feature_columns,
        "task_type": model.task_type,
        "target_col": target_col,
        "timestamp_col": timestamp_col,
        "validation_metrics": metrics,
        "n_train": int(len(train_df)),
        "n_val": int(len(val_df)),
    }

    artifact_file = Path(artifact_path)
    artifact_file.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, artifact_file)

    return artifact