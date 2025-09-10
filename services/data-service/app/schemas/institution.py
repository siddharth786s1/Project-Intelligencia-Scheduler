from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, Field


# Base schema for institution with common attributes
class InstitutionBase(BaseModel):
    name: str
    code: str
    contact_email: EmailStr
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


# Schema for creating a new institution
class InstitutionCreate(InstitutionBase):
    pass


# Schema for updating an institution (all fields optional)
class InstitutionUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


# Schema for institution responses
class InstitutionResponse(InstitutionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
