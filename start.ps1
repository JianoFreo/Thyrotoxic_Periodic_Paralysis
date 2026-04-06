# Start both frontend and backend
Write-Host "Starting TPP Monitoring System..." -ForegroundColor Cyan

# Start backend in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; npm start"

# Wait a moment for backend to start
Start-Sleep -Seconds 2

# Start frontend (Live Server or open in browser)
Write-Host "Opening frontend..." -ForegroundColor Green
Start-Process "http://localhost:8080" 
cd "$PSScriptRoot\frontend"
npx live-server --port=8080 --entry-file=index.html

Write-Host "System running!" -ForegroundColor Green
Write-Host "Backend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:8080" -ForegroundColor Yellow
