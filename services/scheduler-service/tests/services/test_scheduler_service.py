"""
Tests for the scheduler service
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from uuid import UUID, uuid4
from datetime import datetime

from app.services.scheduler_service import SchedulerService
from app.schemas.scheduler import SchedulingRequest, SchedulingStatus, AlgorithmType

pytestmark = pytest.mark.asyncio


@pytest.fixture
def scheduler_service():
    """Create a scheduler service for testing"""
    return SchedulerService(data_service_url="http://mock-data-service:8000/api/v1")


@pytest.fixture
def scheduling_request():
    """Create a sample scheduling request"""
    return SchedulingRequest(
        name="Test Schedule",
        description="Test schedule for unit testing",
        academic_term="Fall 2025",
        start_date="2025-09-01",
        end_date="2025-12-15",
        algorithm_type=AlgorithmType.CSP
    )


@pytest.fixture
def auth_headers():
    """Create sample auth headers"""
    return {
        "Authorization": "Bearer test_token",
        "X-Institution-ID": str(uuid4())
    }


@patch("app.worker.worker_manager.worker_manager.submit_job")
async def test_create_scheduling_job(mock_submit_job, scheduler_service, scheduling_request, auth_headers):
    """Test creating a scheduling job"""
    # Make the mock submit_job function do nothing
    mock_submit_job.return_value = None
    
    # Create a job
    job_status = await scheduler_service.create_scheduling_job(scheduling_request, auth_headers)
    
    # Check that job was created with correct status
    assert job_status is not None
    assert job_status.status == SchedulingStatus.QUEUED
    
    # Check that submit_job was called
    mock_submit_job.assert_called_once()
    assert mock_submit_job.call_args[0][0] == job_status.job_id  # job_id
    assert mock_submit_job.call_args[0][1] == job_status  # job_status
    assert mock_submit_job.call_args[0][2] == scheduler_service._process_scheduling_job  # process_func
    assert mock_submit_job.call_args[0][3] == job_status.job_id  # job_id arg
    assert mock_submit_job.call_args[0][4] == scheduling_request  # request arg


@patch("app.worker.worker_manager.worker_manager.get_job_status")
async def test_get_job_status(mock_get_job_status, scheduler_service):
    """Test getting job status"""
    job_id = uuid4()
    mock_status = MagicMock()
    mock_get_job_status.return_value = mock_status
    
    # Get job status
    status = await scheduler_service.get_job_status(job_id)
    
    # Check that status was returned and get_job_status was called
    assert status == mock_status
    mock_get_job_status.assert_called_once_with(job_id)


@patch("app.worker.worker_manager.worker_manager.get_queue_status")
async def test_get_queue_status(mock_get_queue_status, scheduler_service):
    """Test getting queue status"""
    mock_status = {"queue_size": 5, "running_workers": 2}
    mock_get_queue_status.return_value = mock_status
    
    # Get queue status
    status = await scheduler_service.get_queue_status()
    
    # Check that status was returned and get_queue_status was called
    assert status == mock_status
    mock_get_queue_status.assert_called_once()


@patch("app.services.scheduler_service.SchedulerService._fetch_scheduling_data")
@patch("app.services.scheduler_service.SchedulerService._run_scheduling_algorithm")
@patch("app.services.scheduler_service.SchedulerService._save_scheduling_results")
async def test_process_scheduling_job(
    mock_save_results,
    mock_run_algorithm,
    mock_fetch_data,
    scheduler_service,
    scheduling_request,
    auth_headers
):
    """Test processing a scheduling job"""
    # Set up mocks
    job_id = uuid4()
    mock_data = {"faculty": [], "batches": []}
    mock_fetch_data.return_value = mock_data
    
    schedule_generation_id = uuid4()
    mock_scheduling_results = {
        "sessions": [{"id": str(uuid4())}],
        "metrics": {
            "hard_constraint_violations": 0,
            "soft_constraint_violations": 2,
            "faculty_satisfaction_score": 85.0,
            "batch_satisfaction_score": 90.0,
            "room_utilization": 75.0
        }
    }
    mock_run_algorithm.return_value = (schedule_generation_id, mock_scheduling_results)
    
    # Create a mock job status that will be retrieved by worker manager
    with patch("app.worker.worker_manager.worker_manager.get_job_status") as mock_get_job_status:
        mock_job_status = MagicMock()
        mock_get_job_status.return_value = mock_job_status
        
        # Process the job
        result = await scheduler_service._process_scheduling_job(
            job_id, scheduling_request, auth_headers
        )
        
        # Check that the mocks were called
        mock_fetch_data.assert_called_once_with(scheduling_request, auth_headers)
        mock_run_algorithm.assert_called_once_with(mock_data, scheduling_request, auth_headers)
        mock_save_results.assert_called_once_with(schedule_generation_id, mock_scheduling_results, auth_headers)
        
        # Check that job status was updated
        assert mock_job_status.progress == 80.0
        assert mock_job_status.message == "Saving schedule to data service"
        
        # Check that result has the expected data
        assert result["schedule_generation_id"] == schedule_generation_id
        assert result["total_sessions"] == 1
        assert result["faculty_satisfaction_score"] == 85.0
