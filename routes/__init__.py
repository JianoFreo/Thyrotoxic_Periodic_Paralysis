from flask import Blueprint, request, jsonify

from model import VitalsInput
from service import TPPService

tpp_bp = Blueprint("tpp", __name__)


@tpp_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "tpp-prediction"}), 200


@tpp_bp.route("/predict", methods=["POST"])
def predict():
    """
    POST /predict
    
    Request body (JSON):
    {
        "user_id": "user-1",
        "heart_rate": 138,
        "hrv": 18,
        "steps": 5,
        "activity_intensity": 0,
        "sleep_duration_mins": 480,
        "sleep_stage": "awake",
        "is_sleeping": false
    }
    
    Response:
    {
        "prediction_id": "...",
        "input_id": "...",
        "risk_score": 0.95,
        "severity_level": "critical",
        "predicted_timeline": "0-3 hours",
        "recommendation": "...",
        "processing_time_ms": 15
    }
    """
    try:
        data = request.get_json()
        if not data or "user_id" not in data:
            return jsonify({"error": "Missing user_id"}), 400

        vitals = VitalsInput(
            user_id=data["user_id"],
            heart_rate=data.get("heart_rate"),
            hrv=data.get("hrv"),
            steps=data.get("steps"),
            activity_intensity=data.get("activity_intensity"),
            sleep_duration_mins=data.get("sleep_duration_mins"),
            sleep_stage=data.get("sleep_stage"),
            is_sleeping=data.get("is_sleeping", False),
            source=data.get("source", "api"),
        )

        pred = TPPService.predict(vitals)

        return jsonify({
            "prediction_id": pred.prediction_id,
            "input_id": pred.input_id,
            "risk_score": pred.risk_score,
            "severity_level": pred.severity_level,
            "predicted_timeline": pred.predicted_timeline,
            "recommendation": pred.recommendation,
            "processing_time_ms": pred.processing_time_ms,
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tpp_bp.route("/history", methods=["GET"])
def history():
    """
    GET /history?user_id=user-1&limit=20
    
    Retrieve recent prediction history for a user.
    """
    try:
        user_id = request.args.get("user_id")
        limit = request.args.get("limit", 20, type=int)

        if not user_id:
            return jsonify({"error": "Missing user_id parameter"}), 400

        history = TPPService.get_recent_history(user_id, limit=limit)

        return jsonify({
            "user_id": user_id,
            "count": len(history),
            "history": [
                {
                    "input_id": item["vitals"].input_id,
                    "vitals": {
                        "heart_rate": item["vitals"].heart_rate,
                        "hrv": item["vitals"].hrv,
                        "steps": item["vitals"].steps,
                        "created_at": item["vitals"].created_at,
                    },
                    "prediction": {
                        "prediction_id": item["prediction"].prediction_id,
                        "risk_score": item["prediction"].risk_score,
                        "severity_level": item["prediction"].severity_level,
                        "predicted_timeline": item["prediction"].predicted_timeline,
                    } if item["prediction"] else None,
                }
                for item in history
            ]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
