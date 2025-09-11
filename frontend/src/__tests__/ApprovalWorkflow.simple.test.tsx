import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import ApprovalWorkflow from '../components/ApprovalWorkflow';
import type { Timetable } from '../types/timetable';
import { DataServiceContext } from '../services/dataService';
// We'll use a mock directly since AuthContext is not exported

// Create mock providers for testing
const mockUpdateTimetableStatus = vi.fn().mockResolvedValue({ data: {} });

const MockDataServiceProvider = ({ children }: { children: React.ReactNode }) => {
  return (
    <DataServiceContext.Provider value={{
      updateTimetableStatus: mockUpdateTimetableStatus,
      // Add other required methods as empty stubs
      getInstitutions: vi.fn(),
      getInstitution: vi.fn(),
      createInstitution: vi.fn(),
      updateInstitution: vi.fn(),
      deleteInstitution: vi.fn(),
      getDepartments: vi.fn(),
      getDepartment: vi.fn(),
      createDepartment: vi.fn(),
      updateDepartment: vi.fn(),
      deleteDepartment: vi.fn(),
      getFaculty: vi.fn(),
      getFacultyMember: vi.fn(),
      createFaculty: vi.fn(),
      updateFaculty: vi.fn(),
      deleteFaculty: vi.fn(),
      getSubjects: vi.fn(),
      getSubject: vi.fn(),
      createSubject: vi.fn(),
      updateSubject: vi.fn(),
      deleteSubject: vi.fn(),
      getBatches: vi.fn(),
      getBatch: vi.fn(),
      createBatch: vi.fn(),
      updateBatch: vi.fn(),
      deleteBatch: vi.fn(),
      getClassrooms: vi.fn(),
      getClassroom: vi.fn(),
      createClassroom: vi.fn(),
      updateClassroom: vi.fn(),
      deleteClassroom: vi.fn(),
      getTimeSlots: vi.fn(),
      getTimeSlot: vi.fn(),
      createTimeSlot: vi.fn(),
      updateTimeSlot: vi.fn(),
      deleteTimeSlot: vi.fn(),
      getTimetables: vi.fn(),
      getTimetable: vi.fn(),
      generateTimetable: vi.fn(),
      getGenerationStatus: vi.fn(),
      deleteTimetable: vi.fn(),
    }}>
      {children}
    </DataServiceContext.Provider>
  );
};

const mockHasRole = vi.fn((role: string) => role === 'admin');

// Just mock the hook instead
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 'user1', name: 'Test User', email: 'test@example.com' },
    isAuthenticated: true,
    isLoading: false,
    error: null,
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    clearError: vi.fn(),
    hasRole: mockHasRole,
    setCurrentInstitution: vi.fn(),
    currentInstitutionId: null
  })
}));

describe('ApprovalWorkflow Component', () => {
  const mockTimetable: Timetable = {
    id: 'tt-123',
    name: 'Test Timetable',
    institution_id: 'inst1',
    department_id: 'dept1',
    generated_at: '2025-09-01T10:00:00',
    status: 'draft',
    generation_algorithm: 'Genetic Algorithm',
    sessions: []
  };
  
  const mockOnStatusChange = vi.fn();
  
  beforeEach(() => {
    vi.clearAllMocks();
  });
  
  it('renders with correct status', () => {
    render(
      <MockDataServiceProvider>
        <ApprovalWorkflow timetable={mockTimetable} onStatusChange={mockOnStatusChange} />
      </MockDataServiceProvider>
    );
    
    expect(screen.getByText('Status:')).toBeDefined();
    expect(screen.getByText('DRAFT')).toBeDefined();
    expect(screen.getByText('Submit for Approval')).toBeDefined();
  });
});
