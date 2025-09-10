from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Query
from typing import List

from app.api.dependencies import DB, CurrentUser, get_institution_id_from_token
from app.db.repositories.classroom_repository import ClassroomRepository
from app.schemas.classroom import ClassroomCreate, ClassroomUpdate, ClassroomResponse, ClassroomDetailResponse

router = APIRouter()
repository = ClassroomRepository()

@router.post("/", response_model=ClassroomResponse, status_code=status.HTTP_201_CREATED)
async def create_classroom(
    classroom_in: ClassroomCreate,
    db: DB,
    current_user: CurrentUser,
) -> ClassroomResponse:
    """
    Create a new classroom.
    """
    # Always use the institution ID from the token for security
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Create the classroom with the institution ID from the token
    classroom = await repository.create(db, obj_in=classroom_in, institution_id=institution_id)
    return classroom


@router.get("/", response_model=List[ClassroomResponse])
async def get_classrooms(
    db: DB,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    room_type_id: UUID = None
) -> List[ClassroomResponse]:
    """
    Get all classrooms for the current institution, with optional filtering by room type.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Get classrooms filtered by institution ID and optionally room type
    query_filters = {"institution_id": institution_id}
    if room_type_id:
        query_filters["room_type_id"] = room_type_id
    
    classrooms = await repository.get_multi_with_filters(
        db, skip=skip, limit=limit, filters=query_filters
    )
    return classrooms


@router.get("/{classroom_id}", response_model=ClassroomDetailResponse)
async def get_classroom(
    classroom_id: UUID,
    db: DB,
    current_user: CurrentUser,
) -> ClassroomDetailResponse:
    """
    Get a specific classroom by ID.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Get classroom filtered by institution ID (multi-tenant security)
    classroom = await repository.get_by_id_with_details(db, id=classroom_id, institution_id=institution_id)
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found",
        )
    return classroom


@router.patch("/{classroom_id}", response_model=ClassroomResponse)
async def update_classroom(
    classroom_id: UUID,
    classroom_update: ClassroomUpdate,
    db: DB,
    current_user: CurrentUser,
) -> ClassroomResponse:
    """
    Update a classroom.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Get current classroom (with tenant security)
    classroom = await repository.get_by_id(db, id=classroom_id, institution_id=institution_id)
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found",
        )
    
    # Update classroom
    updated_classroom = await repository.update(db, obj_current=classroom, obj_in=classroom_update)
    return updated_classroom


@router.delete("/{classroom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_classroom(
    classroom_id: UUID,
    db: DB,
    current_user: CurrentUser,
) -> None:
    """
    Delete a classroom.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Delete the classroom (with tenant security)
    deleted = await repository.delete(db, id=classroom_id, institution_id=institution_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found",
        )
