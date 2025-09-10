from uuid import UUID
from typing import Optional, Dict, Any, Union

from pydantic import BaseModel, ConfigDict, Field, validator
from enum import Enum


class ConstraintType(str, Enum):
    HARD = "hard"
    SOFT = "soft"


class ConstraintScope(str, Enum):
    FACULTY = "faculty"
    BATCH = "batch"
    CLASSROOM = "classroom"
    SUBJECT = "subject"
    GLOBAL = "global"


class SchedulingConstraintBase(BaseModel):
    name: str
    description: Optional[str] = None
    constraint_type: ConstraintType = ConstraintType.SOFT
    scope: ConstraintScope
    faculty_id: Optional[UUID] = None
    batch_id: Optional[UUID] = None
    classroom_id: Optional[UUID] = None
    subject_id: Optional[UUID] = None
    configuration: Dict[str, Any]
    weight: int = Field(default=1, ge=1, le=10)
    is_active: bool = True
    
    @validator('faculty_id', 'batch_id', 'classroom_id', 'subject_id')
    def validate_scope_consistency(cls, v, values):
        scope = values.get('scope')
        field_name = next((k for k, val in values.items() if val == v), None)
        
        if scope == ConstraintScope.FACULTY and field_name == 'faculty_id':
            return v
        elif scope == ConstraintScope.BATCH and field_name == 'batch_id':
            return v
        elif scope == ConstraintScope.CLASSROOM and field_name == 'classroom_id':
            return v
        elif scope == ConstraintScope.SUBJECT and field_name == 'subject_id':
            return v
        elif scope == ConstraintScope.GLOBAL:
            if field_name in ('faculty_id', 'batch_id', 'classroom_id', 'subject_id') and v is not None:
                raise ValueError(f"Global scope constraint cannot have {field_name}")
            return v
        
        if field_name in ('faculty_id', 'batch_id', 'classroom_id', 'subject_id') and v is not None:
            if scope != field_name.replace('_id', '').upper():
                raise ValueError(f"{field_name} should be None for scope {scope}")
        
        return v


class SchedulingConstraintCreate(SchedulingConstraintBase):
    pass


class SchedulingConstraintUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    constraint_type: Optional[ConstraintType] = None
    scope: Optional[ConstraintScope] = None
    faculty_id: Optional[UUID] = None
    batch_id: Optional[UUID] = None
    classroom_id: Optional[UUID] = None
    subject_id: Optional[UUID] = None
    configuration: Optional[Dict[str, Any]] = None
    weight: Optional[int] = Field(default=None, ge=1, le=10)
    is_active: Optional[bool] = None


class SchedulingConstraintResponse(SchedulingConstraintBase):
    id: UUID
    institution_id: UUID
    
    model_config = ConfigDict(from_attributes=True)


class SchedulingConstraintDetailResponse(SchedulingConstraintResponse):
    faculty_name: Optional[str] = None
    batch_name: Optional[str] = None
    classroom_name: Optional[str] = None
    subject_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
