import pandas as pd

from src.ingestion_api.config import settings
from src.ingestion_api.prediction_schemas import RealtimePredictionRequest, RealtimePredictionResponse
from src.models.predict import predict_risk_assessment


def run_realtime_prediction(payload: RealtimePredictionRequest) -> RealtimePredictionResponse:
    """Convert request records to DataFrame and run model inference."""
    dataframe = pd.DataFrame([record.model_dump(mode="json") for record in payload.records])
    assessment = predict_risk_assessment(
        raw_timeseries_df=dataframe,
        artifact_path=settings.model_artifact_path,
    )

    return RealtimePredictionResponse(
        risk_score=assessment["risk_score"],
        severity_level=assessment["severity_level"],
        predicted_timeline_window=assessment["predicted_timeline_window"],
        predicted_class=assessment["predicted_class"],
    )
