# IAM Service

Identity and Access Management Service for Project Intelligencia Scheduler.

## Features

- User registration and authentication
- Role-based access control
- JWT-based security
- Multi-tenant architecture with strict isolation

## Roles

- **Super Admin**: Full system access, can manage all institutions
- **Institution Admin**: Full access to their institution
- **Department Head**: Access to their department
- **Faculty**: Limited access to their own data

## API Endpoints

The service provides the following API endpoints:

### Authentication
- `POST /api/v1/auth/login`: Login with email and password
- `POST /api/v1/auth/refresh`: Refresh access token

### Users
- `GET /api/v1/users`: Get all users (paginated)
- `GET /api/v1/users/{id}`: Get user by ID
- `POST /api/v1/users`: Create a new user
- `PUT /api/v1/users/{id}`: Update a user
- `DELETE /api/v1/users/{id}`: Delete a user

### Roles
- `GET /api/v1/roles`: Get all roles

## Setup and Running

### Prerequisites
- Python 3.11+
- PostgreSQL database

### Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export DATABASE_USER=postgres
   export DATABASE_PASSWORD=postgres
   export DATABASE_HOST=localhost
   export DATABASE_PORT=5432
   export DATABASE_NAME=iam_service_db
   export JWT_SECRET_KEY=your_secret_key
   ```

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Run the service:
   ```bash
   uvicorn app.main:app --reload
   ```

### Running with Docker

1. Build the Docker image:
   ```bash
   docker build -t iam-service .
   ```

2. Run the container:
   ```bash
   docker run -d -p 8000:8000 --name iam-service iam-service
   ```

## Testing

Run the tests using pytest:

```bash
pytest
```
