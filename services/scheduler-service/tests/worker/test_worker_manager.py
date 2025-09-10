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
async def worker_manager():
    """Create a worker manager for testing"""
    manager = WorkerManager(max_workers=2, auto_start=False)
    # Manually start the worker task in the test event loop
    manager._start_worker_task()
    yield manager
    # Clean up after test
    await manager.shutdown()


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


async def test_concurrent_job_processing(worker_manager):
    """Test that multiple jobs can be processed concurrently"""
    # Create a worker manager with more workers
    worker_manager = WorkerManager(max_workers=3)
    
    # Track job completion
    job_completed = {}
    job_results = {}
    
    # Create 3 jobs with different processing times
    jobs = []
    for i in range(3):
        job_id = uuid4()
        job_status = SchedulingJobStatus(
            job_id=job_id,
            status=SchedulingStatus.QUEUED,
            message=f"Test job {i}",
            created_at=datetime.now().isoformat()
        )
        
        # Create a flag for this job
        job_completed[job_id] = asyncio.Event()
        
        # Mock process function with different delays
        async def mock_process(j_id=job_id, delay=(i+1)*0.2):
            await asyncio.sleep(delay)  # Different delays
            job_results[j_id] = {"result": f"job {j_id} completed"}
            job_completed[j_id].set()
            return job_results[j_id]
        
        # Submit job
        await worker_manager.submit_job(
            job_id,
            job_status,
            mock_process
        )
        jobs.append((job_id, job_status))
    
    # Wait for all jobs to complete
    await asyncio.gather(*[job_completed[j_id].wait() for j_id, _ in jobs])
    
    # Check all jobs completed
    for job_id, _ in jobs:
        assert job_id in job_results
        assert worker_manager.get_job_status(job_id).status == SchedulingStatus.COMPLETED


async def test_queue_management(worker_manager):
    """Test that the queue properly manages jobs when workers are busy"""
    # Create a worker manager with limited workers
    worker_manager = WorkerManager(max_workers=1)
    
    # Submit more jobs than workers
    job_ids = []
    for i in range(3):
        job_id = uuid4()
        job_ids.append(job_id)
        job_status = SchedulingJobStatus(
            job_id=job_id,
            status=SchedulingStatus.QUEUED,
            message=f"Test job {i}",
            created_at=datetime.now().isoformat()
        )
        
        # Mock process that takes time
        async def mock_process(delay=0.5):
            await asyncio.sleep(delay)
            return {"status": "completed"}
        
        # Submit job
        await worker_manager.submit_job(
            job_id,
            job_status,
            mock_process
        )
    
    # Check queue status immediately after submission
    queue_status = worker_manager.get_queue_status()
    assert queue_status["queue_size"] > 0
    
    # Wait for jobs to process
    await asyncio.sleep(2.0)
    
    # All jobs should be completed now
    for job_id in job_ids:
        assert worker_manager.get_job_status(job_id).status == SchedulingStatus.COMPLETED


async def test_job_cancellation(worker_manager):
    """Test that jobs can be cancelled"""
    job_id = uuid4()
    job_status = SchedulingJobStatus(
        job_id=job_id,
        status=SchedulingStatus.QUEUED,
        message="Test job to cancel",
        created_at=datetime.now().isoformat()
    )
    
    # Mock a long-running process
    async def mock_process():
        await asyncio.sleep(10.0)  # Long delay
        return {"status": "completed"}
    
    # Submit job
    await worker_manager.submit_job(
        job_id,
        job_status,
        mock_process
    )
    
    # Immediately cancel the job
    await worker_manager.cancel_job(job_id)
    
    # Check that the job was cancelled
    status = worker_manager.get_job_status(job_id)
    assert status is not None
    assert status.status == SchedulingStatus.CANCELLED


async def test_graceful_shutdown(worker_manager):
    """Test that the worker manager can shut down gracefully"""
    # Submit a job
    job_id = uuid4()
    job_status = SchedulingJobStatus(
        job_id=job_id,
        status=SchedulingStatus.QUEUED,
        message="Test job",
        created_at=datetime.now().isoformat()
    )
    
    # Mock process that takes time
    async def mock_process():
        await asyncio.sleep(0.5)
        return {"status": "completed"}
    
    # Submit job
    await worker_manager.submit_job(
        job_id,
        job_status,
        mock_process
    )
    
    # Start shutdown
    shutdown_task = asyncio.create_task(worker_manager.shutdown())
    
    # Wait for shutdown
    await shutdown_task
    
    # Check that the worker task is done
    assert worker_manager._worker_task.done()


async def test_job_priority(worker_manager):
    """Test that jobs with higher priority are processed first"""
    # Create a worker manager with limited workers
    worker_manager = WorkerManager(max_workers=1)
    
    # Track order of execution
    execution_order = []
    execution_event = asyncio.Event()
    
    # Create mock process function that records execution order
    async def mock_process(job_id, priority):
        await asyncio.sleep(0.1)  # Short delay
        execution_order.append((job_id, priority))
        if len(execution_order) == 3:
            execution_event.set()
        return {"status": "completed", "job_id": job_id}
    
    # Submit jobs with different priorities
    priorities = [0, 2, 1]  # normal, high, medium
    job_ids = []
    
    for i, priority in enumerate(priorities):
        job_id = uuid4()
        job_ids.append(job_id)
        job_status = SchedulingJobStatus(
            job_id=job_id,
            status=SchedulingStatus.QUEUED,
            message=f"Test job {i} with priority {priority}",
            created_at=datetime.now().isoformat(),
            priority=priority
        )
        
        # Submit job
        await worker_manager.submit_job(
            job_id,
            job_status,
            mock_process,
            job_id,
            priority=priority
        )
    
    # Wait for all jobs to complete
    await asyncio.wait_for(execution_event.wait(), timeout=5.0)
    
    # Check execution order - higher priority jobs should be executed first
    # Expected order: priority 2 (high), priority 1 (medium), priority 0 (normal)
    assert execution_order[0][1] > execution_order[1][1]
    assert execution_order[1][1] > execution_order[2][1]
