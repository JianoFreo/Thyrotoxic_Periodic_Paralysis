"""Command-line entry point for model training."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.train import train_model


DEFAULT_CONFIG_PATH = "configs/config.yaml"


def _load_config(config_path: str) -> dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as fp:
        return yaml.safe_load(fp) or {}


def _find_processed_data_file(config: dict[str, Any]) -> Path:
    training_cfg = config.get("training", {})
    paths_cfg = config.get("paths", {})

    explicit_file = training_cfg.get("processed_data_file")
    if explicit_file:
        path = Path(explicit_file)
        if not path.exists():
            raise FileNotFoundError(f"Configured processed data file does not exist: {path}")
        return path

    processed_dir = Path(paths_cfg.get("processed_data", "data/processed"))
    if not processed_dir.exists():
        raise FileNotFoundError(f"Processed data directory does not exist: {processed_dir}")

    csv_files = sorted(processed_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found in processed data directory. "
            "Set training.processed_data_file in configs/config.yaml."
        )

    return csv_files[-1]


def _write_metrics_log(metrics_path: Path, payload: dict[str, Any]) -> None:
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with open(metrics_path, "w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train baseline risk model from processed wearable time-series CSV.")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to YAML config file.")
    parser.add_argument("--data", default=None, help="Optional override path to processed CSV file.")
    parser.add_argument("--artifact", default=None, help="Optional override model artifact output path.")
    parser.add_argument("--metrics-log", default=None, help="Optional override metrics log JSON path.")
    args = parser.parse_args()

    config = _load_config(args.config)

    data_cfg = config.get("data", {})
    model_cfg = config.get("model", {})
    paths_cfg = config.get("paths", {})
    training_cfg = config.get("training", {})

    data_path = Path(args.data) if args.data else _find_processed_data_file(config)
    target_col = data_cfg.get("target_column", "risk_event")
    timestamp_col = data_cfg.get("time_column", "timestamp")
    val_fraction = float(training_cfg.get("validation_fraction", training_cfg.get("test_size", 0.2)))

    model_dir = Path(paths_cfg.get("models", "models"))
    artifact_name = model_cfg.get("artifact_name", "risk_baseline_model.joblib")
    artifact_path = Path(args.artifact) if args.artifact else (model_dir / artifact_name)

    logs_dir = Path(paths_cfg.get("logs", "logs"))
    metrics_file = training_cfg.get("metrics_file", "training_metrics.json")
    metrics_path = Path(args.metrics_log) if args.metrics_log else (logs_dir / metrics_file)

    raw_df = pd.read_csv(data_path)
    artifact = train_model(
        raw_timeseries_df=raw_df,
        target_col=target_col,
        timestamp_col=timestamp_col,
        val_fraction=val_fraction,
        artifact_path=str(artifact_path),
    )

    run_summary = {
        "project": config.get("project", {}).get("name", "wearable-health-monitoring"),
        "data_file": str(data_path),
        "artifact_path": str(artifact_path),
        "target_column": target_col,
        "timestamp_column": timestamp_col,
        "validation_fraction": val_fraction,
        "n_train": artifact.get("n_train"),
        "n_val": artifact.get("n_val"),
        "metrics": artifact.get("validation_metrics", {}),
    }
    _write_metrics_log(metrics_path, run_summary)

    print("Training complete.")
    print(f"Data loaded from: {data_path}")
    print(f"Artifact saved to: {artifact_path}")
    print(f"Metrics logged to: {metrics_path}")
    print(f"Validation metrics: {artifact['validation_metrics']}")


if __name__ == "__main__":
    main()