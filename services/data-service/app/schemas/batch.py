from uuid import UUID
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


# Base schema for batch with common attributes
class BatchBase(BaseModel):
    name: str
    code: str
    year: int
    size: int


# Schema for creating a new batch
class BatchCreate(BatchBase):
    department_id: UUID
    institution_id: Optional[UUID] = None  # Optional because it should be derived from token


# Schema for updating a batch (all fields optional)
class BatchUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    year: Optional[int] = None
    size: Optional[int] = None
    department_id: Optional[UUID] = None


# Schema for batch responses
class BatchResponse(BatchBase):
    id: UUID
    department_id: UUID
    institution_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Schema for batch detail responses (includes department details)
class BatchDetailResponse(BatchResponse):
    department_name: str
    
    model_config = ConfigDict(from_attributes=True)


# Schema for assigning subjects to a batch
class BatchSubjectAssignment(BaseModel):
    subject_ids: List[UUID]
