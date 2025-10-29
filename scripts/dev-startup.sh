#!/bin/bash

# VELOX-N8N Development Startup Script
# This script sets up the development environment and starts all services

set -e

echo "🚀 Starting VELOX-N8N Development Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to check if a service is healthy
check_service_health() {
    local service_name=$1
    local container_name=$2
    local health_url=$3
    
    echo "🔍 Checking $service_name health..."
    
    # Wait for service to be ready
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec $container_name curl -f $health_url > /dev/null 2>&1; then
            echo "✅ $service_name is healthy"
            return 0
        fi
        
        echo "⏳ Waiting for $service_name to be ready... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to become healthy after $max_attempts attempts"
    return 1
}

# Function to start a service
start_service() {
    local service_name=$1
    local compose_service=$2
    
    echo "🔄 Starting $service_name..."
    docker-compose -f docker-compose.dev.yml up -d $compose_service
    
    if [ $? -eq 0 ]; then
        echo "✅ $service_name started successfully"
    else
        echo "❌ Failed to start $service_name"
        return 1
    fi
    
    return 0
}

# Function to stop a service
stop_service() {
    local service_name=$1
    local compose_service=$2
    
    echo "🔄 Stopping $service_name..."
    docker-compose -f docker-compose.dev.yml stop $compose_service
    
    if [ $? -eq 0 ]; then
        echo "✅ $service_name stopped successfully"
    else
        echo "❌ Failed to stop $service_name"
        return 1
    fi
    
    return 0
}

# Function to show logs
show_logs() {
    local service_name=$1
    local container_name=$2
    
    echo "📋 Showing logs for $service_name..."
    docker-compose -f docker-compose.dev.yml logs -f --tail=100 $container_name
}

# Function to show status
show_status() {
    echo "📊 Service Status:"
    echo "=================="
    
    # Check each service
    services=("postgres" "redis" "fastapi" "n8n" "frontend" "grafana" "openalgo")
    
    for service in "${services[@]}"; do
        if docker ps --filter "name=velo_${service}_dev" --format "table {{.Names}}\t" | grep -q velo_${service}_dev; then
            status="🟢 Running"
        else
            status="🔴 Stopped"
        fi
        
        echo "$service: $status"
    done
    
    echo "=================="
}

# Function to clean up
cleanup() {
    echo "🧹 Cleaning up..."
    
    # Stop all services
    docker-compose -f docker-compose.dev.yml down
    
    # Remove dangling containers
    docker container prune -f
    
    # Remove unused images
    docker image prune -f
    
    # Clean up logs
    rm -rf logs/*
    
    echo "✅ Cleanup completed"
}

# Function to reset database
reset_database() {
    echo "🔄 Resetting database..."
    
    # Stop services
    docker-compose -f docker-compose.dev.yml stop postgres
    
    # Remove database volume
    docker volume rm velo_postgres_dev_data
    
    # Start services
    docker-compose -f docker-compose.dev.yml up -d postgres
    
    echo "✅ Database reset completed"
}

# Function to install dependencies
install_dependencies() {
    echo "📦 Installing dependencies..."
    
    # Backend dependencies
    echo "Installing backend dependencies..."
    cd backend/fastapi
    pip install -r requirements.txt
    
    # Frontend dependencies
    echo "Installing frontend dependencies..."
    cd ../frontend
    npm install
    
    cd ../..
    
    echo "✅ Dependencies installed"
}

# Function to run tests
run_tests() {
    echo "🧪 Running tests..."
    
    # Backend tests
    echo "Running backend tests..."
    cd backend/fastapi
    pytest
    
    # Frontend tests
    echo "Running frontend tests..."
    cd ../frontend
    npm test
    
    cd ../..
    
    echo "✅ Tests completed"
}

# Function to build for production
build_production() {
    echo "🏗 Building for production..."
    
    # Build backend
    echo "Building backend..."
    cd backend/fastapi
    docker build -t velo-fastapi:latest .
    
    # Build frontend
    echo "Building frontend..."
    cd ../frontend
    npm run build
    
    cd ../..
    
    echo "✅ Build completed"
}

# Function to deploy to production
deploy_production() {
    echo "🚀 Deploying to production..."
    
    # This would typically involve:
    # 1. Pushing images to registry
    # 2. Updating production environment
    # 3. Running production compose file
    
    echo "✅ Deployment completed"
}

# Main script logic
case "${1:-help}" in
    "start")
        echo "🚀 Starting all services..."
        
        # Start infrastructure services first
        start_service "PostgreSQL" postgres
        start_service "Redis" redis
        start_service "OpenAlgo" openalgo
        
        # Wait for infrastructure to be ready
        echo "⏳ Waiting for infrastructure services to be ready..."
        sleep 10
        
        # Start application services
        start_service "FastAPI" fastapi
        start_service "N8N" n8n
        start_service "Frontend" frontend
        start_service "Grafana" grafana
        
        # Check health of all services
        echo "🔍 Checking service health..."
        
        # Wait for services to be fully ready
        echo "⏳ Waiting for services to be fully ready..."
        sleep 15
        
        # Show final status
        show_status
        
        echo "✅ All services started successfully!"
        echo "🌐 Frontend: http://localhost:3000"
        echo "🔧 API: http://localhost:8000"
        echo "🔧 API Docs: http://localhost:8000/docs"
        echo "🔄 N8N: http://localhost:5678"
        echo "📊 Grafana: http://localhost:3001"
        echo "📊 Grafana (admin): http://localhost:3001 (admin/admin123)"
        ;;
        
    "stop")
        echo "🛑 Stopping all services..."
        stop_service "FastAPI" fastapi
        stop_service "N8N" n8n
        stop_service "Frontend" frontend
        stop_service "Grafana" grafana
        stop_service "OpenAlgo" openalgo
        stop_service "PostgreSQL" postgres
        stop_service "Redis" redis
        
        echo "✅ All services stopped"
        ;;
        
    "restart")
        echo "🔄 Restarting all services..."
        stop_service "FastAPI" fastapi
        stop_service "N8N" n8n
        stop_service "Frontend" frontend
        stop_service "Grafana" grafana
        stop_service "OpenAlgo" openalgo
        stop_service "PostgreSQL" postgres
        stop_service "Redis" redis
        
        sleep 5
        
        start_service "PostgreSQL" postgres
        start_service "Redis" redis
        start_service "OpenAlgo" openalgo
        start_service "FastAPI" fastapi
        start_service "N8N" n8n
        start_service "Frontend" frontend
        start_service "Grafana" grafana
        
        echo "✅ All services restarted"
        ;;
        
    "logs")
        echo "📋 Showing logs for all services..."
        show_logs "FastAPI" fastapi
        show_logs "N8N" n8n
        show_logs "Frontend" frontend
        show_logs "Grafana" grafana
        show_logs "PostgreSQL" postgres
        show_logs "Redis" redis
        show_logs "OpenAlgo" openalgo
        ;;
        
    "status")
        show_status
        ;;
        
    "health")
        echo "🔍 Checking service health..."
        
        # Check each service health
        postgres_healthy=$(check_service_health "PostgreSQL" velo_postgres_dev "http://localhost:5432/health")
        redis_healthy=$(check_service_health "Redis" velo_redis_dev "http://localhost:6379/health")
        fastapi_healthy=$(check_service_health "FastAPI" velo_fastapi_dev "http://localhost:8000/api/health")
        n8n_healthy=$(check_service_health "N8N" velo_n8n_dev "http://localhost:5678/health")
        frontend_healthy=$(check_service_health "Frontend" velo_frontend_dev "http://localhost:3000")
        grafana_healthy=$(check_service_health "Grafana" velo_grafana_dev "http://localhost:3001/api/health")
        openalgo_healthy=$(check_service_health "OpenAlgo" velo_openalgo_dev "http://localhost:3000/health")
        
        echo "Service Health Status:"
        echo "=================="
        echo "PostgreSQL: $([ $postgres_healthy -eq 0 ] && echo '🟢 Healthy' || echo '🔴 Unhealthy')"
        echo "Redis: $([ $redis_healthy -eq 0 ] && echo '🟢 Healthy' || echo '🔴 Unhealthy')"
        echo "FastAPI: $([ $fastapi_healthy -eq 0 ] && echo '🟢 Healthy' || echo '🔴 Unhealthy')"
        echo "N8N: $([ $n8n_healthy -eq 0 ] && echo '🟢 Healthy' || echo '🔴 Unhealthy')"
        echo "Frontend: $([ $frontend_healthy -eq 0 ] && echo '🟢 Healthy' || echo '🔴 Unhealthy')"
        echo "Grafana: $([ $grafana_healthy -eq 0 ] && echo '🟢 Healthy' || echo '🔴 Unhealthy')"
        echo "OpenAlgo: $([ $openalgo_healthy -eq 0 ] && echo '🟢 Healthy' || echo '🔴 Unhealthy')"
        echo "=================="
        
        # Overall health status
        if [ $postgres_healthy -eq 0 ] && [ $redis_healthy -eq 0 ] && [ $fastapi_healthy -eq 0 ]; then
            echo "✅ All services are healthy"
        else
            echo "❌ Some services are unhealthy"
        fi
        ;;
        
    "cleanup")
        cleanup
        ;;
        
    "reset-db")
        reset_database
        ;;
        
    "install-deps")
        install_dependencies
        ;;
        
    "test")
        run_tests
        ;;
        
    "build")
        build_production
        ;;
        
    "deploy")
        deploy_production
        ;;
        
    "help"|*)
        echo "VELOX-N8N Development Environment Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  start       - Start all services"
        echo "  stop        - Stop all services"
        echo "  restart     - Restart all services"
        echo "  logs        - Show logs for all services"
        echo "  status      - Show service status"
        echo "  health      - Check service health"
        echo "  cleanup     - Clean up containers and images"
        echo "  reset-db    - Reset database"
        echo "  install-deps - Install dependencies"
        echo "  test        - Run tests"
        echo "  build       - Build for production"
        echo "  deploy      - Deploy to production"
        echo ""
        echo "Examples:"
        echo "  $0 start"
        echo "  $0 logs fastapi"
        echo "  $0 status"
        ;;
esac