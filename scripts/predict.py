"""Command-line entry point for batch predictions."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.predict import predict_event


def main() -> None:
    parser = argparse.ArgumentParser(description="Run batch risk prediction from wearable time-series CSV.")
    parser.add_argument("--data", required=True, help="Path to CSV file with raw time-series data.")
    parser.add_argument("--artifact", default="models/risk_baseline_model.joblib", help="Trained model artifact path.")
    parser.add_argument("--out", default="data/processed/predictions.csv", help="Output CSV path for predictions.")
    args = parser.parse_args()

    raw_df = pd.read_csv(args.data)
    predictions = predict_event(raw_df, artifact_path=args.artifact)
    predictions.to_csv(args.out, index=False)

    print(f"Predictions saved to: {args.out}")
    print(f"Generated rows: {len(predictions)}")


if __name__ == "__main__":
    main()