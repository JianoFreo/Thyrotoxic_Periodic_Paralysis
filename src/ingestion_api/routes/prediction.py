from fastapi import APIRouter
from fastapi import Depends

from src.ingestion_api.dependencies import get_current_user
from src.ingestion_api.models import User
from src.ingestion_api.prediction_schemas import RealtimePredictionRequest, RealtimePredictionResponse
from src.ingestion_api.services.prediction import run_realtime_prediction

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("", response_model=RealtimePredictionResponse)
def predict(payload: RealtimePredictionRequest, _: User = Depends(get_current_user)) -> RealtimePredictionResponse:
    """Primary prediction endpoint for real-time TPP risk inference."""
    return run_realtime_prediction(payload)


@router.post("/realtime", response_model=RealtimePredictionResponse)
def realtime_prediction(
    payload: RealtimePredictionRequest,
    _: User = Depends(get_current_user),
) -> RealtimePredictionResponse:
    """Predict TPP risk in real-time from incoming user time-series records."""
    return run_realtime_prediction(payload)
