from uuid import UUID
from typing import List, Optional, Dict, Any, Tuple

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.base import BaseRepository
from app.models.faculty_preferences import (
    FacultyAvailability,
    FacultySubjectExpertise,
    FacultyTeachingPreference
)
from app.models.subject import Subject
from app.models.batch import Batch
from app.models.classroom import Classroom


class FacultyAvailabilityRepository(BaseRepository):
    """Repository for managing faculty availability."""
    
    async def create(self, db: AsyncSession, data: Dict[str, Any], institution_id: UUID) -> FacultyAvailability:
        """Create a new faculty availability record."""
        data["institution_id"] = institution_id
        return await super().create(db, data)
    
    async def update(self, db: AsyncSession, id: UUID, data: Dict[str, Any], institution_id: UUID) -> Optional[FacultyAvailability]:
        """Update an existing faculty availability record."""
        return await super().update(
            db,
            id=id,
            data=data,
            institution_filter=institution_id
        )
    
    async def get(self, db: AsyncSession, id: UUID, institution_id: UUID) -> Optional[FacultyAvailability]:
        """Get a faculty availability record by ID."""
        return await super().get(db, id=id, institution_filter=institution_id)
    
    async def get_all_by_faculty(
        self, 
        db: AsyncSession, 
        faculty_id: UUID,
        institution_id: UUID
    ) -> List[FacultyAvailability]:
        """Get all availability records for a specific faculty member."""
        query = (
            select(FacultyAvailability)
            .where(
                and_(
                    FacultyAvailability.faculty_id == faculty_id,
                    FacultyAvailability.institution_id == institution_id
                )
            )
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def delete(self, db: AsyncSession, id: UUID, institution_id: UUID) -> bool:
        """Delete a faculty availability record."""
        return await super().delete(db, id=id, institution_filter=institution_id)


class FacultySubjectExpertiseRepository(BaseRepository):
    """Repository for managing faculty subject expertise."""
    
    async def create(self, db: AsyncSession, data: Dict[str, Any], institution_id: UUID) -> FacultySubjectExpertise:
        """Create a new faculty subject expertise record."""
        data["institution_id"] = institution_id
        return await super().create(db, data)
    
    async def update(self, db: AsyncSession, id: UUID, data: Dict[str, Any], institution_id: UUID) -> Optional[FacultySubjectExpertise]:
        """Update an existing faculty subject expertise record."""
        return await super().update(
            db,
            id=id,
            data=data,
            institution_filter=institution_id
        )
    
    async def get(self, db: AsyncSession, id: UUID, institution_id: UUID) -> Optional[FacultySubjectExpertise]:
        """Get a faculty subject expertise record by ID."""
        return await super().get(db, id=id, institution_filter=institution_id)
    
    async def get_all_by_faculty(
        self, 
        db: AsyncSession, 
        faculty_id: UUID,
        institution_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get all subject expertise records for a specific faculty member with subject names."""
        query = (
            select(FacultySubjectExpertise, Subject.name.label("subject_name"))
            .join(Subject, FacultySubjectExpertise.subject_id == Subject.id)
            .where(
                and_(
                    FacultySubjectExpertise.faculty_id == faculty_id,
                    FacultySubjectExpertise.institution_id == institution_id
                )
            )
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        expertise_list = []
        for row in rows:
            expertise = {c.name: getattr(row[0], c.name) for c in row[0].__table__.columns}
            expertise["subject_name"] = row[1]
            expertise_list.append(expertise)
            
        return expertise_list
    
    async def delete(self, db: AsyncSession, id: UUID, institution_id: UUID) -> bool:
        """Delete a faculty subject expertise record."""
        return await super().delete(db, id=id, institution_filter=institution_id)


class FacultyTeachingPreferenceRepository(BaseRepository):
    """Repository for managing faculty teaching preferences."""
    
    async def create(self, db: AsyncSession, data: Dict[str, Any], institution_id: UUID) -> FacultyTeachingPreference:
        """Create a new faculty teaching preference record."""
        data["institution_id"] = institution_id
        return await super().create(db, data)
    
    async def update(self, db: AsyncSession, id: UUID, data: Dict[str, Any], institution_id: UUID) -> Optional[FacultyTeachingPreference]:
        """Update an existing faculty teaching preference record."""
        return await super().update(
            db,
            id=id,
            data=data,
            institution_filter=institution_id
        )
    
    async def get(self, db: AsyncSession, id: UUID, institution_id: UUID) -> Optional[FacultyTeachingPreference]:
        """Get a faculty teaching preference record by ID."""
        return await super().get(db, id=id, institution_filter=institution_id)
    
    async def get_batch_preferences(
        self, 
        db: AsyncSession, 
        faculty_id: UUID,
        institution_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get all batch preference records for a specific faculty member."""
        query = (
            select(FacultyTeachingPreference, Batch.name.label("batch_name"))
            .join(Batch, FacultyTeachingPreference.batch_id == Batch.id)
            .where(
                and_(
                    FacultyTeachingPreference.faculty_id == faculty_id,
                    FacultyTeachingPreference.batch_id.isnot(None),
                    FacultyTeachingPreference.institution_id == institution_id
                )
            )
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        preference_list = []
        for row in rows:
            preference = {c.name: getattr(row[0], c.name) for c in row[0].__table__.columns}
            preference["batch_name"] = row[1]
            preference_list.append(preference)
            
        return preference_list
    
    async def get_classroom_preferences(
        self, 
        db: AsyncSession, 
        faculty_id: UUID,
        institution_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get all classroom preference records for a specific faculty member."""
        query = (
            select(FacultyTeachingPreference, Classroom.name.label("classroom_name"))
            .join(Classroom, FacultyTeachingPreference.classroom_id == Classroom.id)
            .where(
                and_(
                    FacultyTeachingPreference.faculty_id == faculty_id,
                    FacultyTeachingPreference.classroom_id.isnot(None),
                    FacultyTeachingPreference.institution_id == institution_id
                )
            )
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        preference_list = []
        for row in rows:
            preference = {c.name: getattr(row[0], c.name) for c in row[0].__table__.columns}
            preference["classroom_name"] = row[1]
            preference_list.append(preference)
            
        return preference_list
    
    async def delete(self, db: AsyncSession, id: UUID, institution_id: UUID) -> bool:
        """Delete a faculty teaching preference record."""
        return await super().delete(db, id=id, institution_filter=institution_id)
