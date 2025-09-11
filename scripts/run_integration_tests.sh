#!/bin/bash

# Integration Test Script for Project Intelligencia Scheduler
# This script sets up the testing environment and runs integration tests
# between the frontend and backend services.

# Exit on any error
set -e

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===============================================${NC}"
echo -e "${YELLOW}     Project Intelligencia Integration Tests   ${NC}"
echo -e "${YELLOW}===============================================${NC}"

# Step 1: Ensure all required services are installed
echo -e "\n${GREEN}Checking required tools...${NC}"

# Check for Docker and Docker Compose
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker and Docker Compose are required for running integration tests${NC}"
    exit 1
fi

# Step 2: Stop any existing containers to ensure a clean environment
echo -e "\n${GREEN}Stopping any existing containers...${NC}"
docker-compose down --remove-orphans || true

# Step 3: Start the database first to ensure it's ready for other services
echo -e "\n${GREEN}Starting database container...${NC}"
docker-compose up -d db
echo "Waiting for database to be ready..."
sleep 10 # Give the database time to initialize

# Step 4: Initialize the database with test data
echo -e "\n${GREEN}Initializing database with test data...${NC}"
docker-compose run --rm db-init

# Step 5: Start the backend services
echo -e "\n${GREEN}Starting backend services...${NC}"
docker-compose up -d iam-service data-service scheduler-service

# Step 6: Wait for services to be ready
echo -e "\n${GREEN}Waiting for services to be ready...${NC}"
echo "This may take a moment..."
sleep 15

# Step 7: Run backend service health checks
echo -e "\n${GREEN}Checking backend service health...${NC}"

# Check IAM Service
echo -e "Testing IAM Service..."
if curl -s http://localhost:8000/api/v1/health | grep -q "status.*UP"; then
    echo -e "${GREEN}✅ IAM Service is healthy${NC}"
else
    echo -e "${RED}❌ IAM Service health check failed${NC}"
    exit 1
fi

# Check Data Service
echo -e "Testing Data Service..."
if curl -s http://localhost:8001/api/v1/health | grep -q "status.*UP"; then
    echo -e "${GREEN}✅ Data Service is healthy${NC}"
else
    echo -e "${RED}❌ Data Service health check failed${NC}"
    exit 1
fi

# Check Scheduler Service
echo -e "Testing Scheduler Service..."
if curl -s http://localhost:8002/api/v1/health | grep -q "status.*UP"; then
    echo -e "${GREEN}✅ Scheduler Service is healthy${NC}"
else
    echo -e "${RED}❌ Scheduler Service health check failed${NC}"
    exit 1
fi

# Step 8: Run integration tests for API endpoints
echo -e "\n${GREEN}Running API integration tests...${NC}"

# Function to run API tests
run_api_test() {
    local endpoint=$1
    local method=${2:-GET}
    local expected_status=${3:-200}
    local data=${4:-""}
    local auth_token=${5:-""}
    
    echo -e "Testing $method $endpoint..."
    
    local auth_header=""
    if [ -n "$auth_token" ]; then
        auth_header="-H 'Authorization: Bearer $auth_token'"
    fi
    
    local cmd=""
    if [ "$method" = "GET" ]; then
        cmd="curl -s -o /dev/null -w '%{http_code}' $auth_header $endpoint"
    else
        cmd="curl -s -X $method -o /dev/null -w '%{http_code}' $auth_header -H 'Content-Type: application/json' -d '$data' $endpoint"
    fi
    
    status=$(eval $cmd)
    
    if [ "$status" -eq "$expected_status" ]; then
        echo -e "${GREEN}✅ Test passed: $method $endpoint returned $status${NC}"
        return 0
    else
        echo -e "${RED}❌ Test failed: $method $endpoint returned $status, expected $expected_status${NC}"
        return 1
    fi
}

# Authenticate and get token
echo -e "Authenticating with IAM service..."
auth_response=$(curl -s -X POST -H "Content-Type: application/json" -d '{"username": "admin@example.com", "password": "adminpassword"}' http://localhost:8000/api/v1/auth/login)
token=$(echo $auth_response | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$token" ]; then
    echo -e "${RED}❌ Authentication failed${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Authentication successful${NC}"
fi

# Run tests with authentication
run_api_test "http://localhost:8001/api/v1/institutions" "GET" 200 "" "$token"
run_api_test "http://localhost:8001/api/v1/departments" "GET" 200 "" "$token"
run_api_test "http://localhost:8001/api/v1/faculty" "GET" 200 "" "$token"
run_api_test "http://localhost:8001/api/v1/subjects" "GET" 200 "" "$token"
run_api_test "http://localhost:8001/api/v1/classrooms" "GET" 200 "" "$token"
run_api_test "http://localhost:8001/api/v1/time-slots" "GET" 200 "" "$token"
run_api_test "http://localhost:8002/api/v1/scheduler/status" "GET" 200 "" "$token"

# Step 9: Start the frontend for end-to-end testing
echo -e "\n${GREEN}Starting frontend for end-to-end testing...${NC}"
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

# Give frontend time to start
echo "Waiting for frontend to start..."
sleep 10

# Step 10: Run basic frontend health check
echo -e "\n${GREEN}Checking frontend health...${NC}"
if curl -s http://localhost:5173 | grep -q "<div id=\"root\">"; then
    echo -e "${GREEN}✅ Frontend is running${NC}"
else
    echo -e "${RED}❌ Frontend health check failed${NC}"
    kill $FRONTEND_PID
    exit 1
fi

echo -e "\n${GREEN}Frontend is ready for manual testing at http://localhost:5173${NC}"
echo -e "${YELLOW}Login with:${NC}"
echo -e "  Username: admin@example.com"
echo -e "  Password: adminpassword"

# Step 11: Run automated UI tests if available
if [ -d "frontend/cypress" ]; then
    echo -e "\n${GREEN}Running automated UI tests...${NC}"
    cd frontend
    npx cypress run
    UI_TEST_STATUS=$?
    cd ..
    
    if [ $UI_TEST_STATUS -eq 0 ]; then
        echo -e "${GREEN}✅ UI tests passed${NC}"
    else
        echo -e "${RED}❌ UI tests failed${NC}"
    fi
else
    echo -e "\n${YELLOW}No automated UI tests found. Skipping this step.${NC}"
fi

# Step 12: Generate a test timetable to verify full integration
echo -e "\n${GREEN}Testing timetable generation...${NC}"
timetable_request='{
  "department_id": "dept-1",
  "algorithm": "csp",
  "parameters": {
    "max_iterations": 1000,
    "timeout_seconds": 30
  }
}'

timetable_response=$(curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $token" -d "$timetable_request" http://localhost:8002/api/v1/scheduler/generate)
job_id=$(echo $timetable_response | grep -o '"job_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$job_id" ]; then
    echo -e "${RED}❌ Timetable generation request failed${NC}"
else
    echo -e "${GREEN}✅ Timetable generation job submitted with ID: $job_id${NC}"
    
    # Poll job status
    echo "Polling job status..."
    max_attempts=10
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        attempt=$((attempt+1))
        status_response=$(curl -s -H "Authorization: Bearer $token" http://localhost:8002/api/v1/scheduler/jobs/$job_id)
        status=$(echo $status_response | grep -o '"status":"[^"]*' | cut -d'"' -f4)
        
        echo "Job status: $status (attempt $attempt/$max_attempts)"
        
        if [ "$status" = "completed" ]; then
            echo -e "${GREEN}✅ Timetable generation completed successfully${NC}"
            break
        elif [ "$status" = "failed" ]; then
            echo -e "${RED}❌ Timetable generation failed${NC}"
            break
        fi
        
        sleep 5
    done
    
    if [ $attempt -eq $max_attempts ] && [ "$status" != "completed" ]; then
        echo -e "${YELLOW}⚠️ Timetable generation is taking longer than expected${NC}"
    fi
fi

# Step 13: Cleanup
echo -e "\n${GREEN}Cleaning up...${NC}"
kill $FRONTEND_PID || true
docker-compose down

echo -e "\n${YELLOW}===============================================${NC}"
echo -e "${GREEN}Integration tests completed!${NC}"
echo -e "${YELLOW}===============================================${NC}"
