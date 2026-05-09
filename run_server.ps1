# Run Server Script for Fitness Tracker (PowerShell)
# This script starts MongoDB in Docker and runs the FastAPI backend server.

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Fitness Tracker Server Startup Script" -ForegroundColor Cyan
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

# Navigate to backend directory
Push-Location (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "backend")

Write-Host ""
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow

if (Test-Path "requirements.txt") {
    pip install -q -r requirements.txt
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  requirements.txt not found in backend directory" -ForegroundColor Yellow
}

# Set MongoDB connection string
$env:MONGODB_URL = "mongodb://admin:admin@localhost:27017/fitness_tracker?authSource=admin"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Starting Fitness Tracker API Server" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Server running at: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "📚 API docs at: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "🔍 ReDoc at: http://127.0.0.1:8000/redoc" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Write-Host ""
Write-Host "Server stopped." -ForegroundColor Yellow

Pop-Location
