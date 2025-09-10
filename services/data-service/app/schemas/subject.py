from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# Base schema for subject with common attributes
class SubjectBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    credits: int
    lecture_hours_per_week: int
    lab_hours_per_week: int = 0


# Schema for creating a new subject
class SubjectCreate(SubjectBase):
    department_id: UUID
    institution_id: Optional[UUID] = None  # Optional because it should be derived from token


# Schema for updating a subject (all fields optional)
class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    credits: Optional[int] = None
    lecture_hours_per_week: Optional[int] = None
    lab_hours_per_week: Optional[int] = None
    department_id: Optional[UUID] = None


# Schema for subject responses
class SubjectResponse(SubjectBase):
    id: UUID
    department_id: UUID
    institution_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Schema for subject detail responses (includes department details)
class SubjectDetailResponse(SubjectResponse):
    department_name: str
    
    model_config = ConfigDict(from_attributes=True)
