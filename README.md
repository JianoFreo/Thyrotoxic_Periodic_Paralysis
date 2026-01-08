# TPP Monitoring System

Full-stack application for Thyrotoxic Periodic Paralysis monitoring with smartwatch data ingestion.

## � Quick Start (Just Double-Click!)

**Windows:**
```
Double-click start.bat
```

**Or run in terminal:**
```powershell
.\start.bat
```

This opens two windows (backend + frontend). Close them when done.

**URLs:**
- Frontend: http://localhost:8080
- Backend: http://localhost:3000

---

## Docker Option (If You Have Docker Desktop Running)

```bash
docker-compose up
```

[See DOCKER.md for details](DOCKER.md)

---

## Manual Start (For Developers)
```bash
# Install dependencies
npm run install:all
npm install

# Start both frontend and backend
npm start
```

### Option 2: Using PowerShell script
```powershell
.\start.ps1
```

### Option 3: Manual start
```bash
# Terminal 1 - Backend
cd backend
npm install
npm start

# Terminal 2 - Frontend
cd frontend
# Open index.html in browser or use live-server
npx live-server --port=8080
```

## URLs
- Frontend: http://localhost:8080
- Backend API: http://localhost:3000
- Health Check: http://localhost:3000/health

## Project Structure
```
├── notebooks/         # Jupyter notebooks for data analysis
│   ├── TPP-Analysis.ipynb
│   ├── TPP-API-Integration.ipynb
│   └── TPP-ML-demo.ipynb
├── scripts/           #  Python CLI tools and utilities
│   ├── analyze_data.py      # Data analysis CLI
│   ├── upload_data.py       # API upload CLI
│   ├── generate_data.py     # Synthetic data generator
│   └── tpp_utils.py         # Shared utilities module
├── frontend/          # Vanilla JS frontend
│   ├── scripts/       # JS classes (OOP)
│   ├── styles/        # Modular CSS
│   └── index.html
├── backend/           # Node + Express API
│   ├── server.js      # Main server
│   ├── data/          # Uploaded data storage
│   └── package.json
├── sample-data/       # Test data for notebooks and uploads
├── requirements.txt   # Python dependencies
└── package.json       # Root scripts
```
