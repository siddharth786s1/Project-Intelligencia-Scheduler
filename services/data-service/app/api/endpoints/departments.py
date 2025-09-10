from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from typing import List

from app.api.dependencies import DB, CurrentUser, get_institution_id_from_token
from app.db.repositories.department_repository import DepartmentRepository
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse

router = APIRouter()
repository = DepartmentRepository()

@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    department_in: DepartmentCreate,
    db: DB,
    current_user: CurrentUser,
) -> DepartmentResponse:
    """
    Create a new department.
    """
    # Always use the institution ID from the token for security
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Create the department with the institution ID from the token
    department = await repository.create(db, obj_in=department_in, institution_id=institution_id)
    return department


@router.get("/", response_model=List[DepartmentResponse])
async def get_departments(
    db: DB,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> List[DepartmentResponse]:
    """
    Get all departments for the current institution.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Get departments filtered by institution ID
    departments = await repository.get_multi(
        db, skip=skip, limit=limit, institution_id=institution_id
    )
    return departments


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: UUID,
    db: DB,
    current_user: CurrentUser,
) -> DepartmentResponse:
    """
    Get a specific department by ID.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Get department filtered by institution ID (multi-tenant security)
    department = await repository.get_by_id(db, id=department_id, institution_id=institution_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )
    return department


@router.patch("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: UUID,
    department_update: DepartmentUpdate,
    db: DB,
    current_user: CurrentUser,
) -> DepartmentResponse:
    """
    Update a department.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Get current department (with tenant security)
    department = await repository.get_by_id(db, id=department_id, institution_id=institution_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )
    
    # Update department
    updated_department = await repository.update(db, obj_current=department, obj_in=department_update)
    return updated_department


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: UUID,
    db: DB,
    current_user: CurrentUser,
) -> None:
    """
    Delete a department.
    """
    # Get institution ID from token
    institution_id = get_institution_id_from_token(current_user)
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institution",
        )
    
    # Delete the department (with tenant security)
    deleted = await repository.delete(db, id=department_id, institution_id=institution_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )
