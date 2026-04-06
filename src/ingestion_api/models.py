import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, JSON, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.ingestion_api.database import Base


class TimeSeriesMeasurement(Base):
    __tablename__ = "timeseries_measurements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    device_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)

    metric_type: Mapped[str] = mapped_column(String(32), index=True)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    aligned_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    value_int: Mapped[int | None] = mapped_column(Integer, nullable=True)
    value_num: Mapped[float | None] = mapped_column(Float, nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)

    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_measurements_user_metric_time", "user_id", "metric_type", "aligned_time"),
        Index("ix_measurements_metric_time", "metric_type", "aligned_time"),
    )
