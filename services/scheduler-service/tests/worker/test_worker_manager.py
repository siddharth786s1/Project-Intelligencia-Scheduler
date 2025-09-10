"""
Tests for the worker manager
"""
import asyncio
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
import time
from datetime import datetime

from app.worker.worker_manager import WorkerManager
from app.schemas.scheduler import SchedulingJobStatus, SchedulingStatus

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
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
    # Create an event for each test to control the workflow
    job_events = {}
    job_results = {}
    completed_count = 0
    all_completed = asyncio.Event()
    
    # Define the async process function
    async def test_process_func(job_index):
        # Short delay to simulate work
        await asyncio.sleep(0.1)
        # Update results and mark as done
        job_results[job_index] = f"Job {job_index} completed"
        job_events[job_index].set()
        nonlocal completed_count
        completed_count += 1
        if completed_count >= 3:  # When all jobs complete
            all_completed.set()
        return {"status": "success", "index": job_index}
    
    # Submit three jobs 
    for i in range(3):
        job_id = uuid4()
        job_events[i] = asyncio.Event()
        
        job_status = SchedulingJobStatus(
            job_id=job_id,
            status=SchedulingStatus.QUEUED,
            message=f"Test job {i}",
            created_at=datetime.now().isoformat()
        )
        
        # Need to create a closure to capture the current value of i
        async def create_func(idx):
            return lambda: test_process_func(idx)
        
        process_func = await create_func(i)
        
        # Submit job
        await worker_manager.submit_job(
            job_id,
            job_status,
            process_func
        )
    
    # Wait for all jobs to complete with timeout
    try:
        await asyncio.wait_for(all_completed.wait(), timeout=3.0)
    except asyncio.TimeoutError:
        assert False, f"Jobs did not complete in time. Completed: {completed_count}/3"
    
    # Verify all jobs ran
    assert len(job_results) == 3, f"Expected 3 job results, got {len(job_results)}"
    for i in range(3):
        assert i in job_results, f"Job {i} did not complete"
        assert job_events[i].is_set(), f"Event for job {i} was not set"


async def test_queue_management(worker_manager):
    """Test that the queue properly manages jobs when workers are busy"""
    # Submit more jobs than workers (worker_manager has max_workers=2)
    job_ids = []
    job_completion_events = {}
    
    # Define a custom process function factory with delay
    async def make_process_func(j_id, delay):
        async def process_func():
            await asyncio.sleep(delay)  # Simulate work
            job_completion_events[j_id].set()
            return {"test_result": f"Job {j_id} completed"}
        return process_func
    
    # Create 4 jobs (more than the 2 max workers)
    for i in range(4):
        job_id = uuid4()
        job_ids.append(job_id)
        job_completion_events[job_id] = asyncio.Event()
        
        job_status = SchedulingJobStatus(
            job_id=job_id,
            status=SchedulingStatus.QUEUED,
            message=f"Test job {i}",
            created_at=datetime.now().isoformat()
        )
        
        # Create the process function with appropriate delay
        process_func = await make_process_func(job_id, 0.2)
        
        # Submit job
        await worker_manager.submit_job(
            job_id,
            job_status,
            process_func
        )
    
    # Check queue status immediately after submission
    # Should have at least 2 jobs in the queue (while 2 are running)
    queue_status = worker_manager.get_queue_status()
    assert queue_status["queue_size"] >= 2, "Queue should have at least 2 jobs waiting"
    
    # Wait for all jobs to complete (with timeout)
    await asyncio.gather(*[
        asyncio.wait_for(job_completion_events[j_id].wait(), timeout=3.0) 
        for j_id in job_ids
    ])
    
    # Give worker manager time to update job statuses
    await asyncio.sleep(0.2)
    
    # All jobs should be completed now
    for job_id in job_ids:
        assert worker_manager.get_job_status(job_id).status == SchedulingStatus.COMPLETED, \
            f"Job {job_id} should be COMPLETED but is {worker_manager.get_job_status(job_id).status}"


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
    # Use the worker_manager fixture that's already set up properly
    # We'll make it only process one job at a time for this test
    worker_manager.max_workers = 1
    
    # Create a shared execution order tracking list
    execution_order = []
    all_jobs_processed = asyncio.Event()
    
    # Define the process function that records execution order
    async def create_priority_process_func(job_idx, priority):
        async def process_func():
            # Record the job execution with its priority
            execution_order.append((job_idx, priority))
            
            # If this is the last job, signal that all jobs are done
            if len(execution_order) == 3:
                all_jobs_processed.set()
                
            # Small delay to simulate work
            await asyncio.sleep(0.1)
            return {"result": f"Job {job_idx} with priority {priority} completed"}
        return process_func
    
    # Submit jobs with mixed priorities
    # We'll submit them in this order: low, medium, high
    # But expect them to be executed in reverse: high, medium, low
    priorities = [0, 1, 2]  # Low, Medium, High
    job_ids = []
    
    for i, priority in enumerate(priorities):
        job_id = uuid4()
        job_ids.append(job_id)
        
        job_status = SchedulingJobStatus(
            job_id=job_id,
            status=SchedulingStatus.QUEUED,
            message=f"Priority test job {i}",
            created_at=datetime.now().isoformat()
        )
        
        # Create the process function for this job
        process_func = await create_priority_process_func(i, priority)
        
        # Submit job with priority
        await worker_manager.submit_job(
            job_id,
            job_status,
            process_func,
            priority=priority
        )
    
    # Wait for all jobs to complete
    try:
        await asyncio.wait_for(all_jobs_processed.wait(), timeout=5.0)
    except asyncio.TimeoutError:
        assert False, f"Not all jobs completed in time. Execution order: {execution_order}"
    
    # Extract just the priorities from the execution order
    execution_priorities = [priority for _, priority in execution_order]
    
    # Jobs should be executed in descending priority order (2, 1, 0)
    expected_priorities = sorted(priorities, reverse=True)
    
    assert execution_priorities == expected_priorities, \
        f"Jobs were not executed in priority order. Got: {execution_priorities}, Expected: {expected_priorities}"
