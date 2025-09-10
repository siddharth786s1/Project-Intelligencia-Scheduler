from uuid import UUID
from typing import Dict, Any, List, Optional
from sqlalchemy import select, join
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.db.repositories.base import BaseRepository
from app.models.subject import Subject
from app.models.department import Department
from app.schemas.subject import SubjectCreate, SubjectUpdate


class SubjectRepository(BaseRepository[Subject, SubjectCreate, SubjectUpdate]):
    def __init__(self):
        super().__init__(Subject)
        
    async def get_by_id_with_details(
        self, db: AsyncSession, id: UUID, institution_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a subject by ID with department details.
        """
        query = (
            select(Subject, Department.name.label("department_name"))
            .join(Department, Subject.department_id == Department.id)
            .where(Subject.id == id)
        )
        
        # Apply institution filtering for multi-tenancy if applicable
        if institution_id is not None:
            query = query.where(Subject.institution_id == institution_id)
            
        result = await db.execute(query)
        row = result.first()
        
        if not row:
            return None
            
        subject, department_name = row
        
        # Create a combined object with subject and department name
        subject_dict = {c.name: getattr(subject, c.name) for c in subject.__table__.columns}
        subject_dict["department_name"] = department_name
        
        return subject_dict
        
    async def get_by_department(
        self, 
        db: AsyncSession, 
        department_id: UUID,
        institution_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Subject]:
        """
        Get subjects for a specific department.
        """
        query = (
            select(Subject)
            .where(Subject.department_id == department_id)
            .offset(skip)
            .limit(limit)
        )
        
        # Apply institution filtering for multi-tenancy if applicable
        if institution_id is not None:
            query = query.where(Subject.institution_id == institution_id)
            
        result = await db.execute(query)
        return result.scalars().all()
