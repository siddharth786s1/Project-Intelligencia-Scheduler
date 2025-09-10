from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(
        self, db: AsyncSession, id: UUID, institution_id: Optional[UUID] = None
    ) -> Optional[ModelType]:
        """
        Get a record by ID, optionally filtering by institution_id for multi-tenancy.
        """
        query = select(self.model).where(self.model.id == id)
        
        # Apply institution filtering for multi-tenancy if applicable
        if institution_id is not None and hasattr(self.model, "institution_id"):
            query = query.where(self.model.institution_id == institution_id)
            
        result = await db.execute(query)
        return result.scalars().first()
        
    async def get_by_id_with_details(
        self, db: AsyncSession, id: UUID, institution_id: Optional[UUID] = None
    ) -> Optional[ModelType]:
        """
        Get a record by ID with related details, optionally filtering by institution_id for multi-tenancy.
        Intended to be overridden by subclasses that need to include related data.
        """
        return await self.get_by_id(db, id, institution_id)

    async def get_multi(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        institution_id: Optional[UUID] = None
    ) -> List[ModelType]:
        """
        Get multiple records, optionally filtered by institution_id for multi-tenancy.
        """
        query = select(self.model).offset(skip).limit(limit)
        
        # Apply institution filtering for multi-tenancy if applicable
        if institution_id is not None and hasattr(self.model, "institution_id"):
            query = query.where(self.model.institution_id == institution_id)
            
        result = await db.execute(query)
        return result.scalars().all()
        
    async def get_multi_with_filters(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get multiple records with custom filters.
        """
        query = select(self.model).offset(skip).limit(limit)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
            
        result = await db.execute(query)
        return result.scalars().all()

    async def create(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: Union[CreateSchemaType, Dict[str, Any]],
        institution_id: Optional[UUID] = None
    ) -> ModelType:
        """
        Create a new record, optionally setting institution_id for multi-tenancy.
        """
        obj_in_data = jsonable_encoder(obj_in)
        
        # Set institution_id for multi-tenancy if applicable
        if institution_id is not None and hasattr(self.model, "institution_id"):
            obj_in_data["institution_id"] = str(institution_id)
            
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        obj_current: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing record.
        """
        obj_data = jsonable_encoder(obj_current)
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        for field in obj_data:
            if field in update_data:
                setattr(obj_current, field, update_data[field])
                
        db.add(obj_current)
        await db.commit()
        await db.refresh(obj_current)
        return obj_current

    async def delete(self, db: AsyncSession, *, id: UUID, institution_id: Optional[UUID] = None) -> bool:
        """
        Delete a record by ID, optionally filtering by institution_id for multi-tenancy.
        """
        query = select(self.model).where(self.model.id == id)
        
        # Apply institution filtering for multi-tenancy if applicable
        if institution_id is not None and hasattr(self.model, "institution_id"):
            query = query.where(self.model.institution_id == institution_id)
            
        result = await db.execute(query)
        obj = result.scalars().first()
        
        if not obj:
            return False
            
        await db.delete(obj)
        await db.commit()
        return True
