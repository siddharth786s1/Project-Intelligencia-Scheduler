"""
Tests for the worker manager
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
import time
from datetime import datetime

from app.worker.worker_manager import WorkerManager
from app.schemas.scheduler import SchedulingJobStatus, SchedulingStatus

pytestmark = pytest.mark.asyncio


@pytest.fixture
def worker_manager():
    """Create a worker manager for testing"""
    return WorkerManager(max_workers=2)


async def test_worker_manager_init(worker_manager):
    """Test that the worker manager initializes correctly"""
    assert worker_manager.max_workers == 2
    assert worker_manager.running_workers == 0
    assert worker_manager.job_queue.empty()
    assert worker_manager._worker_task is not None


async def test_get_queue_status(worker_manager):
    """Test getting queue status"""
    status = worker_manager.get_queue_status()
    assert status["queue_size"] == 0
    assert status["running_workers"] == 0
    assert status["max_workers"] == 2
    assert status["active_jobs"] == 0
    assert status["worker_task_running"] == True


async def test_job_submission(worker_manager):
    """Test submitting a job to the worker manager"""
    job_id = uuid4()
    job_status = SchedulingJobStatus(
        job_id=job_id,
        status=SchedulingStatus.QUEUED,
        message="Test job",
        created_at=datetime.now().isoformat()
    )
    
    # Mock process function
    async def mock_process(*args, **kwargs):
        return {"test_result": "success"}
    
    # Submit job
    await worker_manager.submit_job(
        job_id,
        job_status,
        mock_process,
        "arg1",
        kwarg1="value1"
    )
    
    # Check job is in active jobs
    assert job_id in worker_manager.active_jobs
    assert worker_manager.active_jobs[job_id] == job_status
    
    # Check job was added to queue
    assert worker_manager.job_queue.qsize() == 1


async def test_job_processing(worker_manager):
    """Test that a job gets processed correctly"""
    job_id = uuid4()
    job_status = SchedulingJobStatus(
        job_id=job_id,
        status=SchedulingStatus.QUEUED,
        message="Test job",
        created_at=datetime.now().isoformat()
    )
    
    result_flag = asyncio.Event()
    
    # Mock process function
    async def mock_process(*args, **kwargs):
        await asyncio.sleep(0.1)  # Simulate work
        result_flag.set()
        return {"test_result": "success"}
    
    # Submit job
    await worker_manager.submit_job(
        job_id,
        job_status,
        mock_process,
        "arg1",
        kwarg1="value1"
    )
    
    # Wait for processing to complete
    await asyncio.wait_for(result_flag.wait(), timeout=2.0)
    
    # Allow time for status update
    await asyncio.sleep(0.2)
    
    # Check job status was updated
    job_status = worker_manager.get_job_status(job_id)
    assert job_status is not None
    assert job_status.status == SchedulingStatus.COMPLETED


async def test_job_error_handling(worker_manager):
    """Test that errors in job processing are handled correctly"""
    job_id = uuid4()
    job_status = SchedulingJobStatus(
        job_id=job_id,
        status=SchedulingStatus.QUEUED,
        message="Test job",
        created_at=datetime.now().isoformat()
    )
    
    result_flag = asyncio.Event()
    
    # Mock process function that raises an exception
    async def mock_process(*args, **kwargs):
        await asyncio.sleep(0.1)  # Simulate work
        result_flag.set()
        raise ValueError("Test error")
    
    # Submit job
    await worker_manager.submit_job(
        job_id,
        job_status,
        mock_process,
        "arg1",
        kwarg1="value1"
    )
    
    # Wait for processing to complete
    await asyncio.wait_for(result_flag.wait(), timeout=2.0)
    
    # Allow time for status update
    await asyncio.sleep(0.2)
    
    # Check job status was updated
    job_status = worker_manager.get_job_status(job_id)
    assert job_status is not None
    assert job_status.status == SchedulingStatus.FAILED
    assert "Test error" in job_status.error
