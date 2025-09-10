# Project Intelligencia Scheduler

A comprehensive multi-tenant Smart Classroom & Timetable Scheduler platform.

## Project Overview

The Project Intelligencia Scheduler is a sophisticated platform designed to solve the complex problem of academic timetable scheduling. It employs advanced algorithms to generate optimal timetables while respecting various constraints such as faculty availability, classroom capacity, student batch requirements, and more.

### Key Features

- **Multi-Tenant Architecture**: Support for multiple educational institutions with strict data isolation.
- **Advanced Scheduling Engine**: Hybrid algorithm combining Constraint Satisfaction Problem (CSP) and Genetic Algorithm (GA) approaches.
- **Role-Based Access Control**: Different permission levels for Super Admin, Institution Admin, Department Heads, and Faculty.
- **Comprehensive Data Management**: Manage institutions, departments, classrooms, subjects, faculty, and student batches.
- **Interactive Timetable Viewer**: View schedules by faculty, batch, or room with visual highlighting of metrics.
- **Approval Workflow**: Review and approval process for generated timetables.

## Architecture

The system follows a microservices architecture with the following components:

1. **IAM Service**: Handles authentication, authorization, and user management.
2. **Data Management Service**: Manages all entity data with CRUD operations.
3. **Scheduler Service**: The core engine that generates timetables.
4. **Frontend**: A React.js based SPA with responsive UI for managing the entire system.

## Tech Stack

### Frontend
- React.js (using Vite)
- Material-UI (MUI)
- Redux Toolkit
- Styled-components

### Backend Microservices
- Python 3.11+
- FastAPI
- Google OR-Tools
- Pydantic

### Database
- PostgreSQL
- SQLAlchemy 2.0 (with asyncpg)

### Asynchronous Processing
- RabbitMQ
- Celery

### Containerization
- Docker
- Docker Compose

## Getting Started

Detailed instructions for setting up and running the project can be found in the project's [documentation](/docs).

### Prerequisites

- Docker and Docker Compose
- Git

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/siddharth786s1/Project-Intelligencia-Scheduler.git
   cd Project-Intelligencia-Scheduler
   ```

2. Start the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Access the application at `http://localhost:8080`

## Project Structure

The project follows a well-organized structure:

- `/services`: Contains the backend microservices
  - `/iam-service`: Identity and Access Management service
  - `/data-service`: Data management service
  - `/scheduler-service`: Timetable generation service
- `/frontend`: React.js frontend application
- `/db`: Database initialization scripts
- `/nginx`: Nginx configuration for the frontend
- `/docs`: Project documentation

## Development

Each service follows a test-first approach with comprehensive unit, integration, and end-to-end tests. The development process ensures code quality through rigorous testing and adherence to best practices.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the teams behind Google OR-Tools, FastAPI, and all other open-source libraries used in this project.