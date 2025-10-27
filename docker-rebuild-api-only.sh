#!/bin/bash

# VELOX API Quick Rebuild Script (keeps other services running)

set -e

echo "======================================================================"
echo "Rebuilding VELOX API only..."
echo "======================================================================"

# Stop only velox-api service
echo ""
echo "Stopping velox-api..."
docker compose stop velox-api

# Remove old velox-api container
echo ""
echo "Removing old container..."
docker compose rm -f velox-api

# Rebuild VELOX API
echo ""
echo "Building VELOX API..."
docker compose build --no-cache velox-api

# Start velox-api service
echo ""
echo "Starting velox-api..."
docker compose up -d velox-api

# Wait for service to be healthy
echo ""
echo "Waiting for service to start..."
sleep 10

# Check service status
echo ""
echo "======================================================================"
echo "SERVICE STATUS"
echo "======================================================================"
docker compose ps velox-api

# Display access information
echo ""
echo "======================================================================"
echo "✅ VELOX API REBUILT SUCCESSFULLY!"
echo "======================================================================"
echo ""
echo "📊 Access URLs:"
echo "  VELOX API:      http://localhost:8000"
echo "  API Docs:       http://localhost:8000/docs"
echo ""
echo "📝 Check the updated API docs at http://localhost:8000/docs"
echo "   You should now see all 77 indicators across 4 endpoints!"
echo ""
echo "======================================================================"
