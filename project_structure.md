# Project Intelligencia Scheduler - File Structure

```
/
├── docker-compose.yml
├── README.md
├── services/
│   ├── iam-service/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── auth.py
│   │   │   │   │   └── users.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── router.py
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py
│   │   │   │   ├── security.py
│   │   │   │   └── errors.py
│   │   │   ├── db/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── database.py
│   │   │   │   └── repositories/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── base.py
│   │   │   │       └── user_repository.py
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py
│   │   │   │   ├── role.py
│   │   │   │   └── tenant.py
│   │   │   └── schemas/
│   │   │       ├── __init__.py
│   │   │       ├── user.py
│   │   │       ├── auth.py
│   │   │       └── response.py
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   ├── test_api/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_auth.py
│   │   │   │   └── test_users.py
│   │   │   └── test_core/
│   │   │       ├── __init__.py
│   │   │       └── test_security.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── alembic.ini
│   │   ├── alembic/
│   │   │   ├── README
│   │   │   ├── env.py
│   │   │   └── versions/
│   │   └── README.md
│   ├── data-service/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── institutions.py
│   │   │   │   │   ├── departments.py
│   │   │   │   │   ├── classrooms.py
│   │   │   │   │   ├── subjects.py
│   │   │   │   │   ├── faculty.py
│   │   │   │   │   ├── batches.py
│   │   │   │   │   └── imports.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── router.py
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py
│   │   │   │   └── errors.py
│   │   │   ├── db/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── database.py
│   │   │   │   └── repositories/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── base.py
│   │   │   │       ├── institution_repository.py
│   │   │   │       ├── department_repository.py
│   │   │   │       ├── classroom_repository.py
│   │   │   │       ├── subject_repository.py
│   │   │   │       ├── faculty_repository.py
│   │   │   │       └── batch_repository.py
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── institution.py
│   │   │   │   ├── department.py
│   │   │   │   ├── classroom.py
│   │   │   │   ├── subject.py
│   │   │   │   ├── faculty.py
│   │   │   │   └── batch.py
│   │   │   └── schemas/
│   │   │       ├── __init__.py
│   │   │       ├── institution.py
│   │   │       ├── department.py
│   │   │       ├── classroom.py
│   │   │       ├── subject.py
│   │   │       ├── faculty.py
│   │   │       ├── batch.py
│   │   │       ├── import.py
│   │   │       └── response.py
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   └── test_api/
│   │   │       ├── __init__.py
│   │   │       ├── test_institutions.py
│   │   │       ├── test_departments.py
│   │   │       ├── test_classrooms.py
│   │   │       ├── test_subjects.py
│   │   │       ├── test_faculty.py
│   │   │       ├── test_batches.py
│   │   │       └── test_imports.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── alembic.ini
│   │   ├── alembic/
│   │   │   ├── README
│   │   │   ├── env.py
│   │   │   └── versions/
│   │   └── README.md
│   ├── scheduler-service/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── jobs.py
│   │   │   │   │   └── timetables.py
│   │   │   │   ├── dependencies.py
│   │   │   │   └── router.py
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py
│   │   │   │   └── errors.py
│   │   │   ├── db/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── database.py
│   │   │   │   └── repositories/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── base.py
│   │   │   │       ├── job_repository.py
│   │   │   │       └── timetable_repository.py
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── job.py
│   │   │   │   └── timetable.py
│   │   │   ├── schemas/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── job.py
│   │   │   │   ├── timetable.py
│   │   │   │   └── response.py
│   │   │   ├── engine/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── constraints/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── hard_constraints.py
│   │   │   │   │   └── soft_constraints.py
│   │   │   │   ├── csp_solver.py
│   │   │   │   ├── genetic_algorithm.py
│   │   │   │   ├── solution.py
│   │   │   │   ├── timeslots.py
│   │   │   │   └── fitness.py
│   │   │   └── tasks/
│   │   │       ├── __init__.py
│   │   │       ├── celery_app.py
│   │   │       └── scheduler_tasks.py
│   │   ├── worker/
│   │   │   ├── __init__.py
│   │   │   ├── celery_worker.py
│   │   │   └── Dockerfile
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   ├── test_api/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_jobs.py
│   │   │   │   └── test_timetables.py
│   │   │   └── test_engine/
│   │   │       ├── __init__.py
│   │   │       ├── test_csp_solver.py
│   │   │       ├── test_genetic_algorithm.py
│   │   │       ├── test_constraints.py
│   │   │       └── test_fitness.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── alembic.ini
│   │   ├── alembic/
│   │   │   ├── README
│   │   │   ├── env.py
│   │   │   └── versions/
│   │   └── README.md
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── index.css
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Navbar.jsx
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   ├── LoadingSpinner.jsx
│   │   │   │   └── ErrorAlert.jsx
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.jsx
│   │   │   │   └── RegisterForm.jsx
│   │   │   ├── dashboard/
│   │   │   │   ├── DashboardSummary.jsx
│   │   │   │   └── StatusCards.jsx
│   │   │   ├── data-management/
│   │   │   │   ├── InstitutionForm.jsx
│   │   │   │   ├── DepartmentForm.jsx
│   │   │   │   ├── ClassroomForm.jsx
│   │   │   │   ├── SubjectForm.jsx
│   │   │   │   ├── FacultyForm.jsx
│   │   │   │   ├── BatchForm.jsx
│   │   │   │   ├── DataTable.jsx
│   │   │   │   └── ImportDataForm.jsx
│   │   │   ├── timetable/
│   │   │   │   ├── GeneratorForm.jsx
│   │   │   │   ├── TimetableViewer.jsx
│   │   │   │   ├── JobStatusList.jsx
│   │   │   │   ├── ResultComparison.jsx
│   │   │   │   └── ApprovalWorkflow.jsx
│   │   │   └── reports/
│   │   │       ├── FacultyLoadReport.jsx
│   │   │       └── ResourceUtilizationReport.jsx
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   │   ├── authSlice.js
│   │   │   │   └── authAPI.js
│   │   │   ├── institutions/
│   │   │   │   ├── institutionsSlice.js
│   │   │   │   └── institutionsAPI.js
│   │   │   ├── departments/
│   │   │   │   ├── departmentsSlice.js
│   │   │   │   └── departmentsAPI.js
│   │   │   ├── classrooms/
│   │   │   │   ├── classroomsSlice.js
│   │   │   │   └── classroomsAPI.js
│   │   │   ├── subjects/
│   │   │   │   ├── subjectsSlice.js
│   │   │   │   └── subjectsAPI.js
│   │   │   ├── faculty/
│   │   │   │   ├── facultySlice.js
│   │   │   │   └── facultyAPI.js
│   │   │   ├── batches/
│   │   │   │   ├── batchesSlice.js
│   │   │   │   └── batchesAPI.js
│   │   │   ├── jobs/
│   │   │   │   ├── jobsSlice.js
│   │   │   │   └── jobsAPI.js
│   │   │   └── timetables/
│   │   │       ├── timetablesSlice.js
│   │   │       └── timetablesAPI.js
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── InstitutionsPage.jsx
│   │   │   ├── DepartmentsPage.jsx
│   │   │   ├── ClassroomsPage.jsx
│   │   │   ├── SubjectsPage.jsx
│   │   │   ├── FacultyPage.jsx
│   │   │   ├── BatchesPage.jsx
│   │   │   ├── ImportDataPage.jsx
│   │   │   ├── GenerateTimetablePage.jsx
│   │   │   ├── JobsListPage.jsx
│   │   │   ├── TimetableViewerPage.jsx
│   │   │   └── ReportsPage.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── localStorage.js
│   │   ├── utils/
│   │   │   ├── auth.js
│   │   │   ├── dates.js
│   │   │   └── validation.js
│   │   ├── hooks/
│   │   │   ├── useAuth.js
│   │   │   ├── usePagination.js
│   │   │   └── useToast.js
│   │   ├── theme/
│   │   │   └── index.js
│   │   └── store.js
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── logo.svg
│   │   └── robots.txt
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   ├── jest.config.js
│   ├── .eslintrc.js
│   ├── .prettierrc
│   ├── tests/
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.test.jsx
│   │   │   │   └── RegisterForm.test.jsx
│   │   │   └── timetable/
│   │   │       ├── GeneratorForm.test.jsx
│   │   │       └── TimetableViewer.test.jsx
│   │   └── features/
│   │       ├── auth/
│   │       │   └── authSlice.test.js
│   │       └── jobs/
│   │           └── jobsSlice.test.js
│   ├── Dockerfile
│   └── README.md
├── db/
│   ├── init/
│   │   └── init.sql
│   └── data/
├── nginx/
│   ├── nginx.conf
│   └── Dockerfile
└── docs/
    ├── api/
    │   └── openapi.yaml
    └── schema.sql
```
