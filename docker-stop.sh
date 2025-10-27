#!/bin/bash

# VELOX Docker Stack Stop Script

set -e

echo "======================================================================"
echo "Stopping VELOX Docker Stack..."
echo "======================================================================"

# Stop all services
docker compose down

echo ""
echo "✅ All services stopped"
echo ""
echo "To remove volumes (WARNING: This will delete all data):"
echo "  docker compose down -v"
echo ""
