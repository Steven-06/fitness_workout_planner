# Run Server Script for Fitness Tracker (PowerShell)
# This script starts MongoDB, the FastAPI backend, and the Streamlit frontend.

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Fitness Tracker — Full Stack Startup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if Docker is installed
try {
    docker --version | Out-Null
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Check if Docker daemon is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker daemon is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Start MongoDB container
Write-Host ""
Write-Host "🍃 Starting MongoDB in Docker..." -ForegroundColor Yellow

$mongoContainerName = "fitness_tracker_mongodb"

# Check if MongoDB container exists
$containerExists = docker ps -a --format "{{.Names}}" | Select-String "^$mongoContainerName`$"

if ($containerExists) {
    Write-Host "✓ MongoDB container exists. Starting..." -ForegroundColor Green
    docker start $mongoContainerName 2>$null | Out-Null
} else {
    Write-Host "✓ Creating new MongoDB container..." -ForegroundColor Green
    docker run -d `
        --name $mongoContainerName `
        -p 27017:27017 `
        -e MONGO_INITDB_ROOT_USERNAME=admin `
        -e MONGO_INITDB_ROOT_PASSWORD=admin `
        mongo:7.0 `
        --auth
}

# Wait for MongoDB to be ready
Write-Host "⏳ Waiting for MongoDB to be ready..." -ForegroundColor Yellow

$count = 0
$maxAttempts = 30

while ($count -lt $maxAttempts) {
    try {
        docker exec $mongoContainerName mongosh --eval "db.adminCommand('ping')" 2>$null | Out-Null
        Write-Host "✓ MongoDB is ready!" -ForegroundColor Green
        break
    } catch {
        $count++
        if ($count -ge $maxAttempts) {
            Write-Host "⚠️  MongoDB took too long to start. Continuing anyway..." -ForegroundColor Yellow
            break
        }
        Write-Host "⏳ Waiting for MongoDB... ($count/$maxAttempts)" -ForegroundColor Yellow
        Start-Sleep -Seconds 1
    }
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $scriptDir "venv\Scripts\python.exe"

Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow

# Install backend dependencies
Push-Location (Join-Path $scriptDir "backend")
Write-Host "  Installing backend packages..." -ForegroundColor Cyan
if (Test-Path $venvPython) {
    & $venvPython -m pip install --quiet -r requirements.txt 2>&1 | Out-Null
} else {
    pip install --quiet -r requirements.txt 2>&1 | Out-Null
}
Write-Host "✓ Backend dependencies ready" -ForegroundColor Green
Pop-Location

# Install frontend dependencies
Push-Location (Join-Path $scriptDir "frontend")
Write-Host "  Installing frontend packages (Streamlit - this may take 1-2 minutes)..." -ForegroundColor Cyan
if (Test-Path $venvPython) {
    & $venvPython -m pip install --quiet -r requirements.txt 2>&1 | Out-Null
} else {
    pip install --quiet -r requirements.txt 2>&1 | Out-Null
}
Write-Host "✓ Frontend dependencies ready" -ForegroundColor Green
Pop-Location

# Set MongoDB connection string
$env:MONGODB_URL = "mongodb://admin:admin@localhost:27017/fitness_tracker?authSource=admin"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Starting Fitness Tracker Services" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Backend API: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "📚 API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "💻 Frontend UI: http://127.0.0.1:8501" -ForegroundColor Green
Write-Host ""

# Start Streamlit frontend in background
Write-Host "Starting Streamlit frontend on port 8501..." -ForegroundColor Yellow
$frontendScript = Join-Path $scriptDir "frontend\app.py"
$frontendJob = Start-Process -FilePath $venvPython `
    -ArgumentList '-m','streamlit','run',$frontendScript,'--server.port=8501','--logger.level=warning' `
    -WorkingDirectory (Join-Path $scriptDir "frontend") `
    -PassThru `
    -NoNewWindow
Write-Host "✓ Frontend started (PID: $($frontendJob.Id))" -ForegroundColor Green

# Give frontend time to start
Start-Sleep -Seconds 3

# Start FastAPI backend (foreground - this blocks the script)
Write-Host ""
Write-Host "Starting FastAPI backend on port 8000..." -ForegroundColor Yellow
Write-Host ""
Write-Host "⚡ Both services are now running!" -ForegroundColor Cyan
Write-Host "   - Backend: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "   - Frontend: http://127.0.0.1:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

Push-Location (Join-Path $scriptDir "backend")
try {
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
} finally {
    Write-Host ""
    Write-Host "Stopping frontend process..." -ForegroundColor Yellow
    Stop-Process -Id $frontendJob.Id -ErrorAction SilentlyContinue
    Write-Host "✓ All services stopped" -ForegroundColor Green
    Pop-Location
}

