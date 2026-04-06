"""Model definitions and utilities for event risk prediction."""

from __future__ import annotations

from dataclasses import dataclass

import joblib
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def suggest_model_families() -> list[dict[str, str]]:
    """Recommend model families for wearable time-series risk prediction."""
    return [
        {
            "model": "LSTM / GRU",
            "best_for": "continuous sequence modeling with medium-length windows",
            "pros": "captures temporal dependencies directly",
            "cons": "requires larger labeled data and careful regularization",
        },
        {
            "model": "Temporal CNN (TCN)",
            "best_for": "efficient sequence modeling with long receptive field",
            "pros": "parallel training and stable gradients",
            "cons": "kernel/dilation tuning is important",
        },
        {
            "model": "Transformer / Time-Series Transformer",
            "best_for": "long-range interactions and multi-signal context",
            "pros": "strong expressiveness for complex temporal patterns",
            "cons": "data hungry and more expensive",
        },
        {
            "model": "Classical ML on engineered features (baseline)",
            "best_for": "small-to-medium datasets and fast deployment",
            "pros": "interpretable and low-latency with robust training",
            "cons": "depends on quality of feature engineering",
        },
    ]


def build_baseline_model() -> Pipeline:
    """Create a strong classical baseline for binary risk prediction.

    Logistic regression is optimized with log-loss and provides calibrated-ish
    probabilities when coupled with rich engineered time-series features.
    """
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1500,
                    class_weight="balanced",
                    solver="lbfgs",
                ),
            ),
        ]
    )


@dataclass
class RiskModel:
    """Container for a trained sklearn model and metadata."""

    model: Pipeline
    feature_columns: list[str]
    task_type: str = "classification"

    def predict(self, features: pd.DataFrame):
        """Predict event risk class from engineered features."""
        x = features.reindex(columns=self.feature_columns, fill_value=0.0)
        return self.model.predict(x)

    def predict_proba(self, features: pd.DataFrame):
        """Predict event risk probabilities for classification."""
        x = features.reindex(columns=self.feature_columns, fill_value=0.0)
        if not hasattr(self.model, "predict_proba"):
            raise ValueError("Underlying model does not support predict_proba.")
        return self.model.predict_proba(x)

    def save(self, path: str) -> None:
        """Serialize model and metadata to disk."""
        artifact = {
            "model": self.model,
            "feature_columns": self.feature_columns,
            "task_type": self.task_type,
        }
        joblib.dump(artifact, path)

    @classmethod
    def load(cls, path: str) -> "RiskModel":
        """Load serialized model artifact from disk."""
        artifact = joblib.load(path)
        return cls(
            model=artifact["model"],
            feature_columns=artifact["feature_columns"],
            task_type=artifact.get("task_type", "classification"),
        )