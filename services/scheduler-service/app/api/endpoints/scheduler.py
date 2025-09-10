from typing import List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from httpx import AsyncClient

from app.api.dependencies import (
    get_data_service_client,
    forward_auth_header,
    fetch_data_from_service
)
from app.core.security import get_current_user, get_current_institution_id
from app.schemas.auth import CurrentUser
from app.schemas.scheduler import (
    SchedulingRequest,
    SchedulingJobStatus,
    ScheduleGenerationSummary,
    ResponseModel
)
from app.services.scheduler_service import scheduler_service
from app.core.errors import ServiceException, http_exception_from_service_error

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.post("/jobs", response_model=ResponseModel[SchedulingJobStatus])
async def create_scheduling_job(
    request: SchedulingRequest,
    req: Request,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Create a new scheduling job
    """
    try:
        auth_headers = await forward_auth_header(req)
        job_status = await scheduler_service.create_scheduling_job(request, auth_headers)
        return ResponseModel(
            data=job_status,
            message="Scheduling job created successfully"
        )
    except ServiceException as e:
        raise http_exception_from_service_error(e)


@router.get("/jobs/{job_id}", response_model=ResponseModel[SchedulingJobStatus])
async def get_job_status(
    job_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Get the status of a scheduling job
    """
    job_status = await scheduler_service.get_job_status(job_id)
    if not job_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return ResponseModel(
        data=job_status,
        message="Job status retrieved successfully"
    )


@router.get("/generations", response_model=ResponseModel[List[Dict[str, Any]]])
async def list_schedule_generations(
    req: Request,
    skip: int = 0,
    limit: int = 10,
    client: AsyncClient = Depends(get_data_service_client),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """
    List all schedule generations
    """
    try:
        auth_headers = await forward_auth_header(req)
        endpoint = f"/scheduled-sessions/generations?skip={skip}&limit={limit}"
        result = await fetch_data_from_service(client, endpoint, auth_headers)
        return ResponseModel(
            data=result["data"],
            message="Schedule generations retrieved successfully"
        )
    except ServiceException as e:
        raise http_exception_from_service_error(e)


@router.get("/generations/{generation_id}", response_model=ResponseModel[ScheduleGenerationSummary])
async def get_schedule_generation(
    generation_id: UUID,
    req: Request,
    client: AsyncClient = Depends(get_data_service_client),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """
    Get a specific schedule generation
    """
    try:
        auth_headers = await forward_auth_header(req)
        endpoint = f"/scheduled-sessions/generations/{generation_id}"
        result = await fetch_data_from_service(client, endpoint, auth_headers)
        return ResponseModel(
            data=result["data"],
            message="Schedule generation retrieved successfully"
        )
    except ServiceException as e:
        raise http_exception_from_service_error(e)


@router.delete("/generations/{generation_id}", response_model=ResponseModel[bool])
async def delete_schedule_generation(
    generation_id: UUID,
    req: Request,
    client: AsyncClient = Depends(get_data_service_client),
    institution_id: UUID = Depends(get_current_institution_id),
):
    """
    Delete a schedule generation and all its sessions
    """
    try:
        auth_headers = await forward_auth_header(req)
        endpoint = f"/scheduled-sessions/generations/{generation_id}"
        result = await fetch_data_from_service(
            client, endpoint, auth_headers, method="DELETE"
        )
        return ResponseModel(
            data=result["data"],
            message="Schedule generation deleted successfully"
        )
    except ServiceException as e:
        raise http_exception_from_service_error(e)
