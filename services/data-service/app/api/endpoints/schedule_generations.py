from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct

from app.api.dependencies import get_current_institution_id, get_db
from app.db.repositories.scheduled_session_repository import ScheduledSessionRepository
from app.models.scheduled_session import ScheduledSession
from app.schemas.scheduled_session import (
    ScheduledSessionResponse,
    ScheduleGenerationSummary
)
from app.schemas.response import ResponseModel

router = APIRouter(prefix="/scheduled-sessions/generations", tags=["schedule-generations"])
repository = ScheduledSessionRepository(entity_model="ScheduledSession")


@router.get("/", response_model=ResponseModel[List[dict]])
async def get_schedule_generations(
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """Get all schedule generations for an institution."""
    # Get distinct schedule generation IDs
    query = (
        select(
            ScheduledSession.schedule_generation_id,
            func.count().label("total_sessions"),
            func.min(ScheduledSession.created_at).label("created_at")
        )
        .where(
            ScheduledSession.institution_id == institution_id,
            ScheduledSession.schedule_generation_id.is_not(None)
        )
        .group_by(ScheduledSession.schedule_generation_id)
        .order_by(func.min(ScheduledSession.created_at).desc())
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    generations = result.all()
    
    # Get total count
    count_query = (
        select(func.count(distinct(ScheduledSession.schedule_generation_id)))
        .where(
            ScheduledSession.institution_id == institution_id,
            ScheduledSession.schedule_generation_id.is_not(None)
        )
    )
    total_count = await db.scalar(count_query)
    
    # Format the result
    generations_list = [
        {
            "generation_id": str(g.schedule_generation_id),
            "total_sessions": g.total_sessions,
            "created_at": g.created_at.isoformat()
        }
        for g in generations if g.schedule_generation_id
    ]
    
    return ResponseModel(
        data={"items": generations_list, "total": total_count or 0},
        message="Schedule generations retrieved successfully",
    )


@router.get("/{generation_id}", response_model=ResponseModel[ScheduleGenerationSummary])
async def get_schedule_generation(
    generation_id: UUID = Path(..., title="The ID of the schedule generation"),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """Get a schedule generation by ID with summary metrics."""
    # Check if generation exists
    exists_query = select(func.count()).where(
        ScheduledSession.institution_id == institution_id,
        ScheduledSession.schedule_generation_id == generation_id
    )
    count = await db.scalar(exists_query)
    
    if count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule generation not found",
        )
    
    # Get statistics
    stats_query = select(
        func.count().label("total_sessions"),
        func.count(distinct(ScheduledSession.faculty_id)).label("total_faculty"),
        func.count(distinct(ScheduledSession.batch_id)).label("total_batches"),
        func.count(distinct(ScheduledSession.classroom_id)).label("total_classrooms"),
        func.sum(ScheduledSession.soft_constraints_violated).label("soft_constraint_violations"),
        func.min(ScheduledSession.created_at).label("created_at")
    ).where(
        ScheduledSession.institution_id == institution_id,
        ScheduledSession.schedule_generation_id == generation_id
    )
    
    stats_result = await db.execute(stats_query)
    stats = stats_result.first()
    
    # Get a sample of sessions for preview
    sample_query = (
        select(ScheduledSession)
        .where(
            ScheduledSession.institution_id == institution_id,
            ScheduledSession.schedule_generation_id == generation_id
        )
        .limit(5)
    )
    
    sample_result = await db.execute(sample_query)
    sample_sessions = sample_result.scalars().all()
    
    # Create summary
    summary = ScheduleGenerationSummary(
        generation_id=generation_id,
        total_sessions=stats.total_sessions,
        total_faculty=stats.total_faculty,
        total_batches=stats.total_batches,
        total_classrooms=stats.total_classrooms,
        hard_constraint_violations=0,  # Assuming hard constraints are always satisfied
        soft_constraint_violations=stats.soft_constraint_violations or 0,
        faculty_satisfaction_score=85.5,  # Placeholder values
        batch_satisfaction_score=90.2,  # Placeholder values
        room_utilization=78.4,  # Placeholder values
        created_at=stats.created_at.isoformat(),
        sessions=[session for session in sample_sessions]
    )
    
    return ResponseModel(
        data=summary,
        message="Schedule generation retrieved successfully",
    )


@router.delete("/{generation_id}", response_model=ResponseModel[bool])
async def delete_schedule_generation(
    generation_id: UUID = Path(..., title="The ID of the schedule generation"),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """Delete all sessions for a schedule generation."""
    # Delete all sessions with this generation ID
    query = (
        select(ScheduledSession)
        .where(
            ScheduledSession.institution_id == institution_id,
            ScheduledSession.schedule_generation_id == generation_id
        )
    )
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    if not sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule generation not found",
        )
    
    # Delete each session
    for session in sessions:
        await db.delete(session)
    
    await db.commit()
    
    return ResponseModel(
        data=True,
        message="Schedule generation deleted successfully",
    )
