from uuid import UUID
from typing import Optional, Dict, Any, List
from sqlalchemy import select, join
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.db.repositories.base import BaseRepository
from app.models.classroom import Classroom
from app.models.room_type import RoomType
from app.schemas.classroom import ClassroomCreate, ClassroomUpdate, ClassroomDetailResponse


class ClassroomRepository(BaseRepository[Classroom, ClassroomCreate, ClassroomUpdate]):
    def __init__(self):
        super().__init__(Classroom)
        
    async def get_by_id_with_details(
        self, db: AsyncSession, id: UUID, institution_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a classroom by ID with room type details.
        """
        query = (
            select(Classroom, RoomType.name.label("room_type"))
            .join(RoomType, Classroom.room_type_id == RoomType.id)
            .where(Classroom.id == id)
        )
        
        # Apply institution filtering for multi-tenancy if applicable
        if institution_id is not None:
            query = query.where(Classroom.institution_id == institution_id)
            
        result = await db.execute(query)
        row = result.first()
        
        if not row:
            return None
            
        classroom, room_type_name = row
        
        # Create a combined object with classroom and room type name
        classroom_dict = {c.name: getattr(classroom, c.name) for c in classroom.__table__.columns}
        classroom_dict["room_type"] = room_type_name
        
        return classroom_dict
