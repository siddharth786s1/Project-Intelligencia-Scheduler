from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# Base schema for room type with common attributes
class RoomTypeBase(BaseModel):
    name: str


# Schema for creating a new room type
class RoomTypeCreate(RoomTypeBase):
    institution_id: Optional[UUID] = None  # Optional because it should be derived from token


# Schema for updating a room type
class RoomTypeUpdate(BaseModel):
    name: Optional[str] = None


# Schema for room type responses
class RoomTypeResponse(RoomTypeBase):
    id: UUID
    institution_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
