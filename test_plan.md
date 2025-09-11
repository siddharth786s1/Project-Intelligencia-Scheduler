# Scheduler Service Integration Test Plan

## Overview

This test plan focuses on verifying the integration between the frontend application and the scheduler service to ensure proper timetable generation, viewing, and management.

## Prerequisites

1. All services running in Docker:
   - PostgreSQL database
   - IAM Service
   - Data Service
   - Scheduler Service and Workers
   - RabbitMQ
   - Frontend
   - NGINX

2. Test data should be loaded:
   - Institution
   - Departments
   - Batches
   - Faculty
   - Subjects
   - Classrooms
   - Time slots
   - Constraints

## Test Scenarios

### 1. User Authentication and Authorization

#### 1.1. Authentication Test
- **Objective**: Verify that users can log in and access secured endpoints
- **Steps**:
  1. Log in using valid credentials
  2. Verify JWT token is stored in local storage
  3. Navigate to protected routes
- **Expected Result**: User is authenticated and can access protected routes

#### 1.2. Authorization Test
- **Objective**: Verify that users can only access allowed resources
- **Steps**:
  1. Log in as different user roles (admin, department head, faculty)
  2. Verify access to different sections based on role
- **Expected Result**: Access is granted based on user roles

### 2. Data Service Integration

#### 2.1. Data Retrieval Test
- **Objective**: Verify that the frontend can retrieve necessary data for timetable generation
- **Steps**:
  1. Check data loading for departments
  2. Check data loading for batches
  3. Check data loading for faculty
  4. Check data loading for subjects
  5. Check data loading for classrooms
  6. Check data loading for time slots
- **Expected Result**: All data is correctly retrieved and displayed in the UI

### 3. Timetable Generation Process

#### 3.1. Job Creation Test
- **Objective**: Verify that a timetable generation job can be created
- **Steps**:
  1. Navigate to TimetableGenerator component
  2. Select departments and batches
  3. Configure algorithm settings (CSP or Genetic)
  4. Submit the job
- **Expected Result**: Job is created and a job ID is returned

#### 3.2. Job Status Tracking Test
- **Objective**: Verify that job status can be tracked
- **Steps**:
  1. Create a job
  2. Check status using polling
  3. Verify status updates (PENDING, PROCESSING, COMPLETED, FAILED)
- **Expected Result**: Job status is correctly updated in the UI

#### 3.3. Algorithm Type Test
- **Objective**: Verify both algorithm types (CSP and Genetic)
- **Steps**:
  1. Run a job with CSP algorithm
  2. Run a job with Genetic algorithm
  3. Compare results and performance
- **Expected Result**: Both algorithms produce valid timetables

### 4. Timetable Viewing and Management

#### 4.1. Timetable Viewing Test
- **Objective**: Verify that generated timetables can be viewed
- **Steps**:
  1. Generate a timetable
  2. View the timetable in different formats (batch, faculty, classroom)
  3. Check for correct display of sessions
- **Expected Result**: Timetables are correctly displayed in all formats

#### 4.2. Timetable Filtering Test
- **Objective**: Verify that timetables can be filtered
- **Steps**:
  1. Apply filters by batch
  2. Apply filters by faculty
  3. Apply filters by department
  4. Apply filters by classroom
- **Expected Result**: Filters correctly limit the displayed timetable entries

#### 4.3. Timetable Export Test (if implemented)
- **Objective**: Verify timetable export functionality
- **Steps**:
  1. Generate a timetable
  2. Export to PDF or Excel
  3. Verify content of exported file
- **Expected Result**: Timetable is correctly exported

### 5. Error Handling and Edge Cases

#### 5.1. Job Failure Test
- **Objective**: Verify proper error handling for failed jobs
- **Steps**:
  1. Create a job with invalid parameters or conflicting constraints
  2. Verify error message display
  3. Check if the UI recovers gracefully
- **Expected Result**: Errors are properly displayed and the UI remains usable

#### 5.2. No Solution Test
- **Objective**: Verify behavior when no timetable solution is possible
- **Steps**:
  1. Create a job with constraints that cannot be satisfied
  2. Check the error message
- **Expected Result**: System indicates that no solution could be found

#### 5.3. Session Timeout Test
- **Objective**: Verify behavior on auth token expiry
- **Steps**:
  1. Log in
  2. Wait for token to expire (or modify expiry time for testing)
  3. Attempt an operation
- **Expected Result**: User is redirected to login or token is refreshed automatically

## Integration Test Plan

1. Setup the test environment:
   ```bash
   docker-compose up -d
   ```

2. Load test data:
   - Create institution
   - Create departments
   - Create batches
   - Create faculty
   - Create subjects
   - Create classrooms
   - Define time slots
   - Set up constraints

3. Run the frontend and manually execute the test scenarios above

4. Document any issues found during testing

## Performance Considerations

- Monitor worker CPU and memory usage during timetable generation
- Check response times for large timetable retrievals
- Test with multiple concurrent timetable generation jobs

## Security Considerations

- Verify that users cannot access timetables from other institutions
- Verify proper input validation in the frontend and backend
- Check for proper error handling that doesn't reveal sensitive information

## Next Steps

After completing the tests:
1. Document any issues found
2. Prioritize fixes based on severity
3. Implement fixes
4. Re-test to verify fixes
5. Consider load testing for production deployment
