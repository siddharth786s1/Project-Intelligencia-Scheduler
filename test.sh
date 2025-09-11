#!/bin/bash
# Integration Test Script

# Set up required environment
echo "Setting up test environment..."
mkdir -p test_output

# Run unit tests first
echo "Running unit tests..."
cd frontend
npm test

# If unit tests pass, proceed to integration tests
if [ $? -eq 0 ]; then
  echo "Unit tests passed. Running integration tests..."
  
  # Start backend services in Docker containers
  cd ..
  docker-compose -f docker-compose.test.yml up -d
  
  # Wait for services to be available
  echo "Waiting for services to start..."
  sleep 10
  
  # Run API tests
  echo "Testing API endpoints..."
  # Add API testing commands here
  
  # Run end-to-end tests
  echo "Running end-to-end tests..."
  cd frontend
  npm run test:e2e
  
  # Clean up
  cd ..
  docker-compose -f docker-compose.test.yml down
  
  echo "Integration tests completed."
else
  echo "Unit tests failed. Fixing unit tests before proceeding."
  exit 1
fi
