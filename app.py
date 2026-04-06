"""
TPP Web Service — unified Flask application.

Layered architecture following OCR-1 pattern:
    routes/   -> Flask blueprints  (Controller layer)
    service/  -> Business logic    (Service layer)
    dao/      -> Database access   (DAO layer)
    model/    -> Data classes      (Model / POJO layer)
    config/   -> DB connection     (Infrastructure)

Usage:
    python app.py

Endpoints:
    POST /predict   — synchronous TPP risk prediction
    GET  /history   — retrieve user prediction history
    GET  /health    — service health check
"""

import argparse
import os

from flask import Flask

from config.database import init_db
from routes import tpp_bp


def create_app():
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)
    app.register_blueprint(tpp_bp)
    return app


app = create_app()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TPP Prediction Service")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 5050)))
    args = parser.parse_args()

    init_db()

    app.run(host="0.0.0.0", port=args.port, threaded=True)
