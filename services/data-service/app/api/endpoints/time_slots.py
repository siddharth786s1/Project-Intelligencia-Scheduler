from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_institution_id, get_db
from app.db.repositories.time_slot_repository import TimeSlotRepository
from app.schemas.time_slot import (
    TimeSlotCreate,
    TimeSlotUpdate,
    TimeSlotResponse,
)
from app.schemas.response import ResponseModel

router = APIRouter(prefix="/time-slots", tags=["time-slots"])
repository = TimeSlotRepository(entity_model="TimeSlot")


@router.post("/", response_model=ResponseModel[TimeSlotResponse])
async def create_time_slot(
    data: TimeSlotCreate,
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """Create a new time slot."""
    time_slot = await repository.create(db, data.dict(exclude_unset=True), institution_id)
    return ResponseModel(
        data=time_slot,
        message="Time slot created successfully",
    )


@router.get("/", response_model=ResponseModel[dict])
async def get_time_slots(
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    day_of_week: Optional[int] = Query(None, ge=0, le=6),
):
    """Get all time slots with optional filters."""
    time_slots, count = await repository.get_all(
        db, 
        institution_id, 
        skip, 
        limit,
        day_of_week=day_of_week
    )
    return ResponseModel(
        data={"items": time_slots, "total": count},
        message="Time slots retrieved successfully",
    )


@router.get("/{time_slot_id}", response_model=ResponseModel[TimeSlotResponse])
async def get_time_slot(
    time_slot_id: UUID = Path(..., title="The ID of the time slot"),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """Get a time slot by ID."""
    time_slot = await repository.get(db, time_slot_id, institution_id)
    if not time_slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time slot not found",
        )
    return ResponseModel(
        data=time_slot,
        message="Time slot retrieved successfully",
    )


@router.put("/{time_slot_id}", response_model=ResponseModel[TimeSlotResponse])
async def update_time_slot(
    data: TimeSlotUpdate,
    time_slot_id: UUID = Path(..., title="The ID of the time slot"),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """Update a time slot."""
    time_slot = await repository.update(db, time_slot_id, data.dict(exclude_unset=True), institution_id)
    if not time_slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time slot not found",
        )
    return ResponseModel(
        data=time_slot,
        message="Time slot updated successfully",
    )


@router.delete("/{time_slot_id}", response_model=ResponseModel[bool])
async def delete_time_slot(
    time_slot_id: UUID = Path(..., title="The ID of the time slot"),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """Delete a time slot."""
    deleted = await repository.delete(db, time_slot_id, institution_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time slot not found",
        )
    return ResponseModel(
        data=True,
        message="Time slot deleted successfully",
    )
