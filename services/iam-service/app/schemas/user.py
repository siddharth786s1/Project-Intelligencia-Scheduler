from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import uuid

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role_id: uuid.UUID
    institution_id: Optional[uuid.UUID] = None

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserDB(UserBase):
    id: uuid.UUID
    role_id: uuid.UUID
    institution_id: Optional[uuid.UUID] = None
    is_active: bool = True
    
    class Config:
        orm_mode = True

class UserResponse(UserBase):
    id: uuid.UUID
    role_id: uuid.UUID
    role: Optional[dict] = None
    institution_id: Optional[uuid.UUID] = None
    is_active: bool
    created_at: Optional[str] = None
    
    class Config:
        orm_mode = True
