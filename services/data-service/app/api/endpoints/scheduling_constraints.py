from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_institution_id, get_db
from app.db.repositories.scheduling_constraint_repository import SchedulingConstraintRepository
from app.schemas.scheduling_constraint import (
    SchedulingConstraintCreate,
    SchedulingConstraintUpdate,
    SchedulingConstraintResponse,
)
from app.schemas.response import ResponseModel

router = APIRouter(prefix="/scheduling-constraints", tags=["scheduling-constraints"])
repository = SchedulingConstraintRepository(entity_model="SchedulingConstraint")


@router.post("/", response_model=ResponseModel[SchedulingConstraintResponse])
async def create_scheduling_constraint(
    data: SchedulingConstraintCreate,
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """Create a new scheduling constraint."""
    constraint = await repository.create(db, data.dict(exclude_unset=True), institution_id)
    return ResponseModel(
        data=constraint,
        message="Scheduling constraint created successfully",
    )


@router.get("/", response_model=ResponseModel[dict])
async def get_scheduling_constraints(
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    constraint_type: Optional[str] = None,
    weight: Optional[int] = None,
    entity_type: Optional[str] = None,
    is_enabled: Optional[bool] = None,
):
    """Get all scheduling constraints with optional filters."""
    constraints, count = await repository.get_all(
        db, 
        institution_id, 
        skip, 
        limit,
        constraint_type=constraint_type,
        weight=weight,
        entity_type=entity_type,
        is_enabled=is_enabled
    )
    return ResponseModel(
        data={"items": constraints, "total": count},
        message="Scheduling constraints retrieved successfully",
    )


@router.get("/{constraint_id}", response_model=ResponseModel[SchedulingConstraintResponse])
async def get_scheduling_constraint(
    constraint_id: UUID = Path(..., title="The ID of the scheduling constraint"),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """Get a scheduling constraint by ID."""
    constraint = await repository.get(db, constraint_id, institution_id)
    if not constraint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduling constraint not found",
        )
    return ResponseModel(
        data=constraint,
        message="Scheduling constraint retrieved successfully",
    )


@router.put("/{constraint_id}", response_model=ResponseModel[SchedulingConstraintResponse])
async def update_scheduling_constraint(
    data: SchedulingConstraintUpdate,
    constraint_id: UUID = Path(..., title="The ID of the scheduling constraint"),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """Update a scheduling constraint."""
    constraint = await repository.update(db, constraint_id, data.dict(exclude_unset=True), institution_id)
    if not constraint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduling constraint not found",
        )
    return ResponseModel(
        data=constraint,
        message="Scheduling constraint updated successfully",
    )


@router.delete("/{constraint_id}", response_model=ResponseModel[bool])
async def delete_scheduling_constraint(
    constraint_id: UUID = Path(..., title="The ID of the scheduling constraint"),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """Delete a scheduling constraint."""
    deleted = await repository.delete(db, constraint_id, institution_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduling constraint not found",
        )
    return ResponseModel(
        data=True,
        message="Scheduling constraint deleted successfully",
    )
