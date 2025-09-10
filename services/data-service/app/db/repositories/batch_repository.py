from uuid import UUID
from typing import Dict, Any, List, Optional
from sqlalchemy import select, join, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.db.repositories.base import BaseRepository
from app.models.batch import Batch
from app.models.department import Department
from app.models.associations import batch_subject
from app.schemas.batch import BatchCreate, BatchUpdate


class BatchRepository(BaseRepository[Batch, BatchCreate, BatchUpdate]):
    def __init__(self):
        super().__init__(Batch)
        
    async def get_by_id_with_details(
        self, db: AsyncSession, id: UUID, institution_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a batch by ID with department details.
        """
        query = (
            select(Batch, Department.name.label("department_name"))
            .join(Department, Batch.department_id == Department.id)
            .where(Batch.id == id)
        )
        
        # Apply institution filtering for multi-tenancy if applicable
        if institution_id is not None:
            query = query.where(Batch.institution_id == institution_id)
            
        result = await db.execute(query)
        row = result.first()
        
        if not row:
            return None
            
        batch, department_name = row
        
        # Create a combined object with batch and department name
        batch_dict = {c.name: getattr(batch, c.name) for c in batch.__table__.columns}
        batch_dict["department_name"] = department_name
        
        return batch_dict
        
    async def get_by_department(
        self, 
        db: AsyncSession, 
        department_id: UUID,
        institution_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Batch]:
        """
        Get batches for a specific department.
        """
        query = (
            select(Batch)
            .where(Batch.department_id == department_id)
            .offset(skip)
            .limit(limit)
        )
        
        # Apply institution filtering for multi-tenancy if applicable
        if institution_id is not None:
            query = query.where(Batch.institution_id == institution_id)
            
        result = await db.execute(query)
        return result.scalars().all()
        
    async def assign_subjects(
        self,
        db: AsyncSession,
        batch_id: UUID,
        subject_ids: List[UUID]
    ) -> bool:
        """
        Assign subjects to a batch.
        """
        # Delete existing assignments
        delete_query = delete(batch_subject).where(batch_subject.c.batch_id == batch_id)
        await db.execute(delete_query)
        
        # Create new assignments
        for subject_id in subject_ids:
            insert_query = insert(batch_subject).values(
                batch_id=batch_id,
                subject_id=subject_id
            )
            await db.execute(insert_query)
            
        await db.commit()
        return True
        
    async def get_batch_subjects(
        self,
        db: AsyncSession,
        batch_id: UUID
    ) -> List[UUID]:
        """
        Get subjects assigned to a batch.
        """
        query = select(batch_subject.c.subject_id).where(batch_subject.c.batch_id == batch_id)
        result = await db.execute(query)
        return [row[0] for row in result.all()]
