from uuid import UUID
from typing import List, Optional, Dict, Any, Tuple

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base import BaseRepository
from app.models.faculty import Faculty
from app.models.department import Department


class FacultyRepository(BaseRepository):
    """Repository for managing faculty entities."""
    
    async def create(self, db: AsyncSession, data: Dict[str, Any], institution_id: UUID) -> Faculty:
        """Create a new faculty member."""
        # Set the institution_id from the authenticated user's context
        data["institution_id"] = institution_id
        return await super().create(db, data)
    
    async def update(self, db: AsyncSession, id: UUID, data: Dict[str, Any], institution_id: UUID) -> Optional[Faculty]:
        """Update an existing faculty member."""
        return await super().update(
            db,
            id=id,
            data=data,
            institution_filter=institution_id
        )
    
    async def get(self, db: AsyncSession, id: UUID, institution_id: UUID) -> Optional[Faculty]:
        """Get a faculty member by ID."""
        return await super().get(db, id=id, institution_filter=institution_id)
    
    async def get_all(
        self, 
        db: AsyncSession, 
        institution_id: UUID,
        skip: int = 0,
        limit: int = 100,
        department_id: Optional[UUID] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Faculty], int]:
        """Get all faculty members with optional filtering by department."""
        
        query = select(Faculty).where(Faculty.institution_id == institution_id)
        
        # Filter by department if provided
        if department_id:
            query = query.where(Faculty.department_id == department_id)
        
        # Add search functionality
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Faculty.name.ilike(search_term),
                    Faculty.employee_id.ilike(search_term),
                    Faculty.email.ilike(search_term),
                    Faculty.designation.ilike(search_term)
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await db.scalar(count_query)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        results = await db.execute(query)
        items = results.scalars().all()
        
        return items, total_count
    
    async def delete(self, db: AsyncSession, id: UUID, institution_id: UUID) -> bool:
        """Delete a faculty member."""
        return await super().delete(db, id=id, institution_filter=institution_id)
    
    async def get_faculty_with_department(
        self,
        db: AsyncSession,
        faculty_id: UUID,
        institution_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get faculty with department details."""
        query = (
            select(Faculty, Department.name.label("department_name"))
            .join(Department, Faculty.department_id == Department.id)
            .where(
                and_(
                    Faculty.id == faculty_id,
                    Faculty.institution_id == institution_id
                )
            )
        )
        
        result = await db.execute(query)
        row = result.first()
        
        if not row:
            return None
            
        # Create a dictionary with faculty attributes and department name
        faculty_dict = {c.name: getattr(row[0], c.name) for c in row[0].__table__.columns}
        faculty_dict["department_name"] = row[1]
        
        return faculty_dict
