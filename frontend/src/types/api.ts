// API types reflecting the backend structure

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  role: string;
  institution_id?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Institution {
  id: string;
  name: string;
  code: string;
  address: string;
  city: string;
  state: string;
  country: string;
  pincode: string;
}

export interface Department {
  id: string;
  name: string;
  code: string;
  institution_id: string;
}

export interface Faculty {
  id: string;
  name: string;
  email: string;
  employee_id: string;
  department_id: string;
  designation: string;
  max_weekly_load_hours: number;
}

export interface Subject {
  id: string;
  name: string;
  code: string;
  credits: number;
  weekly_hours: number;
  department_id: string;
}

export interface Batch {
  id: string;
  name: string;
  department_id: string;
  year: number;
  semester: number;
}

export interface Classroom {
  id: string;
  name: string;
  building: string;
  floor: number;
  capacity: number;
  room_type_id: string;
}

export interface TimeSlot {
  id: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
}

export interface SchedulingJob {
  job_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';
  message: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  progress?: number;
  error?: string;
}

export interface ScheduledSession {
  id: string;
  batch_id: string;
  subject_id: string;
  faculty_id: string;
  classroom_id: string;
  time_slot_id: string;
  generation_id: string;
  is_canceled: boolean;
}

export interface ScheduleGenerationSummary {
  id: string;
  name: string;
  description: string;
  created_at: string;
  session_count: number;
  hard_constraint_violations: number;
  soft_constraint_violations: number;
  faculty_satisfaction_score: number;
  batch_satisfaction_score: number;
  room_utilization: number;
}
