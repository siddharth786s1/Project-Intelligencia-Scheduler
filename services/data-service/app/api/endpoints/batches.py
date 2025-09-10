from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Query, Path
from typing import List, Optional

from app.api.dependencies import DB, CurrentUser, get_institution_id_from_token
from app.db.repositories.batch_repository import BatchRepository
from app.schemas.batch import BatchCreate, BatchUpdate, BatchResponse, BatchDetailResponse, BatchSubjectAssignment

router = APIRouter()
repository = BatchRepository()

@router.post("/", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(
    batch_in: BatchCreate,
    db: DB,
    current_user: CurrentUser,
) -> BatchResponse:
    """
    Create a new batch.
    """
    # Always use the institution ID from the token for security
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Create the batch with the institution ID from the token
    batch = await repository.create(db, obj_in=batch_in, institution_id=institution_id)
    return batch


@router.get("/", response_model=List[BatchResponse])
async def get_batches(
    db: DB,
    current_user: CurrentUser,
    department_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[BatchResponse]:
    """
    Get all batches for the current institution, with optional filtering by department.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Get batches filtered by institution ID and optionally department ID
    if department_id:
        batches = await repository.get_by_department(
            db, department_id=department_id, institution_id=institution_id,
            skip=skip, limit=limit
        )
    else:
        batches = await repository.get_multi(
            db, skip=skip, limit=limit, institution_id=institution_id
        )
    return batches


@router.get("/{batch_id}", response_model=BatchDetailResponse)
async def get_batch(
    batch_id: UUID,
    db: DB,
    current_user: CurrentUser,
) -> BatchDetailResponse:
    """
    Get a specific batch by ID.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Get batch filtered by institution ID (multi-tenant security)
    batch = await repository.get_by_id_with_details(db, id=batch_id, institution_id=institution_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found",
        )
    return batch


@router.patch("/{batch_id}", response_model=BatchResponse)
async def update_batch(
    batch_id: UUID,
    batch_update: BatchUpdate,
    db: DB,
    current_user: CurrentUser,
) -> BatchResponse:
    """
    Update a batch.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Get current batch (with tenant security)
    batch = await repository.get_by_id(db, id=batch_id, institution_id=institution_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found",
        )
    
    # Update batch
    updated_batch = await repository.update(db, obj_current=batch, obj_in=batch_update)
    return updated_batch


@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_batch(
    batch_id: UUID,
    db: DB,
    current_user: CurrentUser,
) -> None:
    """
    Delete a batch.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Delete the batch (with tenant security)
    deleted = await repository.delete(db, id=batch_id, institution_id=institution_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found",
        )


@router.post("/{batch_id}/subjects", status_code=status.HTTP_200_OK)
async def assign_subjects_to_batch(
    batch_id: UUID,
    assignment: BatchSubjectAssignment,
    db: DB,
    current_user: CurrentUser,
) -> dict:
    """
    Assign subjects to a batch.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Verify batch exists and belongs to the institution
    batch = await repository.get_by_id(db, id=batch_id, institution_id=institution_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found",
        )
    
    # Assign subjects to the batch
    result = await repository.assign_subjects(db, batch_id=batch_id, subject_ids=assignment.subject_ids)
    
    return {"success": result, "message": "Subjects assigned to batch successfully"}


@router.get("/{batch_id}/subjects", response_model=List[UUID])
async def get_batch_subjects(
    batch_id: UUID,
    db: DB,
    current_user: CurrentUser,
) -> List[UUID]:
    """
    Get subjects assigned to a batch.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Verify batch exists and belongs to the institution
    batch = await repository.get_by_id(db, id=batch_id, institution_id=institution_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found",
        )
    
    # Get subjects assigned to the batch
    subject_ids = await repository.get_batch_subjects(db, batch_id=batch_id)
    
    return subject_ids
