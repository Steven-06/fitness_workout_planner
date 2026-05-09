#!/bin/bash

# Run Server Script for Fitness Tracker
# This script starts MongoDB, the FastAPI backend, and the Streamlit frontend.

set -e

echo "=========================================="
echo "Fitness Tracker - Full Stack Startup"
echo "=========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker to continue."
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker and try again."
    exit 1
fi

# Start MongoDB container
echo ""
echo "🍃 Starting MongoDB in Docker..."
MONGO_CONTAINER_NAME="fitness_tracker_mongodb"

# Check if MongoDB container already exists
if docker ps -a --format '{{.Names}}' | grep -q "^${MONGO_CONTAINER_NAME}$"; then
    echo "✓ MongoDB container exists. Starting..."
    docker start "$MONGO_CONTAINER_NAME" 2>/dev/null || true
else
    echo "✓ Creating new MongoDB container..."
    docker run -d \
        --name "$MONGO_CONTAINER_NAME" \
        -p 27017:27017 \
        -e MONGO_INITDB_ROOT_USERNAME=admin \
        -e MONGO_INITDB_ROOT_PASSWORD=admin \
        mongo:7.0 \
        --auth
fi

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
for i in {1..30}; do
    if docker exec "$MONGO_CONTAINER_NAME" mongosh --eval "db.adminCommand('ping')" &>/dev/null; then
        echo "✓ MongoDB is ready!"
        break
    fi
    echo "⏳ Waiting for MongoDB... ($i/30)"
    sleep 1
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "📦 Installing dependencies..."

# Install backend dependencies
cd "$SCRIPT_DIR/backend"
pip install -q -r requirements.txt 2>/dev/null
echo "✓ Backend dependencies ready"

# Install frontend dependencies
cd "$SCRIPT_DIR/frontend"
pip install -q -r requirements.txt 2>/dev/null
echo "✓ Frontend dependencies ready"

# Set MongoDB connection string
export MONGODB_URL="mongodb://admin:admin@localhost:27017/fitness_tracker?authSource=admin"

echo ""
echo "=========================================="
echo "🚀 Starting Fitness Tracker Services"
echo "=========================================="
echo ""
echo "📍 Backend API: http://127.0.0.1:8000"
echo "📚 API Documentation: http://127.0.0.1:8000/docs"
echo "💻 Frontend UI: http://127.0.0.1:8501"
echo ""

# Start Streamlit frontend in background
echo "Starting Streamlit frontend on port 8501..."
streamlit run "$SCRIPT_DIR/frontend/app.py" --server.port=8501 --logger.level=warning &
FRONTEND_PID=$!

sleep 3

echo ""
echo "Starting FastAPI backend on port 8000..."
echo ""
echo "⚡ Both services are now running!"
echo "   - Backend: http://127.0.0.1:8000"
echo "   - Frontend: http://127.0.0.1:8501"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Start the FastAPI server (foreground)
cd "$SCRIPT_DIR/backend"
trap "kill $FRONTEND_PID 2>/dev/null; exit" EXIT INT TERM
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo ""
echo "✓ All services stopped"
