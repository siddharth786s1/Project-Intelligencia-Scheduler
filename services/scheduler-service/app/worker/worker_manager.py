"""
Worker manager for handling scheduling job queues and worker processes.
"""
import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Callable
from uuid import UUID
import multiprocessing
import json
from datetime import datetime

from app.schemas.scheduler import SchedulingJobStatus, SchedulingStatus
from app.core.errors import SchedulingException

logger = logging.getLogger(__name__)


class WorkerManager:
    """
    Manages scheduling job queues and worker processes.
    
    This class is responsible for:
    - Maintaining a queue of pending jobs
    - Managing a pool of worker processes
    - Tracking job status and results
    - Providing methods to submit and query jobs
    """
    
    def __init__(self, max_workers: int = 2, auto_start: bool = True):
        """
        Initialize the worker manager.
        
        Args:
            max_workers: Maximum number of concurrent worker processes
            auto_start: Whether to automatically start the worker task on initialization
        """
        self.max_workers = max_workers
        self.active_jobs: Dict[UUID, SchedulingJobStatus] = {}
        self.job_queue = asyncio.Queue()
        self.running_workers = 0
        self._worker_task = None
        
        # Create the worker task when initialized if auto_start is True
        if auto_start:
            try:
                self._start_worker_task()
            except RuntimeError:
                logger.warning("No running event loop, worker task not started automatically")
                # In test environments, we'll start the worker task manually
    
    def _start_worker_task(self):
        """Start the worker task if it's not already running."""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._worker_loop())
            logger.info("Worker task started")
    
    async def _worker_loop(self):
        """Main worker loop that processes jobs from the queue."""
        logger.info("Worker loop started")
        
        while True:
            # If we've reached the maximum number of workers, wait until one finishes
            if self.running_workers >= self.max_workers:
                await asyncio.sleep(0.5)
                continue
            
            try:
                # Try to get a job from the queue (non-blocking)
                job_data = await self.job_queue.get()
                
                # Increment running workers count
                self.running_workers += 1
                
                # Update job status
                job_id = job_data["job_id"]
                process_func = job_data["process_func"]
                
                if job_id in self.active_jobs:
                    self.active_jobs[job_id].status = SchedulingStatus.RUNNING
                    self.active_jobs[job_id].started_at = datetime.now().isoformat()
                
                # Process the job in a separate task
                asyncio.create_task(
                    self._process_job(job_id, process_func, job_data["args"], job_data["kwargs"])
                )
                
            except asyncio.QueueEmpty:
                # No jobs in the queue, sleep briefly
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.exception(f"Error in worker loop: {str(e)}")
                await asyncio.sleep(1)  # Sleep to avoid tight loop on error
    
    async def _process_job(
        self, 
        job_id: UUID, 
        process_func: Callable, 
        args: List[Any], 
        kwargs: Dict[str, Any]
    ):
        """
        Process a job and update its status.
        
        Args:
            job_id: The ID of the job
            process_func: The function to call to process the job
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
        """
        try:
            logger.info(f"Processing job {job_id}")
            
            # Call the processing function
            result = await process_func(*args, **kwargs)
            
            # Update job status to completed
            if job_id in self.active_jobs:
                self.active_jobs[job_id].status = SchedulingStatus.COMPLETED
                self.active_jobs[job_id].completed_at = datetime.now().isoformat()
                self.active_jobs[job_id].progress = 100.0
                
                # Add result data if available
                if isinstance(result, dict):
                    for key, value in result.items():
                        setattr(self.active_jobs[job_id], key, value)
            
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            logger.exception(f"Error processing job {job_id}: {str(e)}")
            
            # Update job status to failed
            if job_id in self.active_jobs:
                self.active_jobs[job_id].status = SchedulingStatus.FAILED
                self.active_jobs[job_id].completed_at = datetime.now().isoformat()
                self.active_jobs[job_id].error = str(e)
        
        finally:
            # Decrement running workers count
            self.running_workers -= 1
    
    async def submit_job(
        self, 
        job_id: UUID, 
        job_status: SchedulingJobStatus,
        process_func: Callable, 
        *args, 
        **kwargs
    ):
        """
        Submit a job to the worker queue.
        
        Args:
            job_id: The ID of the job
            job_status: Initial job status
            process_func: The function to call to process the job
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        """
        # Store the job status
        self.active_jobs[job_id] = job_status
        
        # Add the job to the queue
        await self.job_queue.put({
            "job_id": job_id,
            "process_func": process_func,
            "args": args,
            "kwargs": kwargs
        })
        
        logger.info(f"Job {job_id} submitted to queue")
        
        # Make sure the worker task is running
        self._start_worker_task()
    
    def get_job_status(self, job_id: UUID) -> Optional[SchedulingJobStatus]:
        """
        Get the status of a job.
        
        Args:
            job_id: The ID of the job
            
        Returns:
            The job status, or None if the job doesn't exist
        """
        return self.active_jobs.get(job_id)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get the status of the job queue.
        
        Returns:
            A dictionary with queue statistics
        """
        return {
            "queue_size": self.job_queue.qsize(),
            "running_workers": self.running_workers,
            "max_workers": self.max_workers,
            "active_jobs": len(self.active_jobs),
            "worker_task_running": self._worker_task is not None and not self._worker_task.done()
        }
    
    async def cancel_job(self, job_id: UUID) -> bool:
        """
        Cancel a job if it's in the queue or mark it as cancelled if it's running.
        
        Args:
            job_id: The ID of the job to cancel
            
        Returns:
            True if the job was cancelled, False if it doesn't exist
        """
        # Check if the job exists
        if job_id not in self.active_jobs:
            return False
        
        # Get current status
        current_status = self.active_jobs[job_id].status
        
        # If the job is queued, we can simply mark it as cancelled
        if current_status == SchedulingStatus.QUEUED:
            self.active_jobs[job_id].status = SchedulingStatus.CANCELLED
            self.active_jobs[job_id].completed_at = datetime.now().isoformat()
            self.active_jobs[job_id].message = "Job cancelled before execution"
            return True
        
        # If the job is running, we can mark it as cancelled
        # but the actual processing will continue until it completes
        elif current_status == SchedulingStatus.RUNNING:
            self.active_jobs[job_id].status = SchedulingStatus.CANCELLED
            self.active_jobs[job_id].completed_at = datetime.now().isoformat()
            self.active_jobs[job_id].message = "Job marked for cancellation while running"
            return True
            
        # Job is already in a final state
        return False
    
    async def shutdown(self):
        """
        Gracefully shutdown the worker manager.
        Waits for current jobs to complete but doesn't accept new ones.
        """
        logger.info("Shutting down worker manager...")
        
        # Cancel the worker task
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            
            try:
                await self._worker_task
            except asyncio.CancelledError:
                logger.info("Worker task cancelled")
        
        # Wait for running workers to finish
        while self.running_workers > 0:
            logger.info(f"Waiting for {self.running_workers} workers to finish...")
            await asyncio.sleep(0.5)
        
        logger.info("Worker manager shut down successfully")


# Create a singleton instance
worker_manager = WorkerManager(max_workers=2, auto_start=True)
