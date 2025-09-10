from uuid import UUID
from typing import List, Optional, Dict, Any, Tuple

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base import BaseRepository
from app.models.time_slot import TimeSlot


class TimeSlotRepository(BaseRepository):
    """Repository for managing time slots."""
    
    async def create(self, db: AsyncSession, data: Dict[str, Any], institution_id: UUID) -> TimeSlot:
        """Create a new time slot."""
        data["institution_id"] = institution_id
        return await super().create(db, data)
    
    async def update(self, db: AsyncSession, id: UUID, data: Dict[str, Any], institution_id: UUID) -> Optional[TimeSlot]:
        """Update an existing time slot."""
        return await super().update(
            db,
            id=id,
            data=data,
            institution_filter=institution_id
        )
    
    async def get(self, db: AsyncSession, id: UUID, institution_id: UUID) -> Optional[TimeSlot]:
        """Get a time slot by ID."""
        return await super().get(db, id=id, institution_filter=institution_id)
    
    async def get_all(
        self, 
        db: AsyncSession, 
        institution_id: UUID,
        skip: int = 0,
        limit: int = 100,
        day_of_week: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[TimeSlot], int]:
        """Get all time slots with optional filtering."""
        
        query = select(TimeSlot).where(TimeSlot.institution_id == institution_id)
        
        # Apply filters
        if day_of_week is not None:
            query = query.where(TimeSlot.day_of_week == day_of_week)
            
        if is_active is not None:
            query = query.where(TimeSlot.is_active == is_active)
        
        # Order by day of week and start time
        query = query.order_by(TimeSlot.day_of_week, TimeSlot.start_time)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await db.scalar(count_query)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        results = await db.execute(query)
        items = results.scalars().all()
        
        return items, total_count
    
    async def get_by_day(
        self,
        db: AsyncSession,
        day_of_week: int,
        institution_id: UUID
    ) -> List[TimeSlot]:
        """Get all time slots for a specific day."""
        query = (
            select(TimeSlot)
            .where(
                and_(
                    TimeSlot.day_of_week == day_of_week,
                    TimeSlot.institution_id == institution_id,
                    TimeSlot.is_active == True
                )
            )
            .order_by(TimeSlot.start_time)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def delete(self, db: AsyncSession, id: UUID, institution_id: UUID) -> bool:
        """Delete a time slot."""
        return await super().delete(db, id=id, institution_filter=institution_id)
