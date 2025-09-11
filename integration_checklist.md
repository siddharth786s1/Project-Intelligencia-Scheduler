# Frontend-Scheduler Integration Checklist

## Environment Setup

- [ ] All required services are running in Docker containers
- [ ] Database has been initialized with test data
- [ ] API endpoints are accessible

## Authentication Tests

- [ ] Login with test credentials is successful
- [ ] Authentication token is properly stored
- [ ] Protected routes are accessible after login

## Data Service Connection Tests

- [ ] Frontend can retrieve departments list
- [ ] Frontend can retrieve batches list
- [ ] Frontend can retrieve faculty list
- [ ] Frontend can retrieve subjects list
- [ ] Frontend can retrieve classrooms list
- [ ] Frontend can retrieve time slots list

## Timetable Generator Component Tests

- [ ] Component loads without errors
- [ ] Stepper UI functions correctly
- [ ] Department/batch selection works
- [ ] Algorithm selection (CSP vs. Genetic) works
- [ ] Algorithm parameters can be adjusted
- [ ] Job submission works and returns a job ID
- [ ] Progress tracking displays correctly
- [ ] Success/failure states are properly handled

## Job Management Tests

- [ ] Queue status endpoint returns data
- [ ] Job status is properly updated in the UI
- [ ] Job cancellation works (if implemented)

## Timetable Viewer Component Tests

- [x] Component loads without errors
- [x] Generated timetables can be viewed
- [x] Filtering by batch works
- [x] Filtering by faculty works
- [x] Filtering by classroom works
- [x] Different view modes (batch/faculty/classroom) work correctly
- [x] Timetable data is displayed in the correct format
- [x] Time slot and session information is accurate
- [x] ApprovalWorkflow component is integrated
- [x] Timetable status changes reflect in UI
- [x] Status change permissions work correctly
- [x] Approval dialog shows correctly
- [x] Status transitions are saved to the database
- [x] ApprovalWorkflow component has unit tests

## Dashboard Integration Tests

- [ ] Dashboard shows recent timetables
- [ ] Dashboard shows queue status
- [ ] Statistics are displayed correctly

## Error Handling Tests

- [ ] Invalid input is properly validated
- [ ] Failed jobs show appropriate error messages
- [ ] Network errors are handled gracefully
- [ ] Authentication failures redirect to login

## Performance Tests

- [ ] UI remains responsive during job submission
- [ ] Large timetables load and render without performance issues
- [ ] Multiple simultaneous operations work correctly

## Notes

- Document any issues found during testing
- Note any workarounds implemented
- Identify areas for improvement
