# TPP Backend API

Backend server for Thyrotoxic Periodic Paralysis monitoring system.

## Setup

```bash
cd backend
npm install
```

## Run

```bash
npm start
```

Or for development with auto-reload:
```bash
npm run dev
```

Server runs on `http://localhost:3000`

## API Endpoints

### Health Check
```
GET /health
```

### Upload Data
```
POST /api/ingest
Content-Type: multipart/form-data
Body: file (CSV or JSON)
```

### Get All Data
```
GET /api/data
```

## File Storage

- Uploaded files are parsed and saved to `backend/data/` as JSON
- Temporary uploads stored in `backend/uploads/` (auto-cleaned)
