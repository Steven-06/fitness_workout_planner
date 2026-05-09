@echo off
REM Run Server Script for Fitness Tracker (Windows)
REM This script starts MongoDB, the FastAPI backend, and the Streamlit frontend.

setlocal enabledelayedexpansion

echo ==========================================
echo Fitness Tracker - Full Stack Startup
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
cd /d "%~dp0"

echo.
echo 📦 Installing dependencies...

REM Install backend dependencies
cd backend
echo   Installing backend packages...
python -m pip install --quiet -r requirements.txt
echo ✓ Backend dependencies ready
cd ..

REM Install frontend dependencies
cd frontend
echo   Installing frontend packages (Streamlit - this may take 1-2 minutes)...
python -m pip install --quiet -r requirements.txt
echo ✓ Frontend dependencies ready
cd ..

REM Set MongoDB connection string
set MONGODB_URL=mongodb://admin:admin@localhost:27017/fitness_tracker?authSource=admin

echo.
echo ==========================================
echo 🚀 Starting Fitness Tracker Services
echo ==========================================
echo.
echo 📍 Backend API: http://127.0.0.1:8000
echo 📚 API Documentation: http://127.0.0.1:8000/docs
echo 💻 Frontend UI: http://127.0.0.1:8501
echo.
echo Starting Streamlit frontend on port 8501...
start "" python -m streamlit run frontend\app.py --server.port=8501 --logger.level=warning

timeout /t 3 /nobreak >nul

echo.
echo Starting FastAPI backend on port 8000...
echo.
echo ⚡ Both services are now running!
echo    - Backend: http://127.0.0.1:8000
echo    - Frontend: http://127.0.0.1:8501
echo.
echo Press Ctrl+C in both windows to stop all services
echo.

cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
