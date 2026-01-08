# TPP Monitoring System

Full-stack application for Thyrotoxic Periodic Paralysis monitoring with smartwatch data ingestion.


### Option 1: Using npm (recommended)
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
├── notebooks/         # Jupyter notebooks (primary interface)
│   ├── TPP-ML-demo.ipynb
│   ├── TPP-Analysis.ipynb
│   └── TPP-API-Integration.ipynb
├── frontend/          # Vanilla JS frontend
│   ├── scripts/       # JS classes (OOP)
│   ├── styles/        # Modular CSS
│   └── index.html
├── backend/           # Node + Express API
│   ├── server.js      # Main server
│   ├── data/          # Uploaded data storage
│   └── package.json
├── sample-data/       # Test data for notebooks and uploads
├── requirements.txt   # Python dependencies for Jupyter
└── package.json       # Root scripts
```
