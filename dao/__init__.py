"""
Data Access Object for TPP vitals and predictions.

Handles all database read/write operations for vitals input and predictions.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from config.database import get_connection
from model import VitalsInput, Prediction


class VitalsDAO:
    @staticmethod
    def insert_vitals(vitals: VitalsInput) -> str:
        """Insert a new vitals record. Returns the generated input_id."""
        input_id = vitals.input_id or str(uuid.uuid4())
        conn = get_connection()
        conn.execute("""
            INSERT INTO vitals_input (
                input_id, user_id, heart_rate, hrv, steps,
                activity_intensity, sleep_duration_mins, sleep_stage,
                is_sleeping, source, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            input_id,
            vitals.user_id,
            vitals.heart_rate,
            vitals.hrv,
            vitals.steps,
            vitals.activity_intensity,
            vitals.sleep_duration_mins,
            vitals.sleep_stage,
            vitals.is_sleeping,
            vitals.source,
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        conn.commit()
        return input_id

    @staticmethod
    def get_vitals(input_id: str) -> Optional[VitalsInput]:
        """Retrieve a vitals record by ID."""
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM vitals_input WHERE input_id = ?",
            (input_id,)
        ).fetchone()
        if not row:
            return None
        return VitalsInput(
            input_id=row["input_id"],
            user_id=row["user_id"],
            heart_rate=row["heart_rate"],
            hrv=row["hrv"],
            steps=row["steps"],
            activity_intensity=row["activity_intensity"],
            sleep_duration_mins=row["sleep_duration_mins"],
            sleep_stage=row["sleep_stage"],
            is_sleeping=row["is_sleeping"],
            source=row["source"],
            created_at=row["created_at"],
        )

    @staticmethod
    def list_recent_vitals(user_id: str, limit: int = 100) -> List[VitalsInput]:
        """Retrieve recent vitals for a user."""
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM vitals_input WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        ).fetchall()
        return [
            VitalsInput(
                input_id=row["input_id"],
                user_id=row["user_id"],
                heart_rate=row["heart_rate"],
                hrv=row["hrv"],
                steps=row["steps"],
                activity_intensity=row["activity_intensity"],
                sleep_duration_mins=row["sleep_duration_mins"],
                sleep_stage=row["sleep_stage"],
                is_sleeping=row["is_sleeping"],
                source=row["source"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    @staticmethod
    def delete_vitals(input_id: str) -> bool:
        """Delete a vitals row by input_id. Returns True when a row is deleted."""
        conn = get_connection()
        cur = conn.execute(
            "DELETE FROM vitals_input WHERE input_id = ?",
            (input_id,),
        )
        conn.commit()
        return cur.rowcount > 0


class PredictionDAO:
    @staticmethod
    def insert_prediction(pred: Prediction) -> str:
        """Insert a new prediction record. Returns the generated prediction_id."""
        prediction_id = pred.prediction_id or str(uuid.uuid4())
        conn = get_connection()
        conn.execute("""
            INSERT INTO predictions (
                prediction_id, input_id, risk_score, severity_level,
                predicted_timeline, recommendation, model_version,
                processing_time_ms, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prediction_id,
            pred.input_id,
            pred.risk_score,
            pred.severity_level,
            pred.predicted_timeline,
            pred.recommendation,
            pred.model_version,
            pred.processing_time_ms,
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        conn.commit()
        return prediction_id

    @staticmethod
    def get_prediction(prediction_id: str) -> Optional[Prediction]:
        """Retrieve a prediction record by ID."""
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM predictions WHERE prediction_id = ?",
            (prediction_id,)
        ).fetchone()
        if not row:
            return None
        return Prediction(
            prediction_id=row["prediction_id"],
            input_id=row["input_id"],
            risk_score=row["risk_score"],
            severity_level=row["severity_level"],
            predicted_timeline=row["predicted_timeline"],
            recommendation=row["recommendation"],
            model_version=row["model_version"],
            processing_time_ms=row["processing_time_ms"],
            created_at=row["created_at"],
        )

    @staticmethod
    def get_prediction_by_input(input_id: str) -> Optional[Prediction]:
        """Retrieve the prediction for a given vitals input."""
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM predictions WHERE input_id = ? LIMIT 1",
            (input_id,)
        ).fetchone()
        if not row:
            return None
        return Prediction(
            prediction_id=row["prediction_id"],
            input_id=row["input_id"],
            risk_score=row["risk_score"],
            severity_level=row["severity_level"],
            predicted_timeline=row["predicted_timeline"],
            recommendation=row["recommendation"],
            model_version=row["model_version"],
            processing_time_ms=row["processing_time_ms"],
            created_at=row["created_at"],
        )

    @staticmethod
    def list_recent_predictions(user_id: str, limit: int = 50) -> List[Prediction]:
        """Retrieve recent predictions for a user (via vitals join)."""
        conn = get_connection()
        rows = conn.execute("""
            SELECT p.* FROM predictions p
            JOIN vitals_input v ON p.input_id = v.input_id
            WHERE v.user_id = ?
            ORDER BY p.created_at DESC
            LIMIT ?
        """, (user_id, limit)).fetchall()
        return [
            Prediction(
                prediction_id=row["prediction_id"],
                input_id=row["input_id"],
                risk_score=row["risk_score"],
                severity_level=row["severity_level"],
                predicted_timeline=row["predicted_timeline"],
                recommendation=row["recommendation"],
                model_version=row["model_version"],
                processing_time_ms=row["processing_time_ms"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    @staticmethod
    def delete_prediction_by_input(input_id: str) -> int:
        """Delete prediction rows for a given input_id. Returns deleted row count."""
        conn = get_connection()
        cur = conn.execute(
            "DELETE FROM predictions WHERE input_id = ?",
            (input_id,),
        )
        conn.commit()
        return cur.rowcount
