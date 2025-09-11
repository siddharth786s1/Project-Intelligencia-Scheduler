import { useContext, createContext } from 'react';
import apiClient from './apiClient';
import type { 
  Institution, 
  Department, 
  Faculty, 
  Subject, 
  Batch,
  Classroom,
  TimeSlot,
  SchedulingConstraint
} from '../types/api';

import type { Timetable, TimetableGenerationOptions } from '../types/timetable';

interface DataServiceContextValue {
  // Institution endpoints
  getInstitutions: (skip?: number, limit?: number) => Promise<{ data: Institution[], total: number }>;
  getInstitution: (id: string) => Promise<{ data: Institution }>;
  createInstitution: (data: Partial<Institution>) => Promise<{ data: Institution }>;
  updateInstitution: (id: string, data: Partial<Institution>) => Promise<{ data: Institution }>;
  deleteInstitution: (id: string) => Promise<void>;
  
  // Department endpoints
  getDepartments: (skip?: number, limit?: number) => Promise<{ data: Department[], total: number }>;
  getDepartment: (id: string) => Promise<{ data: Department }>;
  createDepartment: (data: Partial<Department>) => Promise<{ data: Department }>;
  updateDepartment: (id: string, data: Partial<Department>) => Promise<{ data: Department }>;
  deleteDepartment: (id: string) => Promise<void>;
  
  // Faculty endpoints
  getFaculty: (skip?: number, limit?: number, departmentId?: string) => Promise<{ data: Faculty[], total: number }>;
  getFacultyMember: (id: string) => Promise<{ data: Faculty }>;
  createFaculty: (data: Partial<Faculty>) => Promise<{ data: Faculty }>;
  updateFaculty: (id: string, data: Partial<Faculty>) => Promise<{ data: Faculty }>;
  deleteFaculty: (id: string) => Promise<void>;
  
  // Subject endpoints
  getSubjects: (skip?: number, limit?: number, departmentId?: string) => Promise<{ data: Subject[], total: number }>;
  getSubject: (id: string) => Promise<{ data: Subject }>;
  createSubject: (data: Partial<Subject>) => Promise<{ data: Subject }>;
  updateSubject: (id: string, data: Partial<Subject>) => Promise<{ data: Subject }>;
  deleteSubject: (id: string) => Promise<void>;
  
  // Batch endpoints
  getBatches: (skip?: number, limit?: number, departmentId?: string) => Promise<{ data: Batch[], total: number }>;
  getBatch: (id: string) => Promise<{ data: Batch }>;
  createBatch: (data: Partial<Batch>) => Promise<{ data: Batch }>;
  updateBatch: (id: string, data: Partial<Batch>) => Promise<{ data: Batch }>;
  deleteBatch: (id: string) => Promise<void>;
  
  // Classroom endpoints
  getClassrooms: (skip?: number, limit?: number) => Promise<{ data: Classroom[], total: number }>;
  getClassroom: (id: string) => Promise<{ data: Classroom }>;
  createClassroom: (data: Partial<Classroom>) => Promise<{ data: Classroom }>;
  updateClassroom: (id: string, data: Partial<Classroom>) => Promise<{ data: Classroom }>;
  deleteClassroom: (id: string) => Promise<void>;
  
  // TimeSlot endpoints
  getTimeSlots: (skip?: number, limit?: number) => Promise<{ data: TimeSlot[], total: number }>;
  getTimeSlot: (id: string) => Promise<{ data: TimeSlot }>;
  createTimeSlot: (data: Partial<TimeSlot>) => Promise<{ data: TimeSlot }>;
  updateTimeSlot: (id: string, data: Partial<TimeSlot>) => Promise<{ data: TimeSlot }>;
  deleteTimeSlot: (id: string) => Promise<void>;
  
  // Timetable endpoints
  getTimetables: (skip?: number, limit?: number, institutionId?: string, departmentId?: string) => Promise<{ data: Timetable[], total: number }>;
  getTimetable: (id: string) => Promise<{ data: Timetable }>;
  generateTimetable: (options: TimetableGenerationOptions) => Promise<{ data: { job_id: string } }>;
  getGenerationStatus: (jobId: string) => Promise<{ data: { status: 'pending' | 'processing' | 'completed' | 'failed', progress?: number, message?: string, timetable_id?: string } }>;
  updateTimetableStatus: (id: string, status: 'draft' | 'approved' | 'published') => Promise<{ data: Timetable }>;
  deleteTimetable: (id: string) => Promise<void>;
}

export const DataServiceContext = createContext<DataServiceContextValue | null>(null);

export const useDataService = () => {
  const context = useContext(DataServiceContext);
  if (!context) {
    throw new Error('useDataService must be used within a DataServiceProvider');
  }
  return context;
};

const DataService: DataServiceContextValue = {
  // Institution endpoints
  getInstitutions: async (skip = 0, limit = 10) => {
    const response = await apiClient.get(`/institutions?skip=${skip}&limit=${limit}`);
    return { data: response.data.data.items, total: response.data.data.total };
  },

  getInstitution: async (id: string) => {
    const response = await apiClient.get(`/institutions/${id}`);
    return { data: response.data.data };
  },

  createInstitution: async (data: Partial<Institution>) => {
    const response = await apiClient.post('/institutions', data);
    return { data: response.data.data };
  },

  updateInstitution: async (id: string, data: Partial<Institution>) => {
    const response = await apiClient.put(`/institutions/${id}`, data);
    return { data: response.data.data };
  },

  deleteInstitution: async (id: string) => {
    await apiClient.delete(`/institutions/${id}`);
  },

  // Department endpoints
  getDepartments: async (skip = 0, limit = 10) => {
    const response = await apiClient.get(`/departments?skip=${skip}&limit=${limit}`);
    return { data: response.data.data.items, total: response.data.data.total };
  },

  getDepartment: async (id: string) => {
    const response = await apiClient.get(`/departments/${id}`);
    return { data: response.data.data };
  },

  createDepartment: async (data: Partial<Department>) => {
    const response = await apiClient.post('/departments', data);
    return { data: response.data.data };
  },

  updateDepartment: async (id: string, data: Partial<Department>) => {
    const response = await apiClient.put(`/departments/${id}`, data);
    return { data: response.data.data };
  },
  
  deleteDepartment: async (id: string) => {
    await apiClient.delete(`/departments/${id}`);
  },

  // Faculty endpoints
  getFaculty: async (skip = 0, limit = 10, departmentId?: string) => {
    let url = `/faculty?skip=${skip}&limit=${limit}`;
    if (departmentId) url += `&department_id=${departmentId}`;
    
    const response = await apiClient.get(url);
    return { data: response.data.data.items, total: response.data.data.total };
  },

  getFacultyMember: async (id: string) => {
    const response = await apiClient.get(`/faculty/${id}`);
    return { data: response.data.data };
  },

  createFaculty: async (data: Partial<Faculty>) => {
    const response = await apiClient.post('/faculty', data);
    return { data: response.data.data };
  },

  updateFaculty: async (id: string, data: Partial<Faculty>) => {
    const response = await apiClient.put(`/faculty/${id}`, data);
    return { data: response.data.data };
  },

  deleteFaculty: async (id: string) => {
    await apiClient.delete(`/faculty/${id}`);
  },

  // Subject endpoints
  getSubjects: async (skip = 0, limit = 10, departmentId?: string) => {
    let url = `/subjects?skip=${skip}&limit=${limit}`;
    if (departmentId) url += `&department_id=${departmentId}`;
    
    const response = await apiClient.get(url);
    return { data: response.data.data.items, total: response.data.data.total };
  },

  getSubject: async (id: string) => {
    const response = await apiClient.get(`/subjects/${id}`);
    return { data: response.data.data };
  },

  createSubject: async (data: Partial<Subject>) => {
    const response = await apiClient.post('/subjects', data);
    return { data: response.data.data };
  },

  updateSubject: async (id: string, data: Partial<Subject>) => {
    const response = await apiClient.put(`/subjects/${id}`, data);
    return { data: response.data.data };
  },

  deleteSubject: async (id: string) => {
    await apiClient.delete(`/subjects/${id}`);
  },

  // Batch endpoints
  getBatches: async (skip = 0, limit = 10, departmentId?: string) => {
    let url = `/batches?skip=${skip}&limit=${limit}`;
    if (departmentId) url += `&department_id=${departmentId}`;
    
    const response = await apiClient.get(url);
    return { data: response.data.data.items, total: response.data.data.total };
  },

  getBatch: async (id: string) => {
    const response = await apiClient.get(`/batches/${id}`);
    return { data: response.data.data };
  },

  createBatch: async (data: Partial<Batch>) => {
    const response = await apiClient.post('/batches', data);
    return { data: response.data.data };
  },

  updateBatch: async (id: string, data: Partial<Batch>) => {
    const response = await apiClient.put(`/batches/${id}`, data);
    return { data: response.data.data };
  },

  deleteBatch: async (id: string) => {
    await apiClient.delete(`/batches/${id}`);
  },

  // Classroom endpoints
  getClassrooms: async (skip = 0, limit = 10) => {
    const response = await apiClient.get(`/classrooms?skip=${skip}&limit=${limit}`);
    return { data: response.data.data.items, total: response.data.data.total };
  },

  getClassroom: async (id: string) => {
    const response = await apiClient.get(`/classrooms/${id}`);
    return { data: response.data.data };
  },

  createClassroom: async (data: Partial<Classroom>) => {
    const response = await apiClient.post('/classrooms', data);
    return { data: response.data.data };
  },

  updateClassroom: async (id: string, data: Partial<Classroom>) => {
    const response = await apiClient.put(`/classrooms/${id}`, data);
    return { data: response.data.data };
  },

  deleteClassroom: async (id: string) => {
    await apiClient.delete(`/classrooms/${id}`);
  },

  // TimeSlot endpoints
  getTimeSlots: async (skip = 0, limit = 10) => {
    const response = await apiClient.get(`/time-slots?skip=${skip}&limit=${limit}`);
    return { data: response.data.data.items, total: response.data.data.total };
  },

  getTimeSlot: async (id: string) => {
    const response = await apiClient.get(`/time-slots/${id}`);
    return { data: response.data.data };
  },

  createTimeSlot: async (data: Partial<TimeSlot>) => {
    const response = await apiClient.post('/time-slots', data);
    return { data: response.data.data };
  },

  updateTimeSlot: async (id: string, data: Partial<TimeSlot>) => {
    const response = await apiClient.put(`/time-slots/${id}`, data);
    return { data: response.data.data };
  },

  deleteTimeSlot: async (id: string) => {
    await apiClient.delete(`/time-slots/${id}`);
  },
  
  // Timetable endpoints
  getTimetables: async (skip = 0, limit = 10, institutionId?: string, departmentId?: string) => {
    let url = `/timetables?skip=${skip}&limit=${limit}`;
    if (institutionId) url += `&institution_id=${institutionId}`;
    if (departmentId) url += `&department_id=${departmentId}`;
    
    const response = await apiClient.get(url);
    return { data: response.data.data.items, total: response.data.data.total };
  },
  
  getTimetable: async (id: string) => {
    const response = await apiClient.get(`/timetables/${id}`);
    return { data: response.data.data };
  },
  
  generateTimetable: async (options: TimetableGenerationOptions) => {
    const response = await apiClient.post('/timetables/generate', options);
    return { data: response.data.data };
  },
  
  getGenerationStatus: async (jobId: string) => {
    const response = await apiClient.get(`/timetables/jobs/${jobId}`);
    return { data: response.data.data };
  },
  
  updateTimetableStatus: async (id: string, status: 'draft' | 'approved' | 'published') => {
    const response = await apiClient.patch(`/timetables/${id}/status`, { status });
    return { data: response.data.data };
  },
  
  deleteTimetable: async (id: string) => {
    await apiClient.delete(`/timetables/${id}`);
  },
};

export default DataService;
