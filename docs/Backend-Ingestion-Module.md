# Smartwatch Ingestion Backend Module (FastAPI)

## Why this design

- API framework: FastAPI for high-throughput validation + clear OpenAPI docs.
- Time-series database: PostgreSQL + TimescaleDB extension for hypertables, retention, and compression.
- Ingestion modes:
  - Stream mode (`POST /api/v1/ingestion/stream`) for near real-time one-event writes.
  - Batch mode (`POST /api/v1/ingestion/batch`) for large upload payloads.

## API routes

- `GET /health`
  - Basic liveness check.

- `POST /api/v1/ingestion/stream`
  - Body:
    - `event`: one discriminated event with `metric_type` in:
      - `heart_rate`
      - `steps`
      - `sleep`
      - `activity`

- `POST /api/v1/ingestion/batch`
  - Body:
    - `events`: list of discriminated events (mixed metrics allowed)
    - `allow_partial`: boolean, default true

## Event schema (validation)

Shared required fields:
- `user_id` (string)
- `timestamp` (ISO datetime)

Shared optional fields:
- `device_id` (string)
- `timezone_offset_minutes` (`-840` to `840`)
- `sample_interval_seconds` (`1` to `86400`)
- `source` (string)

Metric-specific fields:
- `heart_rate`: `bpm` (`20` to `260`)
- `steps`: `step_count` (`>=0`)
- `sleep`: `stage` (`awake|light|deep|rem`), `duration_seconds` (`>0`)
- `activity`: `activity_type`, `intensity` (`0..1`), `calories` (`>=0`)

## Timestamp alignment

Each event is aligned to a deterministic UTC bucket:
- default intervals:
  - heart_rate: 60s
  - steps: 60s
  - sleep: 900s
  - activity: 300s
- if client sends `sample_interval_seconds`, it overrides default for that event.

Alignment formula:
- `aligned_epoch = floor(event_epoch / interval_seconds) * interval_seconds`

## Database schema

Application table: `timeseries_measurements`
- `id` UUID primary key
- `user_id`, `device_id`
- `metric_type`
- `event_time` (raw timestamp)
- `aligned_time` (bucketed timestamp)
- `value_int`, `value_num`, `category`
- `payload` JSON/JSONB for source-specific fields
- `ingested_at`

Timescale SQL script (production):
- `src/ingestion_api/sql/timescaledb_schema.sql`
- includes hypertable creation and recommended indexes.

## Run the API

1. Install dependencies
   - `pip install -r requirements.txt`

2. Set database URL (optional if using defaults)
   - env var: `DATABASE_URL`

3. Start server
   - `uvicorn src.ingestion_api.main:app --reload --port 8000`

4. Open docs
   - `http://localhost:8000/docs`
