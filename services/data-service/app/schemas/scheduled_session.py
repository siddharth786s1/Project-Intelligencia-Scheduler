from uuid import UUID
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class ScheduledSessionBase(BaseModel):
    title: str
    description: Optional[str] = None
    faculty_id: UUID
    subject_id: UUID
    batch_id: UUID
    classroom_id: UUID
    time_slot_id: UUID
    session_type: str = "lecture"
    duration_minutes: int = Field(ge=30, le=180)
    is_canceled: bool = False
    cancellation_reason: Optional[str] = None
    schedule_generation_id: Optional[UUID] = None


class ScheduledSessionCreate(ScheduledSessionBase):
    pass


class ScheduledSessionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    faculty_id: Optional[UUID] = None
    subject_id: Optional[UUID] = None
    batch_id: Optional[UUID] = None
    classroom_id: Optional[UUID] = None
    time_slot_id: Optional[UUID] = None
    session_type: Optional[str] = None
    duration_minutes: Optional[int] = Field(default=None, ge=30, le=180)
    is_canceled: Optional[bool] = None
    cancellation_reason: Optional[str] = None
    schedule_generation_id: Optional[UUID] = None


class ScheduledSessionResponse(ScheduledSessionBase):
    id: UUID
    institution_id: UUID
    soft_constraints_violated: int = 0
    
    model_config = ConfigDict(from_attributes=True)


class ScheduledSessionDetailResponse(ScheduledSessionResponse):
    faculty_name: str
    subject_name: str
    subject_code: str
    batch_name: str
    classroom_name: str
    time_slot_name: str
    day_of_week: int
    start_time: str
    end_time: str
    
    model_config = ConfigDict(from_attributes=True)


class ScheduleGenerationSummary(BaseModel):
    generation_id: UUID
    total_sessions: int
    hard_constraint_violations: int
    soft_constraint_violations: int
    faculty_satisfaction_score: float  # 0-100%
    batch_satisfaction_score: float    # 0-100%
    room_utilization: float            # 0-100%
    sessions: List[ScheduledSessionDetailResponse]
