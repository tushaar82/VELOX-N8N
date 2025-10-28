#!/bin/bash

# VELOX-N8N Verification Script
# Verifies all fixes have been applied correctly

set -e

echo "======================================================================"
echo "VELOX-N8N Fix Verification Script"
echo "======================================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print test result
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
        ((TESTS_FAILED++))
    fi
}

echo "Running verification tests..."
echo ""

# Test 1: Check Dockerfile doesn't have duplicate user creation
echo "Test 1: Checking Dockerfile for duplicate user creation..."
DUPLICATE_COUNT=$(grep -c "useradd -m -u 1000 velox" Dockerfile || true)
if [ "$DUPLICATE_COUNT" -eq 1 ]; then
    print_result 0 "Dockerfile has no duplicate user creation"
else
    print_result 1 "Dockerfile has $DUPLICATE_COUNT user creation commands (should be 1)"
fi
echo ""

# Test 2: Check docker-compose.yml doesn't have version attribute
echo "Test 2: Checking docker-compose.yml for obsolete version attribute..."
if ! grep -q "^version:" docker-compose.yml; then
    print_result 0 "docker-compose.yml has no version attribute"
else
    print_result 1 "docker-compose.yml still has version attribute"
fi
echo ""

# Test 3: Verify Python syntax
echo "Test 3: Verifying Python syntax..."
if python3 -m py_compile main.py 2>/dev/null; then
    print_result 0 "main.py syntax is valid"
else
    print_result 1 "main.py has syntax errors"
fi
echo ""

# Test 4: Verify Python imports
echo "Test 4: Verifying Python imports..."
if python3 -c "import app.core.config; import app.services.option_chain" 2>/dev/null; then
    print_result 0 "All Python imports successful"
else
    print_result 1 "Python imports failed"
fi
echo ""

# Test 5: Verify Docker Compose configuration
echo "Test 5: Verifying Docker Compose configuration..."
if docker compose config > /dev/null 2>&1; then
    print_result 0 "Docker Compose configuration is valid"
else
    print_result 1 "Docker Compose configuration has errors"
fi
echo ""

# Test 6: Check Dockerfile Playwright installation order
echo "Test 6: Checking Playwright installation order in Dockerfile..."
PLAYWRIGHT_LINE=$(grep -n "playwright install chromium" Dockerfile | cut -d: -f1)
COPY_APP_LINE=$(grep -n "^COPY \. \." Dockerfile | cut -d: -f1)
if [ "$PLAYWRIGHT_LINE" -lt "$COPY_APP_LINE" ]; then
    print_result 0 "Playwright is installed before copying app code"
else
    print_result 1 "Playwright installation order is incorrect"
fi
echo ""

# Test 7: Verify .env.example exists
echo "Test 7: Checking .env.example file..."
if [ -f ".env.example" ]; then
    print_result 0 ".env.example file exists"
else
    print_result 1 ".env.example file is missing"
fi
echo ""

# Test 8: Verify required directories exist
echo "Test 8: Checking required directories..."
REQUIRED_DIRS=("app" "app/api" "app/core" "app/services" "app/schemas")
ALL_DIRS_EXIST=true
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        ALL_DIRS_EXIST=false
        break
    fi
done
if [ "$ALL_DIRS_EXIST" = true ]; then
    print_result 0 "All required directories exist"
else
    print_result 1 "Some required directories are missing"
fi
echo ""

# Test 9: Docker build dry-run
echo "Test 9: Testing Docker build (dry-run)..."
if docker compose build --dry-run velox-api > /dev/null 2>&1; then
    print_result 0 "Docker build dry-run successful"
else
    print_result 1 "Docker build dry-run failed"
fi
echo ""

# Test 10: Check requirements.txt
echo "Test 10: Checking requirements.txt..."
if [ -f "requirements.txt" ] && grep -q "fastapi" requirements.txt && grep -q "playwright" requirements.txt; then
    print_result 0 "requirements.txt is valid and contains required packages"
else
    print_result 1 "requirements.txt is missing or incomplete"
fi
echo ""

# Summary
echo "======================================================================"
echo "VERIFICATION SUMMARY"
echo "======================================================================"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    echo ""
    echo "Your VELOX-N8N project is ready for deployment!"
    echo ""
    echo "Next steps:"
    echo "  1. Configure .env file: cp .env.example .env && nano .env"
    echo "  2. Start the stack: ./docker-start.sh"
    echo "  3. Access API docs: http://localhost:8000/docs"
    echo ""
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please review the failed tests above and fix the issues."
    echo ""
    exit 1
fi
