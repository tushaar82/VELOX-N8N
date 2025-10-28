#!/bin/bash

echo "======================================================================"
echo "VELOX - OpenAlgo Host Configuration Fix"
echo "======================================================================"
echo ""

# Check if OpenAlgo is running
OPENALGO_PID=$(pgrep -f "python.*app.py" | head -1)

if [ -n "$OPENALGO_PID" ]; then
    echo "Found OpenAlgo running with PID: $OPENALGO_PID"
    echo "Stopping OpenAlgo..."
    kill $OPENALGO_PID
    sleep 2
    
    # Force kill if still running
    if pgrep -f "python.*app.py" > /dev/null; then
        echo "Force stopping OpenAlgo..."
        pkill -9 -f "python.*app.py"
    fi
else
    echo "OpenAlgo is not currently running"
fi

echo ""
echo "Starting OpenAlgo on all interfaces (0.0.0.0:5000)..."
echo ""

# Find OpenAlgo directory
OPENALGO_DIR=""
if [ -d "./openalgo" ]; then
    OPENALGO_DIR="./openalgo"
elif [ -d "../openalgo" ]; then
    OPENALGO_DIR="../openalgo"
elif [ -d "$HOME/openalgo" ]; then
    OPENALGO_DIR="$HOME/openalgo"
else
    echo "Error: OpenAlgo directory not found!"
    echo "Please ensure OpenAlgo is cloned in one of these locations:"
    echo "  - ./openalgo"
    echo "  - ../openalgo"
    echo "  - ~/openalgo"
    exit 1
fi

echo "Using OpenAlgo directory: $OPENALGO_DIR"
cd "$OPENALGO_DIR"

# Create a script to run OpenAlgo on all interfaces
cat > run_host.py << 'EOF'
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    
    # Configure to run on all interfaces
    print("="*60)
    print("OpenAlgo - Starting on all interfaces")
    print("="*60)
    print("Host: 0.0.0.0")
    print("Port: 5000")
    print("API: http://0.0.0.0:5000")
    print("Local: http://localhost:5000")
    print("="*60)
    
    # Run with host='0.0.0.0' to accept connections from any interface
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
    
except ImportError as e:
    print(f"Error importing OpenAlgo app: {e}")
    print("Make sure you're in the correct OpenAlgo directory")
    sys.exit(1)
except Exception as e:
    print(f"Error starting OpenAlgo: {e}")
    sys.exit(1)
EOF

echo "Starting OpenAlgo with host configuration..."
nohup python3 run_host.py > openalgo.log 2>&1 &
OPENALGO_NEW_PID=$!

echo ""
echo "OpenAlgo started with PID: $OPENALGO_NEW_PID"
echo "Log file: $OPENALGO_DIR/openalgo.log"
echo ""

# Wait a moment and check if it's running
sleep 3

if ps -p $OPENALGO_NEW_PID > /dev/null; then
    echo "✅ OpenAlgo is running successfully!"
    echo ""
    echo "Testing connectivity..."
    
    # Test localhost
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo "✅ Localhost connection: OK"
    else
        echo "⚠️  Localhost connection: Failed"
    fi
    
    # Test 0.0.0.0 (from container perspective)
    if curl -s http://0.0.0.0:5000/health > /dev/null 2>&1; then
        echo "✅ All interfaces connection: OK"
    else
        echo "⚠️  All interfaces connection: Failed"
    fi
    
    echo ""
    echo "OpenAlgo is now accessible from Docker containers!"
    echo "API endpoints:"
    echo "  - Local: http://localhost:5000"
    echo "  - Docker: http://0.0.0.0:5000"
    echo ""
    echo "To view logs: tail -f $OPENALGO_DIR/openalgo.log"
    echo ""
    echo "To stop: kill $OPENALGO_NEW_PID"
else
    echo "❌ Failed to start OpenAlgo!"
    echo "Check logs: cat $OPENALGO_DIR/openalgo.log"
    exit 1
fi

echo ""
echo "======================================================================"