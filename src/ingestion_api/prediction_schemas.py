from datetime import datetime

from pydantic import BaseModel, Field


class TimeSeriesPoint(BaseModel):
    """Incoming real-time wearable record for one timestamp."""

    user_id: str = Field(min_length=1, max_length=128)
    timestamp: datetime
    heart_rate: float | None = None
    bpm: float | None = None
    steps: float | None = None
    step_count: float | None = None
    activity_intensity: float | None = None
    activity: float | None = None
    sleep_duration_minutes: float | None = None
    sleep_stage: str | None = None
    is_sleeping: int | bool | None = None


class RealtimePredictionRequest(BaseModel):
    """Real-time risk prediction payload."""

    records: list[TimeSeriesPoint] = Field(min_length=1, max_length=20000)


class RealtimePredictionResponse(BaseModel):
    """Risk response payload for TPP attack prediction."""

    risk_score: float = Field(ge=0, le=1)
    severity_level: str
    predicted_timeline_window: str
    predicted_class: int
