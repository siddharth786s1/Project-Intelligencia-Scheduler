-- Project Intelligencia Scheduler Database Schema
-- This schema implements a multi-tenant architecture with strict tenant isolation

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==============================================
-- IAM Service Tables
-- ==============================================

-- Institutions (Tenants)
CREATE TABLE institutions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    address TEXT,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(50),
    website VARCHAR(255),
    logo_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Roles
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(name)
);

-- Insert default roles
INSERT INTO roles (name, description) VALUES 
('super_admin', 'Super Administrator with full system access'),
('institution_admin', 'Institution Administrator'),
('department_head', 'Head of Department'),
('faculty', 'Faculty Member');

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID REFERENCES institutions(id),
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role_id UUID NOT NULL REFERENCES roles(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    UNIQUE(email),
    -- Multi-tenant constraint: null institution_id only for super_admin
    CONSTRAINT valid_institution_role CHECK (
        (institution_id IS NULL AND role_id = (SELECT id FROM roles WHERE name = 'super_admin')) OR
        (institution_id IS NOT NULL)
    )
);

-- ==============================================
-- Data Service Tables
-- ==============================================

-- Departments
CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL,
    description TEXT,
    head_user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(institution_id, code)
);

-- Room Types
CREATE TABLE room_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(institution_id, name)
);

-- Insert default room types for each institution (to be done via app logic)
-- INSERT INTO room_types (institution_id, name, description) VALUES ...

-- Classrooms
CREATE TABLE classrooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    building VARCHAR(100),
    floor VARCHAR(50),
    capacity INTEGER NOT NULL,
    room_type_id UUID NOT NULL REFERENCES room_types(id),
    is_lab BOOLEAN DEFAULT FALSE,
    has_projector BOOLEAN DEFAULT FALSE,
    has_computers BOOLEAN DEFAULT FALSE,
    additional_facilities TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(institution_id, name)
);

-- Faculty Members
CREATE TABLE faculty_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    employee_code VARCHAR(100) NOT NULL,
    department_id UUID NOT NULL REFERENCES departments(id),
    designation VARCHAR(100),
    specialization TEXT,
    max_hours_per_day INTEGER DEFAULT 6,
    max_hours_per_week INTEGER DEFAULT 25,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(institution_id, employee_code)
);

-- Faculty Preferences
CREATE TABLE faculty_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    faculty_id UUID NOT NULL REFERENCES faculty_members(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6), -- 0 = Monday, 6 = Sunday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    preference_type VARCHAR(50) NOT NULL CHECK (preference_type IN ('preferred', 'unavailable')),
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT valid_time_range CHECK (end_time > start_time)
);

-- Subjects
CREATE TABLE subjects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    department_id UUID NOT NULL REFERENCES departments(id),
    code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    credits INTEGER NOT NULL,
    lecture_hours_per_week INTEGER NOT NULL,
    lab_hours_per_week INTEGER DEFAULT 0,
    tutorial_hours_per_week INTEGER DEFAULT 0,
    requires_lab BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(institution_id, code)
);

-- Student Batches
CREATE TABLE batches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    department_id UUID NOT NULL REFERENCES departments(id),
    name VARCHAR(100) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
    strength INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(institution_id, department_id, name, academic_year)
);

-- Subject-Faculty Assignments
CREATE TABLE subject_faculty_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES subjects(id),
    faculty_id UUID NOT NULL REFERENCES faculty_members(id),
    batch_id UUID NOT NULL REFERENCES batches(id),
    academic_year VARCHAR(20) NOT NULL,
    semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(subject_id, faculty_id, batch_id, academic_year, semester),
    -- Multi-tenant constraint
    CONSTRAINT same_institution_subject_faculty CHECK (
        (SELECT institution_id FROM subjects WHERE id = subject_id) = institution_id AND
        (SELECT institution_id FROM faculty_members WHERE id = faculty_id) = institution_id AND
        (SELECT institution_id FROM batches WHERE id = batch_id) = institution_id
    )
);

-- Fixed Classes (Pre-defined slots that cannot be moved)
CREATE TABLE fixed_classes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    subject_faculty_assignment_id UUID NOT NULL REFERENCES subject_faculty_assignments(id),
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6), -- 0 = Monday, 6 = Sunday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    classroom_id UUID NOT NULL REFERENCES classrooms(id),
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT valid_time_range CHECK (end_time > start_time),
    -- Multi-tenant constraint
    CONSTRAINT same_institution_fixed_class CHECK (
        (SELECT institution_id FROM subject_faculty_assignments WHERE id = subject_faculty_assignment_id) = institution_id AND
        (SELECT institution_id FROM classrooms WHERE id = classroom_id) = institution_id
    )
);

-- ==============================================
-- Scheduler Service Tables
-- ==============================================

-- Job Status Enum
CREATE TYPE job_status AS ENUM ('pending', 'in_progress', 'completed', 'failed');

-- Timetable Generation Jobs
CREATE TABLE timetable_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    department_id UUID REFERENCES departments(id),
    academic_year VARCHAR(20) NOT NULL,
    semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
    submitted_by UUID NOT NULL REFERENCES users(id),
    status job_status DEFAULT 'pending',
    error_message TEXT,
    config JSONB NOT NULL, -- Stores weights and other configuration parameters
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Timetable Status Enum
CREATE TYPE timetable_status AS ENUM ('draft', 'submitted', 'approved', 'rejected', 'published');

-- Generated Timetables
CREATE TABLE timetables (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES timetable_jobs(id),
    rank INTEGER NOT NULL, -- Ranking among solutions (1-5)
    fitness_score FLOAT NOT NULL, -- Score from the genetic algorithm
    status timetable_status DEFAULT 'draft',
    reviewed_by UUID REFERENCES users(id),
    review_comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(job_id, rank)
);

-- Timetable Entries (Individual class schedules)
CREATE TABLE timetable_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timetable_id UUID NOT NULL REFERENCES timetables(id) ON DELETE CASCADE,
    subject_faculty_assignment_id UUID NOT NULL REFERENCES subject_faculty_assignments(id),
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6), -- 0 = Monday, 6 = Sunday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    classroom_id UUID NOT NULL REFERENCES classrooms(id),
    is_lab_session BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT valid_time_range CHECK (end_time > start_time),
    -- Multi-tenant constraint enforced via timetable_id -> job_id -> institution_id
    CONSTRAINT no_classroom_overlap UNIQUE (timetable_id, classroom_id, day_of_week, start_time),
    CONSTRAINT no_faculty_overlap UNIQUE (
        timetable_id, 
        day_of_week, 
        start_time,
        (SELECT faculty_id FROM subject_faculty_assignments 
         WHERE id = subject_faculty_assignment_id)
    ),
    CONSTRAINT no_batch_overlap UNIQUE (
        timetable_id, 
        day_of_week, 
        start_time,
        (SELECT batch_id FROM subject_faculty_assignments 
         WHERE id = subject_faculty_assignment_id)
    )
);

-- Create appropriate indexes for performance
CREATE INDEX idx_users_institution ON users(institution_id);
CREATE INDEX idx_departments_institution ON departments(institution_id);
CREATE INDEX idx_classrooms_institution ON classrooms(institution_id);
CREATE INDEX idx_subjects_department ON subjects(department_id);
CREATE INDEX idx_faculty_department ON faculty_members(department_id);
CREATE INDEX idx_batches_department ON batches(department_id);
CREATE INDEX idx_subject_faculty_batch ON subject_faculty_assignments(batch_id);
CREATE INDEX idx_timetable_jobs_institution ON timetable_jobs(institution_id);
CREATE INDEX idx_timetables_job ON timetables(job_id);
CREATE INDEX idx_timetable_entries_timetable ON timetable_entries(timetable_id);
