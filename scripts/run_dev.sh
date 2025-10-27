#!/bin/bash

# Development server runner for VELOX
# Runs FastAPI in development mode with auto-reload

set -e

echo "================================================"
echo "  VELOX Development Server"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run ./scripts/setup.sh first"
    exit 1
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "   Creating from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  Please edit .env and add your OpenAlgo API key before continuing"
    echo "   Press Ctrl+C to exit and edit .env, or Enter to continue anyway"
    read
fi

# Check if app/main.py exists
if [ ! -f "app/main.py" ]; then
    echo "❌ app/main.py not found!"
    echo "   The application code hasn't been implemented yet."
    echo "   Please complete Phase 2 and beyond."
    exit 1
fi

echo "🚀 Starting development server..."
echo ""
echo "📍 Server will be available at:"
echo "   - Local:   http://localhost:8000"
echo "   - Network: http://0.0.0.0:8000"
echo ""
echo "📚 API Documentation:"
echo "   - Swagger UI: http://localhost:8000/docs"
echo "   - ReDoc:      http://localhost:8000/redoc"
echo ""
echo "⌨️  Press Ctrl+C to stop the server"
echo ""
echo "================================================"
echo ""

# Run FastAPI in development mode with auto-reload
fastapi dev app/main.py --host 0.0.0.0 --port 8000
