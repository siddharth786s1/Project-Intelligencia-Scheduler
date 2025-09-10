from uuid import UUID
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, ConfigDict, Field


# Base schema for faculty with common attributes
class FacultyBase(BaseModel):
    name: str
    employee_id: str
    email: EmailStr
    phone: Optional[str] = None
    designation: str
    weekly_load_hours: int = Field(default=40, ge=1, le=60)
    is_active: bool = True


# Schema for creating a new faculty member
class FacultyCreate(FacultyBase):
    department_id: UUID
    user_id: Optional[UUID] = None
    institution_id: Optional[UUID] = None  # Optional because it should be derived from token
    joining_date: Optional[datetime] = None


# Schema for updating a faculty member (all fields optional)
class FacultyUpdate(BaseModel):
    name: Optional[str] = None
    employee_id: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    department_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    weekly_load_hours: Optional[int] = Field(default=None, ge=1, le=60)
    is_active: Optional[bool] = None
    joining_date: Optional[datetime] = None


# Schema for faculty responses
class FacultyResponse(FacultyBase):
    id: UUID
    department_id: UUID
    institution_id: UUID
    user_id: Optional[UUID] = None
    joining_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Schema for faculty detail responses (includes department details)
class FacultyDetailResponse(FacultyResponse):
    department_name: str
    
    model_config = ConfigDict(from_attributes=True)
