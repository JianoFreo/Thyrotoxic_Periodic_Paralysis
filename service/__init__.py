"""
TPP Prediction Service — business logic layer.

Orchestrates vitals ingestion, model inference, and prediction persistence.
"""

import time
import pickle
import os
from typing import Optional

from model import VitalsInput, Prediction
from dao import VitalsDAO, PredictionDAO


class TPPService:
    _model = None  # Lazy-loaded model artifact
    _model_load_attempted = False
    
    @staticmethod
    def _load_model():
        """Load the trained model from disk (lazy-init)."""
        if TPPService._model is None and not TPPService._model_load_attempted:
            TPPService._model_load_attempted = True
            model_path = os.environ.get(
                "MODEL_PATH",
                os.path.join("models", "trained_model.pkl")
            )
            try:
                if os.path.exists(model_path):
                    with open(model_path, "rb") as f:
                        TPPService._model = pickle.load(f)
                    print(f"[Service] Loaded model from {model_path}")
                else:
                    print(f"[Service] Warning: model not found at {model_path}, using fallback")
            except Exception as exc:
                TPPService._model = None
                print(f"[Service] Warning: failed to load model at {model_path} ({exc}), using fallback")
        return TPPService._model

    @staticmethod
    def compute_risk_fallback(vitals: VitalsInput) -> tuple:
        """
        Fallback risk computation when model is unavailable or for quick testing.
        
        Returns (risk_score, severity_level, timeline, recommendation)
        """
        hr = vitals.heart_rate or 0
        hrv = vitals.hrv or 0
        steps = vitals.steps or 0

        risk = 0.1
        if hr > 110:
            risk += 0.3
        if hr > 130:
            risk += 0.2
        if steps < 20:
            risk += 0.15
        if hrv > 0 and hrv < 25:
            risk += 0.25

        risk_score = min(0.95, max(0.05, risk))

        # Determine severity
        if risk_score >= 0.85:
            severity = "critical"
            timeline = "0-3 hours"
            recommendation = "High-risk signature detected. Prioritize immediate rest, avoid exertion, and follow emergency care plan."
        elif risk_score >= 0.65:
            severity = "high"
            timeline = "3-12 hours"
            recommendation = "Elevated risk trend observed. Limit intense activity and monitor symptoms every 30 minutes."
        elif risk_score >= 0.35:
            severity = "moderate"
            timeline = "12-24 hours"
            recommendation = "Moderate risk. Continue hydration, maintain regular checks, and avoid sudden workload spikes."
        else:
            severity = "low"
            timeline = "24-72 hours"
            recommendation = "Low risk currently. Keep routine monitoring and maintain medication adherence."

        return risk_score, severity, timeline, recommendation

    @staticmethod
    def predict(vitals: VitalsInput, use_model: bool = True) -> Prediction:
        """
        Generate a TPP risk prediction from vitals.
        
        Args:
            vitals: Input vitals record
            use_model: If True, try model inference; otherwise use fallback
        
        Returns:
            Prediction with risk_score, severity, timeline, and recommendation
        """
        start_time = time.time()

        # First, persist the vitals input
        input_id = VitalsDAO.insert_vitals(vitals)

        # Compute prediction
        try:
            if use_model:
                model = TPPService._load_model()
                if model:
                    # Format vitals for model input (would be numpy array in practice)
                    # For now, use fallback
                    risk_score, severity, timeline, rec = TPPService.compute_risk_fallback(vitals)
                else:
                    risk_score, severity, timeline, rec = TPPService.compute_risk_fallback(vitals)
            else:
                risk_score, severity, timeline, rec = TPPService.compute_risk_fallback(vitals)
        except Exception as e:
            print(f"[Service] Prediction error: {e}, using fallback")
            risk_score, severity, timeline, rec = TPPService.compute_risk_fallback(vitals)

        processing_time_ms = round((time.time() - start_time) * 1000)

        # Create and persist prediction
        pred = Prediction(
            input_id=input_id,
            risk_score=risk_score,
            severity_level=severity,
            predicted_timeline=timeline,
            recommendation=rec,
            model_version="baseline-1.0",
            processing_time_ms=processing_time_ms,
        )
        prediction_id = PredictionDAO.insert_prediction(pred)
        pred.prediction_id = prediction_id

        return pred

    @staticmethod
    def get_recent_history(user_id: str, limit: int = 20) -> list:
        """
        Retrieve recent vitals and predictions for a user.
        
        Returns list of dicts with vitals + prediction joined.
        """
        vitals_list = VitalsDAO.list_recent_vitals(user_id, limit=limit)
        results = []
        for v in vitals_list:
            pred = PredictionDAO.get_prediction_by_input(v.input_id)
            results.append({
                "vitals": v,
                "prediction": pred,
            })
        return results
