from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func
from sqlalchemy.sql import Select
from uuid import UUID

from app.db.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        self.db = db
        self.model = model
    
    async def get(self, id: UUID) -> Optional[ModelType]:
        """Get an entity by ID."""
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        where_clause = None
    ) -> List[ModelType]:
        """Get all entities with optional filtering."""
        query = select(self.model)
        if where_clause is not None:
            if isinstance(where_clause, list):
                for clause in where_clause:
                    query = query.where(clause)
            else:
                query = query.where(where_clause)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def count(self, where_clause = None) -> int:
        """Count entities with optional filtering."""
        query = select(func.count()).select_from(self.model)
        if where_clause is not None:
            if isinstance(where_clause, list):
                for clause in where_clause:
                    query = query.where(clause)
            else:
                query = query.where(where_clause)
        result = await self.db.execute(query)
        return result.scalar()
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new entity."""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, 
        id: UUID, 
        obj_in: Dict[str, Any]
    ) -> Optional[ModelType]:
        """Update an existing entity."""
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**obj_in)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(stmt)
        await self.db.commit()
        return await self.get(id)
    
    async def delete(self, id: UUID) -> None:
        """Delete an entity."""
        stmt = (
            delete(self.model)
            .where(self.model.id == id)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(stmt)
        await self.db.commit()
    
    async def paginate(
        self,
        query: Select,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Paginate a query."""
        # Create a count query
        count_query = select(func.count()).select_from(query.subquery())
        
        # Execute count query
        total = await self.db.execute(count_query)
        total = total.scalar()
        
        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute paginated query
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
