#!/bin/bash

# VELOX Docker Stack Startup Script

set -e

echo "======================================================================"
echo "VELOX Real-Time Technical Analysis System - Docker Stack"
echo "======================================================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your configuration before continuing!"
    echo "   Especially set: OPENALGO_API_KEY, N8N_PASSWORD, GRAFANA_PASSWORD"
    echo ""
    read -p "Press Enter to continue after editing .env file..."
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p logs
mkdir -p n8n-workflows
mkdir -p node-red-flows
mkdir -p grafana/provisioning/datasources
mkdir -p grafana/provisioning/dashboards
mkdir -p grafana/dashboards

echo "✅ Directories created"

# Create Grafana datasource configuration
echo ""
echo "Creating Grafana datasource configuration..."
cat > grafana/provisioning/datasources/velox-api.yml << 'EOF'
apiVersion: 1

datasources:
  - name: VELOX API
    type: grafana-simple-json-datasource
    access: proxy
    url: http://velox-api:8000
    isDefault: false
    editable: true
    jsonData:
      httpMethod: GET
EOF

echo "✅ Grafana datasource configured"

# Create Grafana dashboard provisioning
cat > grafana/provisioning/dashboards/dashboard.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'VELOX Dashboards'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOF

echo "✅ Grafana dashboard provisioning configured"

# Pull latest images
echo ""
echo "Pulling Docker images..."
docker-compose pull

# Build VELOX API
echo ""
echo "Building VELOX API..."
docker-compose build velox-api

# Start services
echo ""
echo "Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to start..."
sleep 10

# Check service status
echo ""
echo "======================================================================"
echo "SERVICE STATUS"
echo "======================================================================"
docker-compose ps

# Display access information
echo ""
echo "======================================================================"
echo "✅ VELOX STACK STARTED SUCCESSFULLY!"
echo "======================================================================"
echo ""
echo "📊 Access URLs:"
echo "  VELOX API:      http://localhost:8000"
echo "  API Docs:       http://localhost:8000/docs"
echo "  n8n:            http://localhost:5678"
echo "  Node-RED:       http://localhost:1880"
echo "  Grafana:        http://localhost:3001"
echo ""
echo "🔐 Default Credentials (change in .env):"
echo "  n8n:            admin / changeme123"
echo "  Grafana:        admin / changeme123"
echo ""
echo "📝 Logs:"
echo "  View all:       docker-compose logs -f"
echo "  VELOX API:      docker-compose logs -f velox-api"
echo "  n8n:            docker-compose logs -f n8n"
echo "  Node-RED:       docker-compose logs -f node-red"
echo "  Grafana:        docker-compose logs -f grafana"
echo ""
echo "🛑 Stop services:"
echo "  docker-compose down"
echo ""
echo "======================================================================"
