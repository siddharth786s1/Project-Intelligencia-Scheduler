-- Initial setup for the databases
-- This is run after the databases are created

-- Connect to IAM service database
\c iam_service_db

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create default roles
INSERT INTO roles (id, name, description, created_at, updated_at)
VALUES 
    (uuid_generate_v4(), 'super_admin', 'Super Administrator with full system access', now(), now()),
    (uuid_generate_v4(), 'institution_admin', 'Institution Administrator', now(), now()),
    (uuid_generate_v4(), 'department_head', 'Head of Department', now(), now()),
    (uuid_generate_v4(), 'faculty', 'Faculty Member', now(), now())
ON CONFLICT (name) DO NOTHING;

-- Create super admin user with password 'admin'
INSERT INTO users (id, email, password_hash, first_name, last_name, role_id, is_active, created_at, updated_at)
VALUES (
    uuid_generate_v4(),
    'admin@scheduler.edu',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
    'System',
    'Admin',
    (SELECT id FROM roles WHERE name = 'super_admin'),
    true,
    now(),
    now()
) ON CONFLICT (email) DO NOTHING;

-- Connect to data service database
\c data_service_db

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Connect to scheduler service database
\c scheduler_service_db

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
