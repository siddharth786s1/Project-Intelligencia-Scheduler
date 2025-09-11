from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class SchedulingStatus(str, Enum):
    """Status of a scheduling job"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"
    CANCELLED = "cancelled"


class AlgorithmType(str, Enum):
    """Type of scheduling algorithm to use"""
    CSP = "csp"
    GENETIC = "genetic"


class SchedulingRequest(BaseModel):
    """Request to create a new timetable"""
    name: str = Field(..., description="Name of the schedule generation")
    description: Optional[str] = None
    
    # Entities to be scheduled
    faculty_ids: Optional[List[UUID]] = None
    batch_ids: Optional[List[UUID]] = None
    subject_ids: Optional[List[UUID]] = None
    classroom_ids: Optional[List[UUID]] = None
    
    # Scheduling parameters
    academic_term: str = Field(..., description="Academic term (e.g., 'Fall 2025')")
    start_date: str = Field(..., description="Start date of the term (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date of the term (YYYY-MM-DD)")
    
    # Algorithm parameters
    algorithm_type: AlgorithmType = Field(default=AlgorithmType.CSP, description="Type of algorithm to use")
    optimization_goals: List[str] = Field(
        default=["minimize_conflicts", "maximize_faculty_preferences"],
        description="Goals to optimize for"
    )
    max_iterations: int = Field(default=100, description="Maximum iterations for optimization")
    use_existing_schedule: bool = Field(default=False, description="Start from existing schedule")
    existing_schedule_id: Optional[UUID] = None


class SchedulingJobStatus(BaseModel):
    """Status of a scheduling job"""
    job_id: UUID
    status: SchedulingStatus
    progress: float = Field(default=0.0, description="Progress percentage (0-100)")
    message: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    
    # Results summary (available when completed)
    schedule_generation_id: Optional[UUID] = None
    total_sessions: Optional[int] = None
    hard_constraint_violations: Optional[int] = None
    soft_constraint_violations: Optional[int] = None
    faculty_satisfaction_score: Optional[float] = None
    batch_satisfaction_score: Optional[float] = None
    room_utilization: Optional[float] = None


class ScheduleGenerationSummary(BaseModel):
    """Summary of a generated schedule"""
    generation_id: UUID
    name: str
    description: Optional[str] = None
    academic_term: str
    start_date: str
    end_date: str
    created_at: str
    
    # Stats
    total_sessions: int
    total_faculty: int
    total_batches: int
    total_classrooms: int
    
    # Quality metrics
    hard_constraint_violations: int
    soft_constraint_violations: int
    faculty_satisfaction_score: float  # 0-100%
    batch_satisfaction_score: float    # 0-100%
    room_utilization: float            # 0-100%
    
    # Sample sessions (5 random ones for preview)
    sample_sessions: Optional[List[Dict[str, Any]]] = None


class ResponseModel(BaseModel):
    """Standard response model with data and message"""
    data: Any
    message: str
