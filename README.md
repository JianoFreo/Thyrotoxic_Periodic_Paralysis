# TPP Hyphertyrodism AI Data System

Full-stack AI deeplearning software for Thyrotoxic Periodic Paralysis monitoring with smartwatch data ingestion. This is to monitor the behavior of your body that predicts the severity and timeline of TPP attacks. It also advises you when to take your Propranolol and Thiamazole tablets and how you would prepare for the attack. It was initially designed for me as I suffered from sa same condition back in early 2024 but as of 2025, I already fully recovered so I didn't get to use it LMAO, still working on it tho.

## Quick Start (Just Double-Click!)

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

