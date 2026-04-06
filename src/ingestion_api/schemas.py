from datetime import datetime
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

BpmValue = Annotated[int, Field(ge=20, le=260)]
StepCountValue = Annotated[int, Field(ge=0)]
SleepDurationSeconds = Annotated[int, Field(gt=0)]
IntensityValue = Annotated[float, Field(ge=0, le=1)]
CaloriesValue = Annotated[float, Field(ge=0)]


class MetricType(str, Enum):
    heart_rate = "heart_rate"
    steps = "steps"
    sleep = "sleep"
    activity = "activity"


class BaseEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(min_length=1, max_length=128)
    device_id: str | None = Field(default=None, max_length=128)
    timestamp: datetime
    timezone_offset_minutes: int | None = Field(default=None, ge=-840, le=840)
    sample_interval_seconds: int | None = Field(default=None, ge=1, le=86400)
    source: str | None = Field(default=None, max_length=64)


class HeartRateEvent(BaseEvent):
    metric_type: Literal[MetricType.heart_rate] = MetricType.heart_rate
    bpm: BpmValue


class StepsEvent(BaseEvent):
    metric_type: Literal[MetricType.steps] = MetricType.steps
    step_count: StepCountValue


class SleepStage(str, Enum):
    awake = "awake"
    light = "light"
    deep = "deep"
    rem = "rem"


class SleepEvent(BaseEvent):
    metric_type: Literal[MetricType.sleep] = MetricType.sleep
    stage: SleepStage
    duration_seconds: SleepDurationSeconds


class ActivityType(str, Enum):
    sedentary = "sedentary"
    walk = "walk"
    run = "run"
    cycle = "cycle"
    workout = "workout"
    other = "other"


class ActivityEvent(BaseEvent):
    metric_type: Literal[MetricType.activity] = MetricType.activity
    activity_type: ActivityType
    intensity: IntensityValue | None = None
    calories: CaloriesValue | None = None


IngestionEvent = Annotated[
    HeartRateEvent | StepsEvent | SleepEvent | ActivityEvent,
    Field(discriminator="metric_type"),
]


class StreamIngestRequest(BaseModel):
    event: IngestionEvent


class BatchIngestRequest(BaseModel):
    events: list[IngestionEvent] = Field(min_length=1, max_length=20000)
    allow_partial: bool = True


class IngestFailure(BaseModel):
    index: int
    reason: str


class IngestResponse(BaseModel):
    accepted: int
    rejected: int
    failures: list[IngestFailure] = []
