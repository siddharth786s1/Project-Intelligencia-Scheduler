import apiClient from './apiClient';
import type { SchedulingJob, ScheduledSession, ScheduleGenerationSummary } from '../types/api';

const SchedulerService = {
  // Create a new scheduling job
  createSchedulingJob: async (requestData: any): Promise<SchedulingJob> => {
    const response = await apiClient.post('/scheduler/jobs', requestData);
    return response.data.data;
  },

  // Get status of a specific job
  getJobStatus: async (jobId: string): Promise<SchedulingJob> => {
    const response = await apiClient.get(`/scheduler/jobs/${jobId}`);
    return response.data.data;
  },

  // Get status of the job queue
  getQueueStatus: async (): Promise<any> => {
    const response = await apiClient.get('/scheduler/queue/status');
    return response.data.data;
  },

  // List all schedule generations
  listScheduleGenerations: async (skip = 0, limit = 10): Promise<{ items: ScheduleGenerationSummary[], total: number }> => {
    const response = await apiClient.get(`/scheduler/generations?skip=${skip}&limit=${limit}`);
    return response.data.data;
  },

  // Get a specific schedule generation
  getScheduleGeneration: async (generationId: string): Promise<ScheduleGenerationSummary> => {
    const response = await apiClient.get(`/scheduler/generations/${generationId}`);
    return response.data.data;
  },

  // Delete a schedule generation
  deleteScheduleGeneration: async (generationId: string): Promise<boolean> => {
    const response = await apiClient.delete(`/scheduler/generations/${generationId}`);
    return response.data.data;
  },

  // Get scheduled sessions for a specific generation
  getSessionsByGeneration: async (generationId: string): Promise<ScheduledSession[]> => {
    const response = await apiClient.get(`/scheduled-sessions?generation_id=${generationId}`);
    return response.data.data.items;
  },

  // Get faculty timetable
  getFacultyTimetable: async (facultyId: string): Promise<ScheduledSession[]> => {
    const response = await apiClient.get(`/scheduled-sessions/faculty/${facultyId}/timetable`);
    return response.data.data;
  },

  // Get batch timetable
  getBatchTimetable: async (batchId: string): Promise<ScheduledSession[]> => {
    const response = await apiClient.get(`/scheduled-sessions/batch/${batchId}/timetable`);
    return response.data.data;
  }
};

export default SchedulerService;
