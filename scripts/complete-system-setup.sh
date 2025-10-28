#!/bin/bash

echo "======================================================================"
echo "VELOX-N8N Complete System Setup"
echo "======================================================================"
echo ""

# Function to display colored output
print_status() {
    local status=$1
    local message=$2
    
    case $status in
        "INFO") echo -e "\033[0;34mℹ️  $message\033[0m" ;;
        "SUCCESS") echo -e "\033[0;32m✅ $message\033[0m" ;;
        "WARNING") echo -e "\033[0;33m⚠️  $message\033[0m" ;;
        "ERROR") echo -e "\033[0;31m❌ $message\033[0m" ;;
        "STEP") echo -e "\033[0;36m➡️  $message\033[0m" ;;
        *) echo "$message" ;;
    esac
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if service is running
service_running() {
    local service=$1
    local port=$2
    
    if command_exists "lsof"; then
        if lsof -i :$port | grep -q "LISTEN"; then
            return 0
        fi
    fi
    
    # Alternative check
    if command_exists "netstat"; then
        if netstat -tuln | grep -q ":$port "; then
            return 0
        fi
    fi
    
    return 1
}

# Function to wait for service to be ready
wait_for_service() {
    local service=$1
    local port=$2
    local max_attempts=$3
    local wait_time=$4
    
    print_status "INFO" "Waiting for $service to be ready on port $port..."
    
    for i in $(seq 1 $max_attempts); do
        if service_running "$service" "$port"; then
            print_status "SUCCESS" "$service is ready!"
            return 0
        fi
        
        print_status "INFO" "Attempt $i/$max_attempts: Waiting ${wait_time}s..."
        sleep $wait_time
    done
    
    print_status "ERROR" "$service failed to start after $max_attempts attempts"
    return 1
}

# Step 1: Check prerequisites
print_status "STEP" "Checking prerequisites..."

# Check if Docker is running
if ! command_exists "docker"; then
    print_status "ERROR" "Docker is not installed or not in PATH"
    exit 1
fi

# Check if docker-compose is available
if ! command_exists "docker-compose"; then
    print_status "ERROR" "docker-compose is not installed or not in PATH"
    exit 1
fi

# Check if required files exist
required_files=(
    "Dockerfile"
    "docker-compose.yml"
    "scripts/fix-openalgo-host.sh"
    "app/services/indicators.py"
    "app/api/v1/endpoints/indicators_categorized.py"
    "app/api/v1/endpoints/technical_analysis.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_status "ERROR" "Required file not found: $file"
        exit 1
    fi
done

print_status "SUCCESS" "All prerequisites checked"

# Step 2: Fix OpenAlgo connectivity
print_status "STEP" "Fixing OpenAlgo connectivity..."

# Check if OpenAlgo is running
if service_running "python" "5000"; then
    print_status "INFO" "Stopping existing OpenAlgo instance..."
    pkill -f "python.*app.py"
    sleep 2
fi

# Run the OpenAlgo fix script
if [ -f "scripts/fix-openalgo-host.sh" ]; then
    print_status "INFO" "Running OpenAlgo host configuration script..."
    chmod +x scripts/fix-openalgo-host.sh
    ./scripts/fix-openalgo-host.sh
    
    # Wait for OpenAlgo to be ready
    if wait_for_service "OpenAlgo" "5000" 10 3; then
        print_status "SUCCESS" "OpenAlgo is running on all interfaces"
    else
        print_status "WARNING" "OpenAlgo may not be running properly"
    fi
else
    print_status "ERROR" "OpenAlgo fix script not found"
    exit 1
fi

# Step 3: Rebuild Docker with Playwright fix
print_status "STEP" "Rebuilding Docker container with Playwright fix..."

# Stop existing container
print_status "INFO" "Stopping existing VELOX API container..."
docker-compose stop velox-api

# Remove old container
print_status "INFO" "Removing old VELOX API container..."
docker-compose rm -f velox-api

# Rebuild with new Dockerfile
print_status "INFO" "Building new VELOX API container with Playwright fix..."
docker-compose build velox-api

# Start the container
print_status "INFO" "Starting VELOX API container..."
docker-compose up -d velox-api

# Wait for API to be ready
if wait_for_service "VELOX API" "8000" 15 5; then
    print_status "SUCCESS" "VELOX API is running"
else
    print_status "WARNING" "VELOX API may not be running properly"
fi

# Step 4: Verify all endpoints are working
print_status "STEP" "Verifying new endpoints..."

# Wait a bit more for the API to fully initialize
sleep 5

# Test categorized indicators endpoints
print_status "INFO" "Testing categorized indicators endpoints..."

# Test volume indicators
if curl -s http://localhost:8000/api/v1/indicators/volume > /dev/null; then
    print_status "SUCCESS" "Volume indicators endpoint is working"
else
    print_status "WARNING" "Volume indicators endpoint may not be working"
fi

# Test statistical indicators (NEW)
if curl -s http://localhost:8000/api/v1/indicators/statistical > /dev/null; then
    print_status "SUCCESS" "Statistical indicators endpoint is working"
else
    print_status "WARNING" "Statistical indicators endpoint may not be working"
fi

# Test pattern indicators (NEW)
if curl -s http://localhost:8000/api/v1/indicators/patterns > /dev/null; then
    print_status "SUCCESS" "Pattern indicators endpoint is working"
else
    print_status "WARNING" "Pattern indicators endpoint may not be working"
fi

# Test technical analysis endpoints (NEW)
print_status "INFO" "Testing technical analysis endpoints..."

# Test pivot points
if curl -s -X POST http://localhost:8000/api/v1/analysis/pivot-points \
    -H "Content-Type: application/json" \
    -d '{"symbol":"NIFTY","exchange":"NSE","interval":"1d"}' > /dev/null; then
    print_status "SUCCESS" "Pivot points endpoint is working"
else
    print_status "WARNING" "Pivot points endpoint may not be working"
fi

# Test Fibonacci retracements
if curl -s -X POST http://localhost:8000/api/v1/analysis/fibonacci \
    -H "Content-Type: application/json" \
    -d '{"symbol":"NIFTY","exchange":"NSE","interval":"1d"}' > /dev/null; then
    print_status "SUCCESS" "Fibonacci retracements endpoint is working"
else
    print_status "WARNING" "Fibonacci retracements endpoint may not be working"
fi

# Step 5: Run comprehensive tests
print_status "STEP" "Running comprehensive tests..."

if [ -f "tests/test_new_endpoints.py" ]; then
    print_status "INFO" "Running test suite..."
    python -m pytest tests/test_new_endpoints.py -v --tb=short
    
    if [ $? -eq 0 ]; then
        print_status "SUCCESS" "All tests passed"
    else
        print_status "WARNING" "Some tests failed"
    fi
else
    print_status "WARNING" "Test file not found"
fi

# Step 6: Display system status
print_status "STEP" "Displaying system status..."

echo ""
print_status "INFO" "System Status Summary:"
echo "=================================="

# Check OpenAlgo
if service_running "python" "5000"; then
    print_status "SUCCESS" "OpenAlgo: Running on port 5000"
else
    print_status "ERROR" "OpenAlgo: Not running"
fi

# Check VELOX API
if service_running "VELOX API" "8000"; then
    print_status "SUCCESS" "VELOX API: Running on port 8000"
else
    print_status "ERROR" "VELOX API: Not running"
fi

# Check n8n
if service_running "n8n" "5678"; then
    print_status "SUCCESS" "n8n: Running on port 5678"
else
    print_status "WARNING" "n8n: Not running (may not be needed)"
fi

# Check Node-RED
if service_running "node-red" "1880"; then
    print_status "SUCCESS" "Node-RED: Running on port 1880"
else
    print_status "WARNING" "Node-RED: Not running (May not be needed)"
fi

# Check Grafana
if service_running "grafana" "3001"; then
    print_status "SUCCESS" "Grafana: Running on port 3001"
else
    print_status "WARNING" "Grafana: Not running (May not be needed)"
fi

echo ""
echo "=================================="
echo ""

# Step 7: Display useful commands
print_status "INFO" "Useful Commands:"
echo "=================================="

echo "View VELOX API logs:"
echo "  docker logs -f velox-api"
echo ""

echo "Restart VELOX API:"
echo "  docker-compose restart velox-api"
echo ""

echo "Stop all services:"
echo "  docker-compose down"
echo ""

echo "Start all services:"
echo "  docker-compose up -d"
echo ""

echo "Access API documentation:"
echo "  http://localhost:8000/docs"
echo ""

echo "Access n8n:"
echo "  http://localhost:5678"
echo ""

echo "Access Node-RED:"
echo "  http://localhost:1880"
echo ""

echo "Access Grafana:"
echo "  http://localhost:3001"
echo ""

echo "Run tests:"
echo "  python -m pytest tests/test_new_endpoints.py -v"
echo ""

print_status "SUCCESS" "Setup complete! The VELOX-N8N system is ready to use."
echo ""
echo "======================================================================"