#!/bin/bash

# Integration Test Setup Script for Project Intelligencia Scheduler

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display status messages
status() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
  echo -e "${RED}[ERROR]${NC} $1"
  exit 1
}

# Check if Docker is running
status "Checking if Docker is running..."
if ! docker info >/dev/null 2>&1; then
  error "Docker is not running. Please start Docker and try again."
fi

# Start the containers
status "Starting all services with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
status "Waiting for services to become ready..."
sleep 10  # Initial wait

# Check if the database is ready
status "Checking database connection..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if docker-compose exec db pg_isready -U postgres > /dev/null 2>&1; then
    status "Database is ready!"
    break
  else
    warning "Database not ready yet. Waiting..."
    RETRY_COUNT=$((RETRY_COUNT+1))
    sleep 5
  fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
  error "Database failed to become ready in time."
fi

# Check if the services are responding
status "Checking service health..."
check_service() {
  local service=$1
  local port=$2
  local max_attempts=10
  local attempt=0
  
  while [ $attempt -lt $max_attempts ]; do
    if curl -s "http://localhost:$port/healthcheck" | grep -q "status.*ok"; then
      status "$service is healthy!"
      return 0
    else
      warning "$service not ready yet. Waiting... (Attempt $((attempt+1))/$max_attempts)"
      attempt=$((attempt+1))
      sleep 5
    fi
  done
  
  error "$service failed to become healthy in time."
}

check_service "IAM Service" 8001
check_service "Data Service" 8002
check_service "Scheduler Service" 8003

# Load test data
status "Setting up test data..."

# 1. Create a test institution
status "Creating test institution..."
INSTITUTION_ID=$(curl -s -X POST "http://localhost:8001/api/v1/institutions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Test University",
    "code": "TESTUNI",
    "address": "123 Test Street, Testville",
    "website": "https://testuni.edu"
  }' | jq -r '.data.id')

if [ "$INSTITUTION_ID" == "null" ]; then
  warning "Failed to create institution or extract ID. Using placeholder."
  INSTITUTION_ID="00000000-0000-0000-0000-000000000000"
fi

# Register an admin user for testing
status "Registering admin user..."
curl -s -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"admin@testuni.edu\",
    \"password\": \"Password123!\",
    \"first_name\": \"Admin\",
    \"last_name\": \"User\",
    \"role\": \"admin\",
    \"institution_id\": \"$INSTITUTION_ID\"
  }"

# Login and get token
status "Logging in to get authentication token..."
TOKEN=$(curl -s -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@testuni.edu",
    "password": "Password123!"
  }' | jq -r '.data.access_token')

if [ "$TOKEN" == "null" ]; then
  error "Failed to get authentication token."
fi

# Create departments
status "Creating departments..."
DEPT_CS_ID=$(curl -s -X POST "http://localhost:8002/api/v1/departments" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"name\": \"Computer Science\",
    \"code\": \"CS\",
    \"institution_id\": \"$INSTITUTION_ID\"
  }" | jq -r '.data.id')

DEPT_EE_ID=$(curl -s -X POST "http://localhost:8002/api/v1/departments" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"name\": \"Electrical Engineering\",
    \"code\": \"EE\",
    \"institution_id\": \"$INSTITUTION_ID\"
  }" | jq -r '.data.id')

# Create batches
status "Creating batches..."
BATCH_CS_ID=$(curl -s -X POST "http://localhost:8002/api/v1/batches" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"name\": \"CS Batch 2023\",
    \"year\": 2023,
    \"department_id\": \"$DEPT_CS_ID\",
    \"strength\": 60
  }" | jq -r '.data.id')

BATCH_EE_ID=$(curl -s -X POST "http://localhost:8002/api/v1/batches" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"name\": \"EE Batch 2023\",
    \"year\": 2023,
    \"department_id\": \"$DEPT_EE_ID\",
    \"strength\": 45
  }" | jq -r '.data.id')

# Create faculty members
status "Creating faculty members..."
FACULTY_1_ID=$(curl -s -X POST "http://localhost:8002/api/v1/faculty" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"name\": \"Dr. John Smith\",
    \"email\": \"john.smith@testuni.edu\",
    \"department_id\": \"$DEPT_CS_ID\",
    \"designation\": \"Professor\",
    \"max_hours_per_day\": 6,
    \"max_hours_per_week\": 20
  }" | jq -r '.data.id')

FACULTY_2_ID=$(curl -s -X POST "http://localhost:8002/api/v1/faculty" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"name\": \"Dr. Jane Doe\",
    \"email\": \"jane.doe@testuni.edu\",
    \"department_id\": \"$DEPT_EE_ID\",
    \"designation\": \"Associate Professor\",
    \"max_hours_per_day\": 5,
    \"max_hours_per_week\": 18
  }" | jq -r '.data.id')

# Create subjects
status "Creating subjects..."
SUBJECT_CS1_ID=$(curl -s -X POST "http://localhost:8002/api/v1/subjects" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"name\": \"Introduction to Programming\",
    \"code\": \"CS101\",
    \"department_id\": \"$DEPT_CS_ID\",
    \"credits\": 4,
    \"lecture_hours_per_week\": 3,
    \"practical_hours_per_week\": 2
  }" | jq -r '.data.id')

SUBJECT_CS2_ID=$(curl -s -X POST "http://localhost:8002/api/v1/subjects" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"name\": \"Data Structures\",
    \"code\": \"CS102\",
    \"department_id\": \"$DEPT_CS_ID\",
    \"credits\": 4,
    \"lecture_hours_per_week\": 3,
    \"practical_hours_per_week\": 2
  }" | jq -r '.data.id')

# Create room types
status "Creating room types..."
ROOM_TYPE_LEC_ID=$(curl -s -X POST "http://localhost:8002/api/v1/room-types" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"name\": \"Lecture Hall\",
    \"institution_id\": \"$INSTITUTION_ID\"
  }" | jq -r '.data.id')

ROOM_TYPE_LAB_ID=$(curl -s -X POST "http://localhost:8002/api/v1/room-types" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"name\": \"Computer Lab\",
    \"institution_id\": \"$INSTITUTION_ID\"
  }" | jq -r '.data.id')

# Create classrooms
status "Creating classrooms..."
CLASSROOM_LEC1_ID=$(curl -s -X POST "http://localhost:8002/api/v1/classrooms" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"name\": \"Lecture Hall 101\",
    \"capacity\": 80,
    \"room_type_id\": \"$ROOM_TYPE_LEC_ID\",
    \"building\": \"Main Building\",
    \"floor\": 1
  }" | jq -r '.data.id')

CLASSROOM_LAB1_ID=$(curl -s -X POST "http://localhost:8002/api/v1/classrooms" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"name\": \"Computer Lab 201\",
    \"capacity\": 60,
    \"room_type_id\": \"$ROOM_TYPE_LAB_ID\",
    \"building\": \"Main Building\",
    \"floor\": 2
  }" | jq -r '.data.id')

# Create time slots
status "Creating time slots..."
for day in "Monday" "Tuesday" "Wednesday" "Thursday" "Friday"; do
  for start_hour in 9 10 11 12 14 15 16; do
    end_hour=$((start_hour + 1))
    
    curl -s -X POST "http://localhost:8002/api/v1/time-slots" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d "{
        \"day\": \"$day\",
        \"start_time\": \"$start_hour:00:00\",
        \"end_time\": \"$end_hour:00:00\",
        \"institution_id\": \"$INSTITUTION_ID\"
      }" > /dev/null
  done
done

# Associate faculty with subjects
status "Associating faculty with subjects..."
curl -s -X POST "http://localhost:8002/api/v1/subjects/$SUBJECT_CS1_ID/faculty/$FACULTY_1_ID" \
  -H "Authorization: Bearer $TOKEN" > /dev/null

curl -s -X POST "http://localhost:8002/api/v1/subjects/$SUBJECT_CS2_ID/faculty/$FACULTY_2_ID" \
  -H "Authorization: Bearer $TOKEN" > /dev/null

# Associate subjects with batches
status "Associating subjects with batches..."
curl -s -X POST "http://localhost:8002/api/v1/batches/$BATCH_CS_ID/subjects/$SUBJECT_CS1_ID" \
  -H "Authorization: Bearer $TOKEN" > /dev/null

curl -s -X POST "http://localhost:8002/api/v1/batches/$BATCH_CS_ID/subjects/$SUBJECT_CS2_ID" \
  -H "Authorization: Bearer $TOKEN" > /dev/null

status "Test data setup complete!"
status "You can now access the application at http://localhost:80"
status ""
status "Test credentials:"
status "  Email: admin@testuni.edu"
status "  Password: Password123!"
status ""
status "Use the test plan to verify the scheduler service integration"
