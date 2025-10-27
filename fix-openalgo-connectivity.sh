#!/bin/bash

echo "======================================================================"
echo "VELOX - OpenAlgo Connectivity Fix"
echo "======================================================================"
echo ""

echo "Current OpenAlgo Status:"
echo "------------------------"
lsof -i :5000 | grep LISTEN || echo "OpenAlgo not running on port 5000"
echo ""

echo "Issue: OpenAlgo is listening on localhost (127.0.0.1) only."
echo "Docker containers cannot reach it."
echo ""

echo "Solutions:"
echo "----------"
echo ""
echo "Option 1: Use Host Network Mode (Quickest)"
echo "   Modify docker-compose.yml to use network_mode: host"
echo "   This removes network isolation but allows direct localhost access"
echo ""
echo "Option 2: Run OpenAlgo on All Interfaces"
echo "   Make OpenAlgo listen on 0.0.0.0 instead of 127.0.0.1"
echo "   This requires modifying OpenAlgo's startup configuration"
echo ""
echo "Option 3: Run OpenAlgo in Docker"
echo "   Add OpenAlgo as a Docker service in docker-compose.yml"
echo "   This provides proper network isolation"
echo ""

read -p "Would you like to apply Option 1 (host network mode)? (y/n): " choice

if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
    echo ""
    echo "Applying host network mode..."
    
    # Backup docker-compose.yml
    cp docker-compose.yml docker-compose.yml.backup
    echo "✅ Backed up docker-compose.yml"
    
    # Update docker-compose.yml to use host network
    cat > /tmp/velox-api-host-network.yml << 'EOF'
  # VELOX API - Real-Time Technical Analysis
  velox-api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: velox-api
    restart: unless-stopped
    network_mode: "host"
    environment:
      - OPENALGO_API_KEY=${OPENALGO_API_KEY}
      - OPENALGO_HOST=${OPENALGO_HOST:-http://localhost:5000}
      - OPENALGO_VERSION=${OPENALGO_VERSION:-v1}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - CORS_ORIGINS=http://localhost:3000,http://localhost:5678,http://localhost:1880,http://localhost:3001
      - MAX_WEBSOCKET_CONNECTIONS=${MAX_WEBSOCKET_CONNECTIONS:-100}
      - TICK_BUFFER_SIZE=${TICK_BUFFER_SIZE:-1000}
      - DEFAULT_TIMEFRAMES=${DEFAULT_TIMEFRAMES:-1m,5m,15m,1h,1d}
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
EOF
    
    echo ""
    echo "⚠️  Manual Step Required:"
    echo "   Please update docker-compose.yml velox-api service to use network_mode: host"
    echo "   A backup has been saved to docker-compose.yml.backup"
    echo ""
    echo "   After updating, restart the container:"
    echo "   docker compose stop velox-api && docker compose rm -f velox-api && docker compose up -d velox-api"
    echo ""
else
    echo ""
    echo "No changes made."
    echo ""
    echo "Please refer to ENDPOINT-STATUS-REPORT.md for detailed solutions."
fi

echo ""
echo "======================================================================"
