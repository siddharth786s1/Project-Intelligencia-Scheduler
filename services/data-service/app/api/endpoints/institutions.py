from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from typing import List

from app.api.dependencies import DB, CurrentUser, require_super_admin, check_is_super_admin
from app.db.repositories.institution_repository import InstitutionRepository
from app.schemas.institution import InstitutionCreate, InstitutionUpdate, InstitutionResponse

router = APIRouter()
repository = InstitutionRepository()

@router.post("/", response_model=InstitutionResponse, status_code=status.HTTP_201_CREATED)
async def create_institution(
    institution_in: InstitutionCreate,
    db: DB,
    current_user: CurrentUser,
) -> InstitutionResponse:
    """
    Create a new institution.
    """
    require_super_admin(current_user)
    institution = await repository.create(db, obj_in=institution_in)
    return institution


@router.get("/", response_model=List[InstitutionResponse])
async def get_institutions(
    db: DB,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> List[InstitutionResponse]:
    """
    Get all institutions.
    """
    # Only super admins can see all institutions
    if not check_is_super_admin(current_user):
        # Regular users can only see their own institution
        institutions = []
        if "institution_id" in current_user:
            inst_id = UUID(current_user["institution_id"])
            institution = await repository.get_by_id(db, id=inst_id)
            if institution:
                institutions = [institution]
    else:
        institutions = await repository.get_multi(db, skip=skip, limit=limit)
    
    return institutions


@router.get("/{institution_id}", response_model=InstitutionResponse)
async def get_institution(
    institution_id: UUID,
    db: DB,
    current_user: CurrentUser,
) -> InstitutionResponse:
    """
    Get a specific institution by ID.
    """
    # Regular users can only access their own institution
    if not check_is_super_admin(current_user) and (
        "institution_id" not in current_user or 
        UUID(current_user["institution_id"]) != institution_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this institution",
        )
    
    institution = await repository.get_by_id(db, id=institution_id)
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution not found",
        )
    return institution


@router.patch("/{institution_id}", response_model=InstitutionResponse)
async def update_institution(
    institution_id: UUID,
    institution_update: InstitutionUpdate,
    db: DB,
    current_user: CurrentUser,
) -> InstitutionResponse:
    """
    Update an institution.
    """
    # Check if user is authorized to update this institution
    if not check_is_super_admin(current_user):
        if "institution_id" not in current_user or UUID(current_user["institution_id"]) != institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this institution",
            )
    
    # Get current institution
    institution = await repository.get_by_id(db, id=institution_id)
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution not found",
        )
    
    # Update institution
    updated_institution = await repository.update(db, obj_current=institution, obj_in=institution_update)
    return updated_institution


@router.delete("/{institution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_institution(
    institution_id: UUID,
    db: DB,
    current_user: CurrentUser,
) -> None:
    """
    Delete an institution.
    """
    # Only super admin can delete institutions
    require_super_admin(current_user)
    
    # Delete the institution
    deleted = await repository.delete(db, id=institution_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution not found",
        )
