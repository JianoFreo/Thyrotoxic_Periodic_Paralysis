-- Recommended production schema for PostgreSQL + TimescaleDB
-- Run once on your Postgres instance:
--   CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS timeseries_measurements (
    id UUID PRIMARY KEY,
    user_id VARCHAR(128) NOT NULL,
    device_id VARCHAR(128),
    metric_type VARCHAR(32) NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    aligned_time TIMESTAMPTZ NOT NULL,
    value_int INTEGER,
    value_num DOUBLE PRECISION,
    category VARCHAR(64),
    payload JSONB NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

SELECT create_hypertable(
    'timeseries_measurements',
    by_range('aligned_time'),
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS ix_measurements_user_metric_time
    ON timeseries_measurements (user_id, metric_type, aligned_time DESC);

CREATE INDEX IF NOT EXISTS ix_measurements_metric_time
    ON timeseries_measurements (metric_type, aligned_time DESC);

-- Optional retention/compression policies for larger deployments:
-- SELECT add_retention_policy('timeseries_measurements', INTERVAL '18 months');
-- ALTER TABLE timeseries_measurements SET (
--     timescaledb.compress,
--     timescaledb.compress_segmentby = 'user_id, metric_type'
-- );
-- SELECT add_compression_policy('timeseries_measurements', INTERVAL '7 days');
