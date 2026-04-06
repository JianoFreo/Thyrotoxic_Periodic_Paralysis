"""
SQLite database connection manager for TPP.

Provides thread-local connections and startup helpers.
Uses WAL mode for concurrent read/write from Flask, Worker, and Streamlit.
"""

import os
import sqlite3
import threading

# Database file path — configurable via environment variable.
DB_PATH = os.environ.get("DB_PATH", os.path.join("data", "tpp.db"))

_local = threading.local()


def get_connection() -> sqlite3.Connection:
    """Return a thread-local SQLite connection (reused within the same thread)."""
    if not hasattr(_local, "conn") or _local.conn is None:
        os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
        conn = sqlite3.connect(
            DB_PATH,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA foreign_keys=ON")
        _local.conn = conn
    return _local.conn


def init_db():
    """Create TPP tables if they do not exist. Called once at startup."""
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS vitals_input (
            input_id            TEXT PRIMARY KEY,
            user_id             TEXT NOT NULL,
            heart_rate          INTEGER,
            hrv                 INTEGER,
            steps               INTEGER,
            activity_intensity  INTEGER,
            sleep_duration_mins INTEGER,
            sleep_stage         TEXT,
            is_sleeping         BOOLEAN,
            source              TEXT DEFAULT 'manual',
            created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS predictions (
            prediction_id           TEXT PRIMARY KEY,
            input_id                TEXT NOT NULL,
            risk_score              REAL NOT NULL,
            severity_level          TEXT NOT NULL
                                    CHECK(severity_level IN ('low','moderate','high','critical')),
            predicted_timeline      TEXT,
            recommendation          TEXT,
            model_version           TEXT,
            processing_time_ms      INTEGER,
            created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(input_id)   REFERENCES vitals_input(input_id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_input_user    ON vitals_input(user_id);
        CREATE INDEX IF NOT EXISTS idx_input_created ON vitals_input(created_at);
        CREATE INDEX IF NOT EXISTS idx_pred_input    ON predictions(input_id);
        CREATE INDEX IF NOT EXISTS idx_pred_severity ON predictions(severity_level);
    """)
    conn.commit()
    print(f"[DB] SQLite database initialised at {DB_PATH}")
