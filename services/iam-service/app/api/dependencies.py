from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Generator, List
from uuid import UUID

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.db.repositories.user_repository import UserRepository
from app.models.role import Role

async def get_roles(db: AsyncSession = Depends(get_db)) -> List[Role]:
    """Get all roles."""
    query = select(Role)
    result = await db.execute(query)
    return result.scalars().all()

async def check_institution_access(
    institution_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> bool:
    """Check if user has access to the given institution."""
    # Super admin has access to all institutions
    if current_user.role.name == "super_admin":
        return True
    
    # Other users can only access their own institution
    return current_user.institution_id == institution_id
