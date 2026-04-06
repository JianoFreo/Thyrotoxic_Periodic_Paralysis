from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.ingestion_api.config import settings
from src.ingestion_api.models import TimeSeriesMeasurement
from src.ingestion_api.schemas import (
    ActivityEvent,
    HeartRateEvent,
    IngestFailure,
    IngestionEvent,
    IngestResponse,
    MetricType,
    SleepEvent,
    StepsEvent,
)

DEFAULT_INTERVALS_SECONDS = {
    MetricType.heart_rate: 60,
    MetricType.steps: 60,
    MetricType.sleep: 900,
    MetricType.activity: 300,
}


def _align_timestamp(ts: datetime, interval_seconds: int) -> datetime:
    ts_utc = ts.astimezone(UTC)
    epoch = int(ts_utc.timestamp())
    aligned_epoch = (epoch // interval_seconds) * interval_seconds
    return datetime.fromtimestamp(aligned_epoch, tz=UTC)


def _build_row(event: IngestionEvent) -> TimeSeriesMeasurement:
    interval = event.sample_interval_seconds or DEFAULT_INTERVALS_SECONDS.get(
        event.metric_type,
        settings.default_alignment_seconds,
    )

    aligned_time = _align_timestamp(event.timestamp, interval)

    value_int: int | None = None
    value_num: float | None = None
    category: str | None = None

    if isinstance(event, HeartRateEvent):
        value_int = int(event.bpm)
    elif isinstance(event, StepsEvent):
        value_int = int(event.step_count)
    elif isinstance(event, SleepEvent):
        value_int = int(event.duration_seconds)
        category = event.stage.value
    elif isinstance(event, ActivityEvent):
        value_num = float(event.intensity) if event.intensity is not None else None
        category = event.activity_type.value

    payload = event.model_dump(mode="json")
    payload.pop("metric_type", None)

    return TimeSeriesMeasurement(
        user_id=event.user_id,
        device_id=event.device_id,
        metric_type=event.metric_type.value,
        event_time=event.timestamp.astimezone(UTC),
        aligned_time=aligned_time,
        value_int=value_int,
        value_num=value_num,
        category=category,
        payload=payload,
    )


def ingest_stream(db: Session, event: IngestionEvent) -> IngestResponse:
    row = _build_row(event)
    db.add(row)
    db.commit()
    return IngestResponse(accepted=1, rejected=0, failures=[])


def ingest_batch(db: Session, events: list[IngestionEvent], allow_partial: bool = True) -> IngestResponse:
    accepted = 0
    failures: list[IngestFailure] = []

    for idx, event in enumerate(events):
        try:
            db.add(_build_row(event))
            accepted += 1
        except Exception as exc:
            failures.append(IngestFailure(index=idx, reason=str(exc)))
            if not allow_partial:
                db.rollback()
                return IngestResponse(accepted=0, rejected=len(events), failures=failures)

    if failures and not allow_partial:
        db.rollback()
        return IngestResponse(accepted=0, rejected=len(events), failures=failures)

    if failures:
        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            return IngestResponse(
                accepted=0,
                rejected=len(events),
                failures=[IngestFailure(index=-1, reason=f"database commit error: {exc}")],
            )
    else:
        db.commit()

    return IngestResponse(accepted=accepted, rejected=len(events) - accepted, failures=failures)
