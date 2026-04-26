#!/bin/bash
# Verification Script for Prakriti AI Facial Analysis System
# Run this to verify everything is set up correctly

echo "============================================"
echo "  PRAKRITI AI - SYSTEM VERIFICATION"
echo "============================================"
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter
PASSED=0
FAILED=0

# Function to check if command exists
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $1 is NOT installed"
        ((FAILED++))
    fi
}

# Function to check if port is listening
check_port() {
    if nc -z localhost $1 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Port $1 is listening"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Port $1 is NOT listening"
        ((FAILED++))
    fi
}

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $1 does NOT exist"
        ((FAILED++))
    fi
}

# Function to test HTTP endpoint
check_endpoint() {
    response=$(curl -s -o /dev/null -w "%{http_code}" $1)
    if [ "$response" = "200" ] || [ "$response" = "404" ] || [ "$response" = "405" ]; then
        echo -e "${GREEN}✓${NC} $1 is responding (HTTP $response)"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $1 returned HTTP $response"
        ((FAILED++))
    fi
}

echo "[1] CHECKING SYSTEM REQUIREMENTS"
echo "================================"
check_command "node"
check_command "npm"
check_command "python"
echo

echo "[2] CHECKING PROJECT FILES"
echo "================================"
check_file "package.json"
check_file "server.js"
check_file "ml_service/app.py"
check_file "ml_service/requirements.txt"
check_file "public/js/main.js"
check_file "public/index.html"
echo

echo "[3] CHECKING RUNNING SERVICES"
echo "================================"
check_port 3000
check_port 5000
echo

if [ "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000)" -eq "200" ]; then
    echo "[4] TESTING BACKEND ENDPOINTS"
    echo "================================"
    check_endpoint "http://localhost:3000"
    echo
fi

if [ "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5000)" -eq "200" ]; then
    echo "[5] TESTING ML SERVICE ENDPOINTS"
    echo "================================"
    check_endpoint "http://localhost:5000/health"
    echo
fi

echo "============================================"
echo "  VERIFICATION SUMMARY"
echo "============================================"
echo -e "${GREEN}✓ Passed: $PASSED${NC}"
echo -e "${RED}✗ Failed: $FAILED${NC}"
echo

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All checks passed! System is ready.${NC}"
    exit 0
else
    echo -e "${YELLOW}Some checks failed. Please review the issues above.${NC}"
    exit 1
fi
