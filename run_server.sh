#!/bin/bash

# Run Server Script for Fitness Tracker
# This script starts MongoDB in Docker and runs the FastAPI backend server.

set -e

echo "=========================================="
echo "Fitness Tracker Server Startup Script"
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

# Check if we're in the backend directory
cd "$(dirname "$0")/backend" || exit 1

echo ""
echo "📦 Installing Python dependencies..."
# Prefer using the project's venv python when available
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PY="$SCRIPT_DIR/venv/bin/python"
if [ -x "$VENV_PY" ]; then
    echo "Using venv python: $VENV_PY"
    "$VENV_PY" -m pip install --disable-pip-version-check --no-input -r "$SCRIPT_DIR/requirements.txt" || {
        echo "Install from repo root failed; trying backend requirements"
        "$VENV_PY" -m pip install --disable-pip-version-check --no-input -r "$SCRIPT_DIR/backend/requirements.txt"
    }
    echo "✓ Dependencies installation finished (venv)"
elif [ -f "../requirements.txt" ]; then
    pip install --disable-pip-version-check --no-input -r ../requirements.txt
    echo "✓ Dependencies installed (from repo root)"
elif [ -f "requirements.txt" ]; then
    pip install --disable-pip-version-check --no-input -r requirements.txt
    echo "✓ Dependencies installed (from backend folder)"
else
    echo "⚠️  requirements.txt not found (checked repo root and backend)"
fi

# Set MongoDB connection string
export MONGODB_URL="mongodb://admin:admin@localhost:27017/fitness_tracker?authSource=admin"

echo ""
echo "=========================================="
echo "🚀 Starting Fitness Tracker API Server"
echo "=========================================="
echo ""
echo "📍 Server running at: http://127.0.0.1:8000"
echo "📚 API docs at: http://127.0.0.1:8000/docs"
echo "� ReDoc at: http://127.0.0.1:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
# Start Streamlit frontend in background (use venv python if available)
FRONTEND_PATH="$SCRIPT_DIR/../frontend/app.py"
if [ -x "$VENV_PY" ]; then
    echo "Starting Streamlit (venv) on port 8501..."
    "$VENV_PY" -m streamlit run "$SCRIPT_DIR/../frontend/app.py" --server.port=8501 --server.headless true &
else
    echo "Starting Streamlit (system) on port 8501..."
    streamlit run "$SCRIPT_DIR/../frontend/app.py" --server.port=8501 --server.headless true &
fi

# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo "📍 Frontend running at: http://127.0.0.1:8501"
echo ""
echo "Server stopped."
