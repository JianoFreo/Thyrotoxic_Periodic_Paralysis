@echo off
echo Starting TPP Monitoring System...
echo.

REM Start backend in background
start "TPP Backend" cmd /k "cd backend && npm install && npm start"

REM Wait 2 seconds
timeout /t 2 /nobreak > nul

REM Start frontend in background
start "TPP Frontend" cmd /k "cd frontend && npx live-server --port=8080"

echo.
echo ========================================
echo   TPP Monitoring System Started!
echo ========================================
echo   Frontend: http://localhost:8080
echo   Backend:  http://localhost:3000
echo ========================================
echo.
echo Close both terminal windows to stop.
echo.
