from fastapi import APIRouter

from src.ingestion_api.prediction_schemas import RealtimePredictionRequest, RealtimePredictionResponse
from src.ingestion_api.services.prediction import run_realtime_prediction

router = APIRouter(prefix="/prediction", tags=["prediction"])


@router.post("/realtime", response_model=RealtimePredictionResponse)
def realtime_prediction(payload: RealtimePredictionRequest) -> RealtimePredictionResponse:
    """Predict TPP risk in real-time from incoming user time-series records."""
    return run_realtime_prediction(payload)
