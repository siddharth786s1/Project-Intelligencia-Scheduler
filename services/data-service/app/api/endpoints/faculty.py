from uuid import UUID
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.dependencies import get_current_institution_id
from app.db.repositories.faculty_repository import FacultyRepository
from app.schemas.faculty import (
    FacultyCreate, FacultyUpdate, FacultyResponse, FacultyDetailResponse
)
from app.schemas.common import PaginationParams
from app.schemas.response import PaginatedResponseModel, ResponseModel

router = APIRouter()
faculty_repository = FacultyRepository(model="Faculty")


@router.post("", response_model=ResponseModel[FacultyResponse])
async def create_faculty(
    faculty: FacultyCreate,
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Create a new faculty member."""
    faculty_data = faculty.model_dump()
    created_faculty = await faculty_repository.create(db, faculty_data, institution_id)
    return ResponseModel(
        data=created_faculty,
        message="Faculty created successfully"
    )


@router.get("", response_model=PaginatedResponseModel[List[FacultyResponse]])
async def get_all_faculty(
    pagination: PaginationParams = Depends(),
    department_id: Optional[UUID] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Get all faculty members with optional filtering."""
    faculty_list, total_count = await faculty_repository.get_all(
        db, 
        institution_id, 
        skip=pagination.skip, 
        limit=pagination.limit,
        department_id=department_id,
        search=search
    )
    
    return PaginatedResponseModel(
        data=faculty_list,
        count=len(faculty_list),
        total=total_count,
        page=pagination.page,
        pages=(total_count // pagination.limit) + (1 if total_count % pagination.limit else 0)
    )


@router.get("/{faculty_id}", response_model=ResponseModel[FacultyResponse])
async def get_faculty(
    faculty_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Get a specific faculty member by ID."""
    faculty = await faculty_repository.get(db, faculty_id, institution_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    return ResponseModel(
        data=faculty,
        message="Faculty retrieved successfully"
    )


@router.get("/{faculty_id}/details", response_model=ResponseModel[FacultyDetailResponse])
async def get_faculty_details(
    faculty_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Get a specific faculty member with department details."""
    faculty_data = await faculty_repository.get_faculty_with_department(db, faculty_id, institution_id)
    if not faculty_data:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    return ResponseModel(
        data=faculty_data,
        message="Faculty details retrieved successfully"
    )


@router.put("/{faculty_id}", response_model=ResponseModel[FacultyResponse])
async def update_faculty(
    faculty: FacultyUpdate,
    faculty_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Update a faculty member."""
    # Check if faculty exists
    existing_faculty = await faculty_repository.get(db, faculty_id, institution_id)
    if not existing_faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    # Update faculty
    faculty_data = faculty.model_dump(exclude_unset=True)
    updated_faculty = await faculty_repository.update(db, faculty_id, faculty_data, institution_id)
    
    return ResponseModel(
        data=updated_faculty,
        message="Faculty updated successfully"
    )


@router.delete("/{faculty_id}", response_model=ResponseModel[bool])
async def delete_faculty(
    faculty_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Delete a faculty member."""
    # Check if faculty exists
    existing_faculty = await faculty_repository.get(db, faculty_id, institution_id)
    if not existing_faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    # Delete faculty
    result = await faculty_repository.delete(db, faculty_id, institution_id)
    
    return ResponseModel(
        data=result,
        message="Faculty deleted successfully"
    )
