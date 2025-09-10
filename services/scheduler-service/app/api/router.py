from fastapi import APIRouter
from app.core.config import settings

from app.api.endpoints import scheduler

api_router = APIRouter(prefix=settings.API_V1_PREFIX)

# Include API endpoint routers
api_router.include_router(scheduler.router)
