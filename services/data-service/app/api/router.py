from fastapi import APIRouter
from app.core.config import settings

from app.api.endpoints import (
    institutions, 
    departments, 
    classrooms, 
    room_types,
    subjects,
    batches,
    faculty,
    faculty_preferences
)

api_router = APIRouter(prefix=settings.API_V1_PREFIX)

# Include all API endpoint routers
api_router.include_router(institutions.router, prefix="/institutions", tags=["institutions"])
api_router.include_router(departments.router, prefix="/departments", tags=["departments"])
api_router.include_router(classrooms.router, prefix="/classrooms", tags=["classrooms"])
api_router.include_router(room_types.router, prefix="/room_types", tags=["room_types"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["subjects"])
api_router.include_router(batches.router, prefix="/batches", tags=["batches"])
api_router.include_router(faculty.router, prefix="/faculty", tags=["faculty"])
api_router.include_router(faculty_preferences.router, prefix="/faculty-preferences", tags=["faculty_preferences"])
