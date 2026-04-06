from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.ingestion_api.database import get_db
from src.ingestion_api.schemas import BatchIngestRequest, IngestResponse, StreamIngestRequest
from src.ingestion_api.services.ingestion import ingest_batch, ingest_stream

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/stream", response_model=IngestResponse)
def stream_ingest(payload: StreamIngestRequest, db: Session = Depends(get_db)) -> IngestResponse:
    """Ingest one event at a time (suitable for near real-time streaming clients)."""
    return ingest_stream(db, payload.event)


@router.post("/batch", response_model=IngestResponse)
def batch_ingest(payload: BatchIngestRequest, db: Session = Depends(get_db)) -> IngestResponse:
    """Ingest many events in one request with optional partial acceptance."""
    return ingest_batch(db, payload.events, allow_partial=payload.allow_partial)
