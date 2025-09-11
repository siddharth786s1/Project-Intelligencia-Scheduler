export interface ScheduledSession {
  id: string;
  subject_id: string;
  subject_name: string;
  subject_code: string;
  faculty_id: string;
  faculty_name: string;
  batch_id: string;
  batch_name: string;
  classroom_id: string;
  classroom_name: string;
  day_of_week: number; // 0 = Sunday, 1 = Monday, etc.
  start_time: string; // HH:MM:SS format
  end_time: string; // HH:MM:SS format
  session_type: 'lecture' | 'tutorial' | 'practical';
  created_at?: string;
  updated_at?: string;
}
