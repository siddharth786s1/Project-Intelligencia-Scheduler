from fastapi import APIRouter, Depends

from app.api.endpoints import auth, users
from app.api import dependencies
from app.core.config import settings

# Create API router
api_router = APIRouter(prefix=settings.API_V1_PREFIX)

# Add route for roles
@api_router.get("/roles", tags=["Roles"])
async def get_roles(roles=Depends(dependencies.get_roles)):
    return roles

# Include endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
