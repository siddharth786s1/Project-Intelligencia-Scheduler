from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# Base schema for classroom with common attributes
class ClassroomBase(BaseModel):
    name: str
    capacity: int


# Schema for creating a new classroom
class ClassroomCreate(ClassroomBase):
    room_type_id: UUID
    institution_id: Optional[UUID] = None  # Optional because it should be derived from token


# Schema for updating a classroom
class ClassroomUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    room_type_id: Optional[UUID] = None


# Schema for classroom responses
class ClassroomResponse(ClassroomBase):
    id: UUID
    room_type_id: UUID
    institution_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Schema for classroom responses with room type details
class ClassroomDetailResponse(ClassroomResponse):
    room_type: str
    
    model_config = ConfigDict(from_attributes=True)
