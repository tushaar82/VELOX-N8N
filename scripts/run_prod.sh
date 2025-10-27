#!/bin/bash

# Production server runner for VELOX
# Runs FastAPI in production mode with multiple workers

set -e

echo "================================================"
echo "  VELOX Production Server"
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
    echo "❌ .env file not found!"
    echo "   Please create .env file with proper configuration"
    exit 1
fi

# Check if app/main.py exists
if [ ! -f "app/main.py" ]; then
    echo "❌ app/main.py not found!"
    echo "   The application code hasn't been implemented yet."
    exit 1
fi

# Load environment variables
source .env

# Set defaults if not specified
HOST=${APP_HOST:-0.0.0.0}
PORT=${APP_PORT:-8000}
WORKERS=${APP_WORKERS:-4}

echo "🚀 Starting production server..."
echo ""
echo "⚙️  Configuration:"
echo "   - Host:    $HOST"
echo "   - Port:    $PORT"
echo "   - Workers: $WORKERS"
echo ""
echo "📍 Server will be available at:"
echo "   - http://$HOST:$PORT"
echo ""
echo "📚 API Documentation:"
echo "   - Swagger UI: http://localhost:$PORT/docs"
echo "   - ReDoc:      http://localhost:$PORT/redoc"
echo ""
echo "⌨️  Press Ctrl+C to stop the server"
echo ""
echo "================================================"
echo ""

# Run FastAPI in production mode
fastapi run app/main.py --host $HOST --port $PORT --workers $WORKERS
