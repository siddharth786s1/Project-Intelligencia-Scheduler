import { ScheduledSession } from './scheduledSession';

export interface Timetable {
  id: string;
  name: string;
  description?: string;
  institution_id: string;
  department_id: string;
  generated_at: string;
  status: 'draft' | 'approved' | 'published';
  generation_algorithm: string;
  generation_parameters?: Record<string, any>;
  sessions: ScheduledSession[];
}

export interface TimetableGenerationOptions {
  name?: string;
  description?: string;
  departments: string[];
  batches: string[];
  algorithm: 'csp' | 'genetic';
  parameters: {
    maxIterations: number;
    populationSize: number;
    mutationRate: number;
    timeLimit: number;
  };
  constraints?: {
    hard_constraints?: string[];
    soft_constraints?: string[];
  };
  preferences?: {
    faculty_preferences_weight?: number;
    room_preferences_weight?: number;
    time_preferences_weight?: number;
  };
  time_slots?: string[];
  classrooms?: string[];
}
