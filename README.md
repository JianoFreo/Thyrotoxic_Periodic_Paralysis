# TPP Hyphertyrodism AI Data System

![alt text](image.png)

Full-stack AI and machine learning software for Thyrotoxic Periodic Paralysis (TPP) monitoring with smartwatch data ingestion. The platform tracks physiological behavior, predicts TPP attack risk and likely timeline windows, and provides recommendation support for preparedness and clinical follow-up.

## Clean Architecture

The repository is organized around a single ML workflow, a React dashboard, and a FastAPI service layer:

- `data/raw/` stores incoming smartwatch exports.
- `data/processed/` stores cleaned data, training input, and prediction outputs.
- `notebooks/exploration.ipynb` is the main notebook for analysis.
- `src/data/` handles loading and preprocessing.
- `src/features/` builds time-series features.
- `src/models/` contains training and inference code.
- `src/evaluation/` contains evaluation metrics.
- `src/utils/` contains shared helpers.
- `src/ingestion_api/` contains the FastAPI auth, ingest, predict, and user routes.
- `configs/config.yaml` stores training and path settings.
- `models/` stores the trained model artifact.
- `tests/` contains unit tests.
- `scripts/train.py` trains the model.
- `scripts/predict.py` runs batch inference.
- `frontend/` contains the React dashboard.
- `backend/` is the Node data API used by the dashboard.

Redundant docs, sample assets, and legacy frontend files were removed so the repository stays focused on the working pipeline.

## What the system does

- Ingests smartwatch time-series data.
- Cleans and normalizes the records.
- Builds physiological features such as HRV, rolling averages, rate of change, circadian signals, activity, and sleep metrics.
- Trains a baseline risk model.
- Predicts TPP risk score, severity, and likely timeline window.
- Serves authenticated ingest, prediction, and user endpoints through FastAPI.
- Shows real-time metrics and risk trends in the dashboard.

## How To Use

### 1. Install dependencies

Python dependencies:

```powershell
C:/Program Files/Python314/python.exe -m pip install -r requirements.txt
```

Node dependencies:

```bash
npm run install:all
```

### 2. Prepare training data

The default training input file is:

- `data/processed/training_data.csv`

Your processed dataset should include at least:

- `timestamp`
- `user_id`
- `heart_rate` or `bpm`
- `steps`
- `activity_intensity`
- `sleep_duration_minutes`
- `event_severity` for supervised training

### 3. Train the model

```powershell
C:/Program Files/Python314/python.exe scripts/train.py --config configs/config.yaml
```

Outputs:

- `models/trained_model.pkl`
- `logs/training_metrics.json`

### 4. Run batch prediction

```powershell
C:/Program Files/Python314/python.exe scripts/predict.py --data data/processed/training_data.csv --artifact models/trained_model.pkl --out data/processed/predictions.csv
```

Output:

- `data/processed/predictions.csv`

### 5. Run tests

1. Open a terminal in the repository root: `c:\Users\User\OneDrive\Desktop\Thyrotoxic_Periodic_Paralysis`.
2. Activate your Python environment if you are not already using it.
3. Make sure the test dependencies are installed:

```powershell
C:/Program Files/Python314/python.exe -m pip install -r requirements.txt
```

4. Run the actual system test. This starts the real backend process, sends a real upload request, and checks the persisted data:

```powershell
C:/Program Files/Python314/python.exe -m pytest tests/test_system_backend.py -q
```

5. If you also want the unit-level checks, run the full suite after that:

```powershell
C:/Program Files/Python314/python.exe -m pytest tests -q
```

6. Run frontend dashboard tests (no smartwatch hardware required). These tests mock wearable/API responses and validate real UI behavior:

If Node is installed locally:

```bash
cd frontend
npm run test
```

If Node is not available in your local PATH, run tests with Docker instead:

```bash
docker compose run --rm --no-deps frontend sh -lc "npm install; npm run test"
```

7. Review the result. A successful run shows all requested tests passing with no failures.

### 6. Run the dashboard and Node backend

Use this when you want to run the actual frontend locally with live backend data.

From the project root:

```bash
npm start
```

URLs:

- Frontend dashboard: http://localhost:8080
- Backend API: http://localhost:3000

Without a smartwatch connected, the frontend still runs normally and can be tested using uploaded/sample backend data plus mocked frontend tests.

### 7. Run the app with Docker

Use a single Docker Compose command to start frontend, backend, and database locally:

```bash
docker compose up --build
```

This starts:

- backend API on http://localhost:3000
- frontend dashboard on http://localhost:8080
- PostgreSQL database on localhost:5432

Default database credentials:

- database: `tpp`
- user: `tpp`
- password: `tpp_dev_password`

To stop everything:

```bash
docker compose down
```

To run frontend mock tests while smartwatch hardware is unavailable:

```bash
docker compose run --rm --no-deps frontend sh -lc "npm install; npm run test"
```

If you also want the notebook environment, run the optional profile:

```bash
docker compose --profile notebook up --build
```

This adds:

- Jupyter on http://localhost:8888

### 8. Run the FastAPI service

```powershell
C:/Program Files/Python314/python.exe -m uvicorn src.ingestion_api.main:app --reload --port 8000
```

The service uses local SQLite by default so it starts without an external database.
Set `DATABASE_URL` if you want to point it at PostgreSQL or TimescaleDB instead.

API docs:

- http://localhost:8000/docs

## FastAPI Endpoints

All routes are mounted under `/api/v1`.

Authentication:

- `POST /api/v1/auth/token`

Users:

- `POST /api/v1/users`
- `GET /api/v1/users`
- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me`

Ingestion:

- `POST /api/v1/ingest`
- `POST /api/v1/ingest/stream`
- `POST /api/v1/ingest/batch`

Prediction:

- `POST /api/v1/predict`
- `POST /api/v1/predict/realtime`

## Data Flow

1. Smartwatch or uploaded data lands in `data/raw/` or is sent to the API.
2. `src/data/load_data.py` reads the source file.
3. `src/data/preprocess.py` cleans and aligns the dataframe.
4. `src/features/build_features.py` builds ML features.
5. `src/models/train.py` trains the baseline model with a time-based split.
6. `src/models/predict.py` loads the artifact and returns risk outputs.
7. `frontend/` displays metrics, charts, and alerts.

## Model Outputs

The prediction pipeline returns:

- risk score
- severity level
- predicted timeline window
- class label

Severity mapping used by the current baseline:

- `critical` if risk score is at least `0.85`
- `high` if risk score is at least `0.65`
- `moderate` if risk score is at least `0.35`
- `low` otherwise

Timeline mapping used by the current baseline:

- `critical` -> `0-3 hours`
- `high` -> `3-12 hours`
- `moderate` -> `12-24 hours`
- `low` -> `24-72 hours`

## Files Generated By The Pipeline

- `models/trained_model.pkl` is generated by training and should not be edited manually.
- `logs/training_metrics.json` stores the run summary and validation metrics.
- `data/processed/predictions.csv` stores batch inference output.

## Notes

- The current baseline model is classical ML on engineered features, which is a good starting point for small-to-medium wearable datasets.
- If you want sequence models later, the same feature/data pipeline can be extended to LSTM, Temporal CNN, or Transformer models without changing the top-level structure.
