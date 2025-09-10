from uuid import UUID
from typing import List, Optional, Dict, Any, Tuple

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.repositories.base import BaseRepository
from app.models.scheduled_session import ScheduledSession
from app.models.faculty import Faculty
from app.models.batch import Batch
from app.models.classroom import Classroom
from app.models.subject import Subject
from app.models.time_slot import TimeSlot


class ScheduledSessionRepository(BaseRepository):
    """Repository for managing scheduled sessions."""
    
    async def create(self, db: AsyncSession, data: Dict[str, Any], institution_id: UUID) -> ScheduledSession:
        """Create a new scheduled session."""
        data["institution_id"] = institution_id
        return await super().create(db, data)
    
    async def update(self, db: AsyncSession, id: UUID, data: Dict[str, Any], institution_id: UUID) -> Optional[ScheduledSession]:
        """Update an existing scheduled session."""
        return await super().update(
            db,
            id=id,
            data=data,
            institution_filter=institution_id
        )
    
    async def get(self, db: AsyncSession, id: UUID, institution_id: UUID) -> Optional[ScheduledSession]:
        """Get a scheduled session by ID."""
        return await super().get(db, id=id, institution_filter=institution_id)
    
    async def get_all(
        self, 
        db: AsyncSession, 
        institution_id: UUID,
        skip: int = 0,
        limit: int = 100,
        faculty_id: Optional[UUID] = None,
        subject_id: Optional[UUID] = None,
        batch_id: Optional[UUID] = None,
        classroom_id: Optional[UUID] = None,
        day_of_week: Optional[int] = None,
        is_canceled: Optional[bool] = None,
        generation_id: Optional[UUID] = None
    ) -> Tuple[List[ScheduledSession], int]:
        """Get all scheduled sessions with filtering options."""
        
        query = select(ScheduledSession).where(ScheduledSession.institution_id == institution_id)
        
        # Apply filters
        if faculty_id:
            query = query.where(ScheduledSession.faculty_id == faculty_id)
            
        if subject_id:
            query = query.where(ScheduledSession.subject_id == subject_id)
            
        if batch_id:
            query = query.where(ScheduledSession.batch_id == batch_id)
            
        if classroom_id:
            query = query.where(ScheduledSession.classroom_id == classroom_id)
            
        if day_of_week is not None:
            query = query.join(TimeSlot).where(TimeSlot.day_of_week == day_of_week)
            
        if is_canceled is not None:
            query = query.where(ScheduledSession.is_canceled == is_canceled)
            
        if generation_id:
            query = query.where(ScheduledSession.schedule_generation_id == generation_id)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await db.scalar(count_query)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        results = await db.execute(query)
        items = results.scalars().all()
        
        return items, total_count
    
    async def get_session_with_details(
        self,
        db: AsyncSession,
        session_id: UUID,
        institution_id: UUID
    ) -> Optional[ScheduledSession]:
        """Get a session with all related entity details."""
        query = (
            select(ScheduledSession)
            .options(
                joinedload(ScheduledSession.faculty),
                joinedload(ScheduledSession.subject),
                joinedload(ScheduledSession.batch),
                joinedload(ScheduledSession.classroom),
                joinedload(ScheduledSession.time_slot)
            )
            .where(
                and_(
                    ScheduledSession.id == session_id,
                    ScheduledSession.institution_id == institution_id
                )
            )
        )
        
        result = await db.execute(query)
        session = result.scalars().first()
        
        return session
    
async def get_faculty_timetable(
    self,
    db: AsyncSession,
    faculty_id: UUID,
    institution_id: UUID
) -> List[ScheduledSession]:
    """Get all scheduled sessions for a faculty member."""
    query = (
        select(ScheduledSession)
        .options(
            joinedload(ScheduledSession.faculty),
            joinedload(ScheduledSession.subject),
            joinedload(ScheduledSession.batch),
            joinedload(ScheduledSession.classroom),
            joinedload(ScheduledSession.time_slot)
        )
        .where(
            and_(
                ScheduledSession.faculty_id == faculty_id,
                ScheduledSession.institution_id == institution_id,
                ScheduledSession.is_canceled == False
            )
        )
        .order_by(ScheduledSession.time_slot_id)
    )
    
    result = await db.execute(query)
    return result.scalars().all()
    
async def get_batch_timetable(
        self,
        db: AsyncSession,
        batch_id: UUID,
        institution_id: UUID
    ) -> List[ScheduledSession]:
        """Get all scheduled sessions for a batch."""
        query = (
            select(ScheduledSession)
            .options(
                joinedload(ScheduledSession.faculty),
                joinedload(ScheduledSession.subject),
                joinedload(ScheduledSession.classroom),
                joinedload(ScheduledSession.time_slot)
            )
            .where(
                and_(
                    ScheduledSession.batch_id == batch_id,
                    ScheduledSession.institution_id == institution_id,
                    ScheduledSession.is_canceled == False
                )
            )
            .order_by(ScheduledSession.time_slot_id)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def delete(self, db: AsyncSession, id: UUID, institution_id: UUID) -> bool:
        """Delete a scheduled session."""
        return await super().delete(db, id=id, institution_filter=institution_id)
