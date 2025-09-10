# Scheduler Service

The Scheduler Service is responsible for generating optimal timetables based on the data stored in the Data Service. It uses a hybrid approach combining Constraint Satisfaction Problem (CSP) and Genetic Algorithm (GA) techniques to create feasible timetables that satisfy both hard constraints (must be met) and soft constraints (preferences).

## Features

- Timetable generation with hard and soft constraints
- Asynchronous job processing for long-running scheduling tasks
- Real-time job status tracking
- Integration with Data Service for entity management
- Support for customizable optimization goals
- Schedule quality metrics calculation

## Architecture

The service follows a layered architecture:

1. **API Layer**: REST endpoints for user interactions
2. **Service Layer**: Business logic for scheduling operations
3. **Algorithm Layer**: Implementation of scheduling algorithms
4. **Data Layer**: Integration with Data Service

## Scheduling Algorithms

The service implements multiple scheduling algorithms:

1. **CSP Scheduler**: Uses Google OR-Tools CP-SAT solver to find a feasible solution satisfying all hard constraints.
2. **GA Scheduler**: Uses genetic algorithm with custom operators to optimize a solution based on soft constraints and preferences.
3. **Hybrid Scheduler**: Combines CSP and GA for optimal results.

## Hard Constraints

These are constraints that must be satisfied for a valid schedule:

- Faculty can only teach one session at a time
- Batch can only attend one session at a time
- Classroom can only host one session at a time
- Each batch-subject pair must be scheduled
- Respect faculty availability
- Respect classroom capacity

## Soft Constraints

These are preferences that should be satisfied but can be violated if necessary:

- Faculty preferred subjects
- Faculty preferred time slots
- Faculty preferred rooms
- Minimize gaps in faculty schedules
- Minimize gaps in batch schedules
- Balanced workload for faculty
- Distribute sessions across the week

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose

### Installation

1. Clone the repository
2. Navigate to the scheduler-service directory
3. Build the Docker image:

```bash
docker build -t scheduler-service .
```

### Running the Service

```bash
docker-compose up -d
```

### API Documentation

The API documentation is available at `/docs` or `/redoc` when the service is running.

## Usage

To generate a new timetable:

1. Create a new scheduling job with your requirements
2. Monitor the job status
3. When complete, retrieve the generated schedule
4. View metrics and analyze the quality of the schedule

## Environment Variables

- `DATA_SERVICE_URL`: URL of the Data Service
- `AUTH_SERVICE_URL`: URL of the IAM Service
- `MAX_SCHEDULING_ATTEMPTS`: Maximum number of attempts for scheduling
- `TIMEOUT_SECONDS`: Maximum time for scheduling algorithm execution
- `POPULATION_SIZE`: Population size for genetic algorithm
- `MAX_GENERATIONS`: Maximum number of generations for genetic algorithm
- `DEFAULT_MUTATION_RATE`: Mutation rate for genetic algorithm
- `DEFAULT_CROSSOVER_RATE`: Crossover rate for genetic algorithm

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
