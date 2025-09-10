from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Query, Path
from typing import List, Optional

from app.api.dependencies import DB, CurrentUser, get_institution_id_from_token
from app.db.repositories.subject_repository import SubjectRepository
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse, SubjectDetailResponse

router = APIRouter()
repository = SubjectRepository()

@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject_in: SubjectCreate,
    db: DB,
    current_user: CurrentUser,
) -> SubjectResponse:
    """
    Create a new subject.
    """
    # Always use the institution ID from the token for security
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Create the subject with the institution ID from the token
    subject = await repository.create(db, obj_in=subject_in, institution_id=institution_id)
    return subject


@router.get("/", response_model=List[SubjectResponse])
async def get_subjects(
    db: DB,
    current_user: CurrentUser,
    department_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[SubjectResponse]:
    """
    Get all subjects for the current institution, with optional filtering by department.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Get subjects filtered by institution ID and optionally department ID
    if department_id:
        subjects = await repository.get_by_department(
            db, department_id=department_id, institution_id=institution_id,
            skip=skip, limit=limit
        )
    else:
        subjects = await repository.get_multi(
            db, skip=skip, limit=limit, institution_id=institution_id
        )
    return subjects


@router.get("/{subject_id}", response_model=SubjectDetailResponse)
async def get_subject(
    subject_id: UUID,
    db: DB,
    current_user: CurrentUser,
) -> SubjectDetailResponse:
    """
    Get a specific subject by ID.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Get subject filtered by institution ID (multi-tenant security)
    subject = await repository.get_by_id_with_details(db, id=subject_id, institution_id=institution_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found",
        )
    return subject


@router.patch("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: UUID,
    subject_update: SubjectUpdate,
    db: DB,
    current_user: CurrentUser,
) -> SubjectResponse:
    """
    Update a subject.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Get current subject (with tenant security)
    subject = await repository.get_by_id(db, id=subject_id, institution_id=institution_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found",
        )
    
    # Update subject
    updated_subject = await repository.update(db, obj_current=subject, obj_in=subject_update)
    return updated_subject


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
    subject_id: UUID,
    db: DB,
    current_user: CurrentUser,
) -> None:
    """
    Delete a subject.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Delete the subject (with tenant security)
    deleted = await repository.delete(db, id=subject_id, institution_id=institution_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found",
        )
