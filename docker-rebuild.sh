#!/bin/bash

# VELOX Docker Stack Rebuild Script

set -e

echo "======================================================================"
echo "Rebuilding VELOX Docker Stack..."
echo "======================================================================"

# Stop all services
echo ""
echo "Stopping services..."
docker compose down

# Remove old velox-api image to force rebuild
echo ""
echo "Removing old velox-api image..."
docker rmi velox-n8n-velox-api 2>/dev/null || echo "Image not found, skipping..."

# Rebuild VELOX API
echo ""
echo "Building VELOX API..."
docker compose build --no-cache velox-api

# Start services
echo ""
echo "Starting services..."
docker compose up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to start..."
sleep 10

# Check service status
echo ""
echo "======================================================================"
echo "SERVICE STATUS"
echo "======================================================================"
docker compose ps

# Display access information
echo ""
echo "======================================================================"
echo "✅ VELOX STACK REBUILT SUCCESSFULLY!"
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
echo "📝 Check the updated API docs at http://localhost:8000/docs"
echo "   You should now see all 77 indicators!"
echo ""
echo "======================================================================"
