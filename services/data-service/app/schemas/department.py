from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# Base schema for department with common attributes
class DepartmentBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


# Schema for creating a new department
class DepartmentCreate(DepartmentBase):
    institution_id: Optional[UUID] = None  # Optional because it should be derived from token


# Schema for updating a department (all fields optional)
class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None


# Schema for department responses
class DepartmentResponse(DepartmentBase):
    id: UUID
    institution_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
