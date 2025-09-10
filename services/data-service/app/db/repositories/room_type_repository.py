from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.base import BaseRepository
from app.models.room_type import RoomType
from app.schemas.room_type import RoomTypeCreate, RoomTypeUpdate


class RoomTypeRepository(BaseRepository[RoomType, RoomTypeCreate, RoomTypeUpdate]):
    def __init__(self):
        super().__init__(RoomType)
