"""Evaluation metrics for model validation and monitoring."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    f1_score,
    log_loss,
    precision_recall_fscore_support,
    roc_auc_score,
)


def evaluate_predictions(
    y_true: Any,
    y_pred: Any,
    y_proba: Any | None = None,
) -> dict[str, float]:
    """Compute classification metrics and losses for risk prediction."""
    y_true_arr = np.asarray(y_true)
    y_pred_arr = np.asarray(y_pred)

    precision, recall, _, _ = precision_recall_fscore_support(
        y_true_arr,
        y_pred_arr,
        average="binary",
        zero_division=0,
    )

    metrics: dict[str, float] = {
        "accuracy": float(accuracy_score(y_true_arr, y_pred_arr)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1_score(y_true_arr, y_pred_arr, zero_division=0)),
    }

    if y_proba is not None:
        proba_arr = np.asarray(y_proba)
        pos_proba = proba_arr[:, 1] if proba_arr.ndim == 2 else proba_arr

        metrics["log_loss"] = float(log_loss(y_true_arr, proba_arr))
        metrics["brier_score"] = float(brier_score_loss(y_true_arr, pos_proba))
        metrics["roc_auc"] = float(roc_auc_score(y_true_arr, pos_proba))
        metrics["pr_auc"] = float(average_precision_score(y_true_arr, pos_proba))

    return metrics