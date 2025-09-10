from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Query, Path
from typing import List

from app.api.dependencies import DB, CurrentUser, get_institution_id_from_token
from app.db.repositories.room_type_repository import RoomTypeRepository
from app.schemas.room_type import RoomTypeCreate, RoomTypeUpdate, RoomTypeResponse

router = APIRouter()
repository = RoomTypeRepository()

@router.post("/", response_model=RoomTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_room_type(
    room_type_in: RoomTypeCreate,
    db: DB,
    current_user: CurrentUser,
) -> RoomTypeResponse:
    """
    Create a new room type.
    """
    # Always use the institution ID from the token for security
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Create the room type with the institution ID from the token
    room_type = await repository.create(db, obj_in=room_type_in, institution_id=institution_id)
    return room_type


@router.get("/", response_model=List[RoomTypeResponse])
async def get_room_types(
    db: DB,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> List[RoomTypeResponse]:
    """
    Get all room types for the current institution.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Get room types filtered by institution ID
    room_types = await repository.get_multi(
        db, skip=skip, limit=limit, institution_id=institution_id
    )
    return room_types


@router.get("/{room_type_id}", response_model=RoomTypeResponse)
async def get_room_type(
    room_type_id: UUID,
    db: DB,
    current_user: CurrentUser,
) -> RoomTypeResponse:
    """
    Get a specific room type by ID.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Get room type filtered by institution ID (multi-tenant security)
    room_type = await repository.get_by_id(db, id=room_type_id, institution_id=institution_id)
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )
    return room_type


@router.patch("/{room_type_id}", response_model=RoomTypeResponse)
async def update_room_type(
    room_type_id: UUID,
    room_type_update: RoomTypeUpdate,
    db: DB,
    current_user: CurrentUser,
) -> RoomTypeResponse:
    """
    Update a room type.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Get current room type (with tenant security)
    room_type = await repository.get_by_id(db, id=room_type_id, institution_id=institution_id)
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )
    
    # Update room type
    updated_room_type = await repository.update(db, obj_current=room_type, obj_in=room_type_update)
    return updated_room_type


@router.delete("/{room_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_type(
    room_type_id: UUID,
    db: DB,
    current_user: CurrentUser,
) -> None:
    """
    Delete a room type.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Delete the room type (with tenant security)
    deleted = await repository.delete(db, id=room_type_id, institution_id=institution_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )
