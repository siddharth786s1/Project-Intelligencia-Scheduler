#!/bin/bash

# Start only the necessary components for integration testing

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

# Define the components to start
status "Starting only the necessary components for integration testing..."

# 1. Start the database
status "Starting PostgreSQL database..."
docker-compose up -d db

# Wait for the database to be ready
status "Waiting for database to become ready..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if docker-compose exec db pg_isready -U postgres > /dev/null 2>&1; then
    status "Database is ready!"
    break
  else
    warning "Database not ready yet. Waiting... (Attempt $((RETRY_COUNT+1))/$MAX_RETRIES)"
    RETRY_COUNT=$((RETRY_COUNT+1))
    sleep 5
  fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
  error "Database failed to become ready in time."
fi

# 2. Start RabbitMQ
status "Starting RabbitMQ..."
docker-compose up -d rabbitmq

# 3. Start the services one by one
status "Starting IAM Service..."
docker-compose up -d iam-service

status "Starting Data Service..."
docker-compose up -d data-service

status "Starting Scheduler Service..."
docker-compose up -d scheduler-service

# 4. Start the worker
status "Starting Scheduler Worker..."
docker-compose up -d scheduler-worker

# 5. Start the frontend in development mode for easier debugging
status "Starting frontend in development mode..."

# Change to the frontend directory
cd "$(dirname "$0")/frontend"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  status "Installing frontend dependencies..."
  npm install
fi

# Set environment variables for development
export VITE_API_BASE_URL=http://localhost:8080/api
export VITE_IAM_SERVICE_URL=http://localhost:8001/api/v1
export VITE_DATA_SERVICE_URL=http://localhost:8002/api/v1
export VITE_SCHEDULER_SERVICE_URL=http://localhost:8003/api/v1

# Start the development server
status "Starting Vite development server..."
npm run dev &

# 6. Start NGINX as a reverse proxy
status "Starting NGINX reverse proxy..."
docker-compose up -d nginx

status "All components started successfully!"
status ""
status "Useful endpoints:"
status "  - Frontend: http://localhost:5173 (dev server) or http://localhost:80 (via NGINX)"
status "  - IAM Service API: http://localhost:8001/api/v1"
status "  - Data Service API: http://localhost:8002/api/v1"
status "  - Scheduler Service API: http://localhost:8003/api/v1"
status "  - RabbitMQ Management: http://localhost:15672 (guest/guest)"
status ""
status "To run the integration tests, follow the test plan in test_plan.md"
status "Use the integration checklist in integration_checklist.md to verify functionality"
status ""
status "Press Ctrl+C to stop the frontend dev server"

# Wait for Ctrl+C
wait
