@echo off
REM Run Server Script for Fitness Tracker (Windows)
REM This script starts MongoDB in Docker and runs the FastAPI backend server.

setlocal enabledelayedexpansion

echo ==========================================
echo Fitness Tracker Server Startup Script
echo ==========================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop and try again.
    pause
    exit /b 1
)

REM Check if Docker daemon is running
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker daemon is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Start MongoDB container
echo.
echo 🍃 Starting MongoDB in Docker...
set MONGO_CONTAINER_NAME=fitness_tracker_mongodb

REM Check if MongoDB container exists
docker ps -a --format "{{.Names}}" | findstr /R "^%MONGO_CONTAINER_NAME%$" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ MongoDB container exists. Starting...
    docker start %MONGO_CONTAINER_NAME% >nul 2>&1
) else (
    echo ✓ Creating new MongoDB container...
    docker run -d ^
        --name %MONGO_CONTAINER_NAME% ^
        -p 27017:27017 ^
        -e MONGO_INITDB_ROOT_USERNAME=admin ^
        -e MONGO_INITDB_ROOT_PASSWORD=admin ^
        mongo:7.0 ^
        --auth
)

REM Wait for MongoDB to be ready
echo ⏳ Waiting for MongoDB to be ready...
set /A count=0
:wait_mongo
docker exec %MONGO_CONTAINER_NAME% mongosh --eval "db.adminCommand('ping')" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ MongoDB is ready!
    goto mongo_ready
)
set /A count=!count!+1
if !count! geq 30 (
    echo ⚠️  MongoDB took too long to start. Continuing anyway...
    goto mongo_ready
)
echo ⏳ Waiting for MongoDB... (!count!/30)
timeout /t 1 /nobreak >nul
goto wait_mongo

:mongo_ready
REM Navigate to backend directory
cd /d "%~dp0backend"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to navigate to backend directory
    pause
    exit /b 1
)

echo.
echo 📦 Installing Python dependencies...
set "VENV_PY=%~dp0venv\Scripts\python.exe"
if exist "%VENV_PY%" (
    echo Using venv python: "%VENV_PY%"
    "%VENV_PY%" -m pip install --disable-pip-version-check --no-input -r ..\requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install from repo root; trying backend requirements
        "%VENV_PY%" -m pip install --disable-pip-version-check --no-input -r requirements.txt
    )
    echo ✓ Dependencies installation finished
) else (
    echo venv python not found; falling back to system pip
    pip install --disable-pip-version-check --no-input -r ..\requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        pip install --disable-pip-version-check --no-input -r requirements.txt
    )
    echo ✓ Dependencies installation finished
)

REM Set MongoDB connection string
set MONGODB_URL=mongodb://admin:admin@localhost:27017/fitness_tracker?authSource=admin

echo.
echo ==========================================
echo 🚀 Starting Fitness Tracker API Server
echo ==========================================
echo.
echo 📍 Server running at: http://127.0.0.1:8000
echo 📚 API docs at: http://127.0.0.1:8000/docs
echo 🔍 ReDoc at: http://127.0.0.1:8000/redoc
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the FastAPI server
REM Start Streamlit frontend in a new window (if venv exists)
if exist "%VENV_PY%" (
    echo Starting Streamlit in this terminal
    start "" /b "%VENV_PY%" -m streamlit run ..\frontend\app.py --server.port=8501 --server.headless true
) else (
    echo Starting Streamlit in this terminal
    start "" /b streamlit run ..\frontend\app.py --server.port=8501 --server.headless true
)

REM Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo Server stopped.
pause
