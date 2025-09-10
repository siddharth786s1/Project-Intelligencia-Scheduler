from uuid import UUID
from typing import List, Optional, Dict, Any, Tuple

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.repositories.base import BaseRepository
from app.models.scheduling_constraint import SchedulingConstraint, ConstraintScope
from app.models.faculty import Faculty
from app.models.batch import Batch
from app.models.classroom import Classroom
from app.models.subject import Subject


class SchedulingConstraintRepository(BaseRepository):
    """Repository for managing scheduling constraints."""
    
    async def create(self, db: AsyncSession, data: Dict[str, Any], institution_id: UUID) -> SchedulingConstraint:
        """Create a new scheduling constraint."""
        data["institution_id"] = institution_id
        return await super().create(db, data)
    
    async def update(self, db: AsyncSession, id: UUID, data: Dict[str, Any], institution_id: UUID) -> Optional[SchedulingConstraint]:
        """Update an existing scheduling constraint."""
        return await super().update(
            db,
            id=id,
            data=data,
            institution_filter=institution_id
        )
    
    async def get(self, db: AsyncSession, id: UUID, institution_id: UUID) -> Optional[SchedulingConstraint]:
        """Get a scheduling constraint by ID."""
        return await super().get(db, id=id, institution_filter=institution_id)
    
    async def get_all(
        self, 
        db: AsyncSession, 
        institution_id: UUID,
        skip: int = 0,
        limit: int = 100,
        constraint_type: Optional[str] = None,
        scope: Optional[str] = None,
        faculty_id: Optional[UUID] = None,
        batch_id: Optional[UUID] = None,
        classroom_id: Optional[UUID] = None,
        subject_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[SchedulingConstraint], int]:
        """Get all scheduling constraints with filtering options."""
        
        query = select(SchedulingConstraint).where(SchedulingConstraint.institution_id == institution_id)
        
        # Apply filters
        if constraint_type:
            query = query.where(SchedulingConstraint.constraint_type == constraint_type)
            
        if scope:
            query = query.where(SchedulingConstraint.scope == scope)
            
        if faculty_id:
            query = query.where(SchedulingConstraint.faculty_id == faculty_id)
            
        if batch_id:
            query = query.where(SchedulingConstraint.batch_id == batch_id)
            
        if classroom_id:
            query = query.where(SchedulingConstraint.classroom_id == classroom_id)
            
        if subject_id:
            query = query.where(SchedulingConstraint.subject_id == subject_id)
            
        if is_active is not None:
            query = query.where(SchedulingConstraint.is_active == is_active)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await db.scalar(count_query)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        results = await db.execute(query)
        items = results.scalars().all()
        
        return items, total_count
    
    async def get_constraint_with_details(
        self,
        db: AsyncSession,
        constraint_id: UUID,
        institution_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get a constraint with related entity details."""
        query = (
            select(SchedulingConstraint)
            .options(
                joinedload(SchedulingConstraint.faculty),
                joinedload(SchedulingConstraint.batch),
                joinedload(SchedulingConstraint.classroom),
                joinedload(SchedulingConstraint.subject)
            )
            .where(
                and_(
                    SchedulingConstraint.id == constraint_id,
                    SchedulingConstraint.institution_id == institution_id
                )
            )
        )
        
        result = await db.execute(query)
        constraint = result.scalars().first()
        
        if not constraint:
            return None
            
        # Create a dictionary with constraint attributes and related entity names
        constraint_dict = {c.name: getattr(constraint, c.name) for c in constraint.__table__.columns}
        
        # Add related entity names based on scope
        if constraint.scope == ConstraintScope.FACULTY and constraint.faculty:
            constraint_dict["faculty_name"] = constraint.faculty.name
            
        elif constraint.scope == ConstraintScope.BATCH and constraint.batch:
            constraint_dict["batch_name"] = constraint.batch.name
            
        elif constraint.scope == ConstraintScope.CLASSROOM and constraint.classroom:
            constraint_dict["classroom_name"] = constraint.classroom.name
            
        elif constraint.scope == ConstraintScope.SUBJECT and constraint.subject:
            constraint_dict["subject_name"] = constraint.subject.name
        
        return constraint_dict
    
    async def delete(self, db: AsyncSession, id: UUID, institution_id: UUID) -> bool:
        """Delete a scheduling constraint."""
        return await super().delete(db, id=id, institution_filter=institution_id)
