from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from collections.abc import Generator
from pathlib import Path

import requests


ROOT_DIR = Path(__file__).resolve().parents[1]
PYTHON_EXE = sys.executable


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_for_health(base_url: str, timeout_seconds: float = 60.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            response = requests.get(f"{base_url}/health", timeout=2)
            if response.ok:
                return
            last_error = RuntimeError(f"Health check failed with status {response.status_code}")
        except requests.RequestException as error:
            last_error = error

        time.sleep(0.5)

    raise RuntimeError(f"API did not become ready: {last_error}")


@contextmanager
def _start_api(data_dir: Path) -> Generator[tuple[str, subprocess.Popen[str]], None, None]:
    port = _find_free_port()
    base_url = f"http://127.0.0.1:{port}"
    database_path = data_dir / "ingestion.db"

    env = os.environ.copy()
    env.update(
        {
            "PORT": str(port),
            "DATABASE_URL": f"sqlite:///{database_path.as_posix()}",
            "JWT_SECRET_KEY": "test-secret-key",
        }
    )

    process = subprocess.Popen(
        [
            PYTHON_EXE,
            "-m",
            "uvicorn",
            "src.ingestion_api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=ROOT_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        _wait_for_health(base_url)
        yield base_url, process
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)


def _auth_headers(base_url: str, username: str, password: str) -> dict[str, str]:
    token_response = requests.post(
        f"{base_url}/api/v1/auth/token",
        data={"username": username, "password": password},
        timeout=10,
    )

    assert token_response.status_code == 200
    access_token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def test_live_api_end_to_end_flow(tmp_path: Path) -> None:
    data_dir = tmp_path / "api-data"
    data_dir.mkdir()

    with _start_api(data_dir) as (base_url, _process):
        health_response = requests.get(f"{base_url}/health", timeout=10)
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "ok"

        unauthorized_response = requests.post(
            f"{base_url}/api/v1/ingest",
            json={"events": []},
            timeout=10,
        )
        assert unauthorized_response.status_code == 401

        user_payload = {
            "username": "system_tester",
            "email": "system_tester@example.com",
            "full_name": "System Tester",
            "password": "StrongPass123",
        }
        create_user_response = requests.post(
            f"{base_url}/api/v1/users",
            json=user_payload,
            timeout=10,
        )
        assert create_user_response.status_code == 201
        assert create_user_response.json()["username"] == user_payload["username"]

        headers = _auth_headers(base_url, user_payload["username"], user_payload["password"])

        me_response = requests.get(f"{base_url}/api/v1/users/me", headers=headers, timeout=10)
        assert me_response.status_code == 200
        assert me_response.json()["email"] == user_payload["email"]

        ingest_payload = {
            "events": [
                {
                    "metric_type": "heart_rate",
                    "user_id": "system_tester",
                    "timestamp": "2026-01-01T00:00:00Z",
                    "bpm": 112,
                },
                {
                    "metric_type": "steps",
                    "user_id": "system_tester",
                    "timestamp": "2026-01-01T00:05:00Z",
                    "step_count": 18,
                },
            ],
            "allow_partial": True,
        }
        ingest_response = requests.post(
            f"{base_url}/api/v1/ingest",
            json=ingest_payload,
            headers=headers,
            timeout=10,
        )
        assert ingest_response.status_code == 200
        assert ingest_response.json()["accepted"] == 2
        assert ingest_response.json()["rejected"] == 0

        predict_payload = {
            "records": [
                {
                    "user_id": "system_tester",
                    "timestamp": "2026-01-01T00:00:00Z",
                    "heart_rate": 112,
                    "steps": 18,
                    "activity_intensity": 0.2,
                    "sleep_duration_minutes": 0,
                    "sleep_stage": "awake",
                    "is_sleeping": False,
                }
            ]
        }
        prediction_response = requests.post(
            f"{base_url}/api/v1/predict/realtime",
            json=predict_payload,
            headers=headers,
            timeout=10,
        )
        assert prediction_response.status_code == 200
        prediction_payload = prediction_response.json()
        assert 0 <= prediction_payload["risk_score"] <= 1
        assert prediction_payload["severity_level"]
        assert prediction_payload["predicted_timeline_window"]
        assert isinstance(prediction_payload["predicted_class"], int)
