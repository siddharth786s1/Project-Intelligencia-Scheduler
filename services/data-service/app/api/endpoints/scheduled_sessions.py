from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_institution_id, get_db
from app.db.repositories.scheduled_session_repository import ScheduledSessionRepository
from app.schemas.scheduled_session import (
    ScheduledSessionCreate,
    ScheduledSessionUpdate,
    ScheduledSessionResponse,
    ScheduledSessionDetailResponse,
)
from app.schemas.response import ResponseModel

router = APIRouter(prefix="/scheduled-sessions", tags=["scheduled-sessions"])
repository = ScheduledSessionRepository(entity_model="ScheduledSession")


@router.post("/", response_model=ResponseModel[ScheduledSessionResponse])
async def create_scheduled_session(
    data: ScheduledSessionCreate,
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """Create a new scheduled session."""
    session = await repository.create(db, data.dict(exclude_unset=True), institution_id)
    return ResponseModel(
        data=session,
        message="Scheduled session created successfully",
    )


@router.get("/", response_model=ResponseModel[dict])
async def get_scheduled_sessions(
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    faculty_id: Optional[UUID] = None,
    subject_id: Optional[UUID] = None,
    batch_id: Optional[UUID] = None,
    classroom_id: Optional[UUID] = None,
    day_of_week: Optional[int] = Query(None, ge=0, le=6),
    is_canceled: Optional[bool] = None,
    generation_id: Optional[UUID] = None,
):
    """Get all scheduled sessions with optional filters."""
    sessions, count = await repository.get_all(
        db, 
        institution_id, 
        skip, 
        limit,
        faculty_id=faculty_id,
        subject_id=subject_id,
        batch_id=batch_id,
        classroom_id=classroom_id,
        day_of_week=day_of_week,
        is_canceled=is_canceled,
        generation_id=generation_id
    )
    return ResponseModel(
        data={"items": sessions, "total": count},
        message="Scheduled sessions retrieved successfully",
    )


@router.get("/{session_id}", response_model=ResponseModel[ScheduledSessionDetailResponse])
async def get_scheduled_session(
    session_id: UUID = Path(..., title="The ID of the scheduled session"),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """Get a scheduled session by ID with detailed information."""
    session = await repository.get_session_with_details(db, session_id, institution_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled session not found",
        )
    return ResponseModel(
        data=session,
        message="Scheduled session retrieved successfully",
    )


@router.put("/{session_id}", response_model=ResponseModel[ScheduledSessionResponse])
async def update_scheduled_session(
    data: ScheduledSessionUpdate,
    session_id: UUID = Path(..., title="The ID of the scheduled session"),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """Update a scheduled session."""
    session = await repository.update(db, session_id, data.dict(exclude_unset=True), institution_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled session not found",
        )
    return ResponseModel(
        data=session,
        message="Scheduled session updated successfully",
    )


@router.delete("/{session_id}", response_model=ResponseModel[bool])
async def delete_scheduled_session(
    session_id: UUID = Path(..., title="The ID of the scheduled session"),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """Delete a scheduled session."""
    deleted = await repository.delete(db, session_id, institution_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled session not found",
        )
    return ResponseModel(
        data=True,
        message="Scheduled session deleted successfully",
    )


@router.get("/faculty/{faculty_id}/timetable", response_model=ResponseModel[List[ScheduledSessionDetailResponse]])
async def get_faculty_timetable(
    faculty_id: UUID = Path(..., title="The ID of the faculty member"),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """Get the timetable for a faculty member."""
    sessions = await repository.get_faculty_timetable(db, faculty_id, institution_id)
    return ResponseModel(
        data=sessions,
        message="Faculty timetable retrieved successfully",
    )


@router.get("/batch/{batch_id}/timetable", response_model=ResponseModel[List[ScheduledSessionDetailResponse]])
async def get_batch_timetable(
    batch_id: UUID = Path(..., title="The ID of the batch"),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """Get the timetable for a batch."""
    sessions = await repository.get_batch_timetable(db, batch_id, institution_id)
    return ResponseModel(
        data=sessions,
        message="Batch timetable retrieved successfully",
    )
