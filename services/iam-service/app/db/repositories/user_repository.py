from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.models.user import User
from app.models.role import Role
from app.db.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address."""
        query = select(User).where(User.email == email).options(
            # Load the role relationship
            selectinload(User.role)
        )
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_users_by_institution(
        self, 
        institution_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        role_id: Optional[UUID] = None
    ) -> List[User]:
        """Get all users for a specific institution with optional role filter."""
        query = select(User).where(User.institution_id == institution_id)
        if role_id:
            query = query.where(User.role_id == role_id)
        query = query.options(
            # Load the role relationship
            selectinload(User.role)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_users_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
        role_id: Optional[UUID] = None,
        institution_id: Optional[UUID] = None,
        search_term: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated users with optional filters."""
        # Build the base query
        query = select(User).options(
            # Load the role relationship
            selectinload(User.role)
        )
        
        # Apply filters
        filters = []
        
        if role_id:
            filters.append(User.role_id == role_id)
        
        if institution_id:
            # Institution can be NULL for super_admin
            filters.append(
                or_(
                    User.institution_id == institution_id,
                    User.role_id == self._get_super_admin_role_id()
                )
            )
        
        if search_term:
            search_filter = or_(
                User.email.ilike(f"%{search_term}%"),
                User.first_name.ilike(f"%{search_term}%"),
                User.last_name.ilike(f"%{search_term}%")
            )
            filters.append(search_filter)
        
        # Apply all filters to the query
        if filters:
            for filter_clause in filters:
                query = query.where(filter_clause)
        
        # Paginate and return results
        return await self.paginate(query, page, page_size)
    
    async def _get_super_admin_role_id(self) -> UUID:
        """Get the super_admin role ID (helper method)."""
        query = select(Role.id).where(Role.name == "super_admin")
        result = await self.db.execute(query)
        return result.scalar_one()
