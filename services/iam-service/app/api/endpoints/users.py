from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.security import (
    get_current_user,
    get_current_active_superuser,
    get_current_institution_admin,
    get_password_hash,
)
from app.db.database import get_db
from app.db.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.response import PaginatedResponse
from app.core.errors import (
    UserNotFoundException,
    EmailAlreadyExistsException,
    PermissionDeniedException,
)

router = APIRouter()

@router.get("", response_model=PaginatedResponse[UserResponse])
async def get_users(
    page: int = Query(1, gt=0),
    page_size: int = Query(50, gt=0, le=100),
    role_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all users with pagination.
    
    - Super admins can see all users
    - Institution admins can only see users from their institution
    """
    user_repo = UserRepository(db)
    
    # Apply filtering based on user role
    institution_id = None
    if current_user.role.name != "super_admin":
        institution_id = current_user.institution_id
    
    # Get paginated users
    paginated_users = await user_repo.get_users_paginated(
        page=page, 
        page_size=page_size, 
        role_id=role_id,
        institution_id=institution_id
    )
    
    return paginated_users

@router.get("/{id}", response_model=UserResponse)
async def get_user(
    id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a user by ID."""
    user_repo = UserRepository(db)
    user = await user_repo.get(id)
    
    if not user:
        raise UserNotFoundException()
    
    # Check permissions
    if (
        current_user.role.name != "super_admin" and
        current_user.institution_id != user.institution_id
    ):
        raise PermissionDeniedException()
    
    return user

@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_institution_admin),
):
    """
    Create a new user.
    
    - Super admins can create users for any institution
    - Institution admins can only create users for their institution
    """
    user_repo = UserRepository(db)
    
    # Check if email already exists
    existing_user = await user_repo.get_by_email(user_create.email)
    if existing_user:
        raise EmailAlreadyExistsException()
    
    # Check permissions
    if (
        current_user.role.name != "super_admin" and
        current_user.institution_id != user_create.institution_id
    ):
        raise PermissionDeniedException()
    
    # Hash password
    hashed_password = get_password_hash(user_create.password)
    
    # Create user
    user_data = user_create.dict()
    user_data["password_hash"] = hashed_password
    del user_data["password"]
    
    user = await user_repo.create(user_data)
    return user

@router.put("/{id}", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_institution_admin),
):
    """
    Update a user.
    
    - Super admins can update any user
    - Institution admins can only update users from their institution
    """
    user_repo = UserRepository(db)
    user = await user_repo.get(id)
    
    if not user:
        raise UserNotFoundException()
    
    # Check permissions
    if (
        current_user.role.name != "super_admin" and
        current_user.institution_id != user.institution_id
    ):
        raise PermissionDeniedException()
    
    # Update user data
    update_data = user_update.dict(exclude_unset=True)
    
    # Hash password if provided
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data["password"])
        del update_data["password"]
    
    # Update user
    updated_user = await user_repo.update(id, update_data)
    return updated_user

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_institution_admin),
):
    """
    Delete a user.
    
    - Super admins can delete any user
    - Institution admins can only delete users from their institution
    """
    user_repo = UserRepository(db)
    user = await user_repo.get(id)
    
    if not user:
        raise UserNotFoundException()
    
    # Check permissions
    if (
        current_user.role.name != "super_admin" and
        current_user.institution_id != user.institution_id
    ):
        raise PermissionDeniedException()
    
    # Delete user
    await user_repo.delete(id)
