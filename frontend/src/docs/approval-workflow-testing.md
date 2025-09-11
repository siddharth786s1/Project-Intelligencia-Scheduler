# ApprovalWorkflow Testing Guide

This document provides guidance for implementing tests for the ApprovalWorkflow component, which is a critical part of the timetable management system.

## Overview

The ApprovalWorkflow component manages the status transitions of timetables from draft to published state. It includes permission checks, confirmation dialogs, and API calls to update the timetable status.

## Test Prerequisites

To properly test this component, you'll need:

1. Testing libraries:
   - Vitest (or Jest) for test running
   - React Testing Library for component rendering and interaction
   - MSW (Mock Service Worker) for API mocking

2. Mock implementations:
   - AuthContext - to simulate different user roles
   - DataServiceContext - to mock API calls
   - Timetable data with different statuses

## Test Scenarios

### 1. Basic Rendering

Verify that the component renders correctly with:
- The current status displayed as a chip
- The appropriate action button based on status
- Disabled state when appropriate

### 2. User Role Testing

Test the component with different user roles:
- Admin (can perform all actions)
- Department head (can submit and approve)
- Regular user (can only submit drafts)
- Test that buttons are disabled when the user doesn't have permission

### 3. Workflow Testing

Verify the complete workflow from draft to published:
- Draft → Submitted → Approved → Published
- Verify each transition works correctly
- Verify UI updates after status changes

### 4. Error Handling

Test error conditions:
- API call failures
- Permission denied scenarios
- Network errors
- Verify appropriate error messages are displayed

### 5. Dialog Interaction

Test the confirmation dialog:
- Opens correctly with the right message
- Cancel closes without making changes
- Confirm button triggers API call
- Loading state during API calls

## Example Test Implementation

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ApprovalWorkflow from '../components/ApprovalWorkflow';
import type { Timetable } from '../types/timetable';

// Mock the contexts
vi.mock('../contexts/AuthContext', () => ({
  useAuth: vi.fn()
}));

vi.mock('../services/dataService', () => ({
  useDataService: vi.fn()
}));

describe('ApprovalWorkflow Component', () => {
  // Setup test data and mocks

  it('renders with correct status for draft timetable', () => {
    // Implementation
  });

  it('disables action button when user lacks permission', () => {
    // Implementation
  });

  it('shows confirmation dialog with correct message', async () => {
    // Implementation
  });

  it('calls API when status change is confirmed', async () => {
    // Implementation
  });

  // Additional test cases
});
```

## Integration Testing

Beyond unit tests, consider integration tests that verify:
- ApprovalWorkflow works correctly within TimetableViewer
- Status changes are reflected in the parent component
- Database state is correctly updated (in end-to-end tests)

## Test Data Setup

Create mock timetables with various statuses:

```typescript
const createMockTimetable = (status: 'draft' | 'approved' | 'published' | 'submitted' | 'rejected'): Timetable => ({
  id: 'tt-123',
  name: 'Test Timetable',
  institution_id: 'inst1',
  department_id: 'dept1',
  generated_at: '2025-09-01T10:00:00',
  status: status === 'submitted' || status === 'rejected' ? 'draft' : status,
  generation_algorithm: 'Genetic Algorithm',
  sessions: []
});
```

## Next Steps

1. Create a test file: `ApprovalWorkflow.test.tsx`
2. Implement the test scenarios described above
3. Integrate with the CI/CD pipeline
4. Add code coverage reporting to identify untested paths
