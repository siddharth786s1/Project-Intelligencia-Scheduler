from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.base import BaseRepository
from app.models.institution import Institution
from app.schemas.institution import InstitutionCreate, InstitutionUpdate


class InstitutionRepository(BaseRepository[Institution, InstitutionCreate, InstitutionUpdate]):
    def __init__(self):
        super().__init__(Institution)
