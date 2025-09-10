# Data Service

This microservice is responsible for managing educational data entities such as institutions, departments, classrooms, and room types.

## Features

- Multi-tenant architecture with proper isolation
- RESTful API endpoints for CRUD operations
- JWT-based authentication and authorization
- Comprehensive test coverage

## API Endpoints

### Institutions

- `POST /api/v1/institutions/` - Create a new institution (Super Admin only)
- `GET /api/v1/institutions/` - List all institutions (filtered by user's permissions)
- `GET /api/v1/institutions/{institution_id}` - Get a specific institution
- `PATCH /api/v1/institutions/{institution_id}` - Update an institution
- `DELETE /api/v1/institutions/{institution_id}` - Delete an institution (Super Admin only)

### Departments

- `POST /api/v1/departments/` - Create a new department
- `GET /api/v1/departments/` - List all departments for the current institution
- `GET /api/v1/departments/{department_id}` - Get a specific department
- `PATCH /api/v1/departments/{department_id}` - Update a department
- `DELETE /api/v1/departments/{department_id}` - Delete a department

### Classrooms

- `POST /api/v1/classrooms/` - Create a new classroom
- `GET /api/v1/classrooms/` - List all classrooms for the current institution
- `GET /api/v1/classrooms/{classroom_id}` - Get a specific classroom
- `PATCH /api/v1/classrooms/{classroom_id}` - Update a classroom
- `DELETE /api/v1/classrooms/{classroom_id}` - Delete a classroom

### Room Types

- `POST /api/v1/room_types/` - Create a new room type
- `GET /api/v1/room_types/` - List all room types for the current institution
- `GET /api/v1/room_types/{room_type_id}` - Get a specific room type
- `PATCH /api/v1/room_types/{room_type_id}` - Update a room type
- `DELETE /api/v1/room_types/{room_type_id}` - Delete a room type

## Development

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the service:
   ```bash
   uvicorn app.main:app --reload
   ```

### Testing

Run the tests using:
```bash
pytest
```

## Docker

Build and run using Docker:
```bash
docker build -t data-service .
docker run -p 8000:8000 data-service
```

Or use docker-compose:
```bash
docker-compose up -d data-service
```
