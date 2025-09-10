from uuid import UUID
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.dependencies import get_current_institution_id
from app.db.repositories.faculty_repository import FacultyRepository
from app.db.repositories.faculty_preferences_repository import (
    FacultyAvailabilityRepository,
    FacultySubjectExpertiseRepository,
    FacultyTeachingPreferenceRepository
)
from app.schemas.faculty_preferences import (
    # Availability schemas
    FacultyAvailabilityCreate,
    FacultyAvailabilityUpdate,
    FacultyAvailabilityResponse,
    # Subject expertise schemas
    FacultySubjectExpertiseCreate,
    FacultySubjectExpertiseUpdate,
    FacultySubjectExpertiseResponse,
    # Batch preference schemas
    FacultyBatchPreferenceCreate,
    FacultyBatchPreferenceUpdate,
    FacultyBatchPreferenceResponse,
    # Classroom preference schemas
    FacultyClassroomPreferenceCreate,
    FacultyClassroomPreferenceUpdate,
    FacultyClassroomPreferenceResponse,
    # Combined response
    FacultyPreferencesResponse
)
from app.schemas.response import ResponseModel

router = APIRouter()
faculty_repository = FacultyRepository(model="Faculty")
faculty_availability_repository = FacultyAvailabilityRepository(model="FacultyAvailability")
faculty_expertise_repository = FacultySubjectExpertiseRepository(model="FacultySubjectExpertise")
faculty_preference_repository = FacultyTeachingPreferenceRepository(model="FacultyTeachingPreference")


# Faculty Availability Endpoints
@router.post("/availability", response_model=ResponseModel[FacultyAvailabilityResponse])
async def create_faculty_availability(
    availability: FacultyAvailabilityCreate,
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Create a new faculty availability record."""
    # Check if faculty exists
    faculty = await faculty_repository.get(db, availability.faculty_id, institution_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    # Convert the Pydantic model to a dict for the repository
    availability_data = {
        "faculty_id": availability.faculty_id,
        "day_of_week": availability.day_of_week,
        "time_slot": availability.time_slot,
        "is_available": availability.is_available
    }
    
    created_availability = await faculty_availability_repository.create(
        db, 
        availability_data, 
        institution_id
    )
    
    return ResponseModel(
        data=created_availability,
        message="Faculty availability created successfully"
    )


@router.get("/availability/{faculty_id}", response_model=ResponseModel[List[FacultyAvailabilityResponse]])
async def get_faculty_availability(
    faculty_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Get all availability records for a faculty member."""
    # Check if faculty exists
    faculty = await faculty_repository.get(db, faculty_id, institution_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    availability_list = await faculty_availability_repository.get_all_by_faculty(
        db, 
        faculty_id, 
        institution_id
    )
    
    return ResponseModel(
        data=availability_list,
        message="Faculty availability retrieved successfully"
    )


@router.put("/availability/{availability_id}", response_model=ResponseModel[FacultyAvailabilityResponse])
async def update_faculty_availability(
    availability_update: FacultyAvailabilityUpdate,
    availability_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Update a faculty availability record."""
    # Check if availability record exists
    existing_availability = await faculty_availability_repository.get(db, availability_id, institution_id)
    if not existing_availability:
        raise HTTPException(status_code=404, detail="Faculty availability record not found")
    
    # Update availability
    availability_data = availability_update.model_dump(exclude_unset=True)
    updated_availability = await faculty_availability_repository.update(
        db, 
        availability_id, 
        availability_data, 
        institution_id
    )
    
    return ResponseModel(
        data=updated_availability,
        message="Faculty availability updated successfully"
    )


@router.delete("/availability/{availability_id}", response_model=ResponseModel[bool])
async def delete_faculty_availability(
    availability_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Delete a faculty availability record."""
    # Check if availability record exists
    existing_availability = await faculty_availability_repository.get(db, availability_id, institution_id)
    if not existing_availability:
        raise HTTPException(status_code=404, detail="Faculty availability record not found")
    
    # Delete availability
    result = await faculty_availability_repository.delete(db, availability_id, institution_id)
    
    return ResponseModel(
        data=result,
        message="Faculty availability deleted successfully"
    )


# Faculty Subject Expertise Endpoints
@router.post("/expertise", response_model=ResponseModel[FacultySubjectExpertiseResponse])
async def create_faculty_expertise(
    expertise: FacultySubjectExpertiseCreate,
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Create a new faculty subject expertise record."""
    # Check if faculty exists
    faculty = await faculty_repository.get(db, expertise.faculty_id, institution_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    # Convert the Pydantic model to a dict for the repository
    expertise_data = {
        "faculty_id": expertise.faculty_id,
        "subject_id": expertise.subject_id,
        "expertise_level": expertise.expertise_level.value
    }
    
    created_expertise = await faculty_expertise_repository.create(
        db, 
        expertise_data, 
        institution_id
    )
    
    return ResponseModel(
        data=created_expertise,
        message="Faculty expertise created successfully"
    )


@router.get("/expertise/{faculty_id}", response_model=ResponseModel[List[FacultySubjectExpertiseResponse]])
async def get_faculty_expertise(
    faculty_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Get all subject expertise records for a faculty member."""
    # Check if faculty exists
    faculty = await faculty_repository.get(db, faculty_id, institution_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    expertise_list = await faculty_expertise_repository.get_all_by_faculty(
        db, 
        faculty_id, 
        institution_id
    )
    
    return ResponseModel(
        data=expertise_list,
        message="Faculty expertise retrieved successfully"
    )


@router.put("/expertise/{expertise_id}", response_model=ResponseModel[FacultySubjectExpertiseResponse])
async def update_faculty_expertise(
    expertise_update: FacultySubjectExpertiseUpdate,
    expertise_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Update a faculty subject expertise record."""
    # Check if expertise record exists
    existing_expertise = await faculty_expertise_repository.get(db, expertise_id, institution_id)
    if not existing_expertise:
        raise HTTPException(status_code=404, detail="Faculty expertise record not found")
    
    # Update expertise
    expertise_data = expertise_update.model_dump(exclude_unset=True)
    if "expertise_level" in expertise_data:
        expertise_data["expertise_level"] = expertise_data["expertise_level"].value
    
    updated_expertise = await faculty_expertise_repository.update(
        db, 
        expertise_id, 
        expertise_data, 
        institution_id
    )
    
    return ResponseModel(
        data=updated_expertise,
        message="Faculty expertise updated successfully"
    )


@router.delete("/expertise/{expertise_id}", response_model=ResponseModel[bool])
async def delete_faculty_expertise(
    expertise_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Delete a faculty subject expertise record."""
    # Check if expertise record exists
    existing_expertise = await faculty_expertise_repository.get(db, expertise_id, institution_id)
    if not existing_expertise:
        raise HTTPException(status_code=404, detail="Faculty expertise record not found")
    
    # Delete expertise
    result = await faculty_expertise_repository.delete(db, expertise_id, institution_id)
    
    return ResponseModel(
        data=result,
        message="Faculty expertise deleted successfully"
    )


# Faculty Batch Preferences Endpoints
@router.post("/batch-preference", response_model=ResponseModel[FacultyBatchPreferenceResponse])
async def create_batch_preference(
    preference: FacultyBatchPreferenceCreate,
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Create a new faculty batch preference."""
    # Check if faculty exists
    faculty = await faculty_repository.get(db, preference.faculty_id, institution_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    # Convert the Pydantic model to a dict for the repository
    preference_data = {
        "faculty_id": preference.faculty_id,
        "batch_id": preference.batch_id,
        "preference_type": preference.preference_level.value,
        "preference_weight": 3  # Default weight
    }
    
    created_preference = await faculty_preference_repository.create(
        db, 
        preference_data, 
        institution_id
    )
    
    return ResponseModel(
        data=created_preference,
        message="Batch preference created successfully"
    )


@router.get("/batch-preference/{faculty_id}", response_model=ResponseModel[List[FacultyBatchPreferenceResponse]])
async def get_batch_preferences(
    faculty_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Get all batch preferences for a faculty member."""
    # Check if faculty exists
    faculty = await faculty_repository.get(db, faculty_id, institution_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    preference_list = await faculty_preference_repository.get_batch_preferences(
        db, 
        faculty_id, 
        institution_id
    )
    
    return ResponseModel(
        data=preference_list,
        message="Batch preferences retrieved successfully"
    )


# Faculty Classroom Preferences Endpoints
@router.post("/classroom-preference", response_model=ResponseModel[FacultyClassroomPreferenceResponse])
async def create_classroom_preference(
    preference: FacultyClassroomPreferenceCreate,
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Create a new faculty classroom preference."""
    # Check if faculty exists
    faculty = await faculty_repository.get(db, preference.faculty_id, institution_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    # Convert the Pydantic model to a dict for the repository
    preference_data = {
        "faculty_id": preference.faculty_id,
        "classroom_id": preference.classroom_id,
        "preference_type": preference.preference_level.value,
        "preference_weight": 3  # Default weight
    }
    
    created_preference = await faculty_preference_repository.create(
        db, 
        preference_data, 
        institution_id
    )
    
    return ResponseModel(
        data=created_preference,
        message="Classroom preference created successfully"
    )


@router.get("/classroom-preference/{faculty_id}", response_model=ResponseModel[List[FacultyClassroomPreferenceResponse]])
async def get_classroom_preferences(
    faculty_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Get all classroom preferences for a faculty member."""
    # Check if faculty exists
    faculty = await faculty_repository.get(db, faculty_id, institution_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    preference_list = await faculty_preference_repository.get_classroom_preferences(
        db, 
        faculty_id, 
        institution_id
    )
    
    return ResponseModel(
        data=preference_list,
        message="Classroom preferences retrieved successfully"
    )


# Combined Faculty Preferences
@router.get("/{faculty_id}/all-preferences", response_model=ResponseModel[FacultyPreferencesResponse])
async def get_all_faculty_preferences(
    faculty_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    institution_id: UUID = Depends(get_current_institution_id)
):
    """Get all preferences for a faculty member."""
    # Check if faculty exists
    faculty = await faculty_repository.get(db, faculty_id, institution_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    # Get all types of preferences
    availability = await faculty_availability_repository.get_all_by_faculty(db, faculty_id, institution_id)
    expertise = await faculty_expertise_repository.get_all_by_faculty(db, faculty_id, institution_id)
    batch_preferences = await faculty_preference_repository.get_batch_preferences(db, faculty_id, institution_id)
    classroom_preferences = await faculty_preference_repository.get_classroom_preferences(db, faculty_id, institution_id)
    
    # Combine into a single response
    preferences = FacultyPreferencesResponse(
        faculty_id=faculty_id,
        availability=availability,
        subject_expertise=expertise,
        batch_preferences=batch_preferences,
        classroom_preferences=classroom_preferences
    )
    
    return ResponseModel(
        data=preferences,
        message="All faculty preferences retrieved successfully"
    )
