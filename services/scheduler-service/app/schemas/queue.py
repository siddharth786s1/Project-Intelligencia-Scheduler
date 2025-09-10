"""
Scheduler queue status schema
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class QueueStatus(BaseModel):
    """Status of the scheduling job queue"""
    queue_size: int = Field(..., description="Number of jobs in the queue")
    running_workers: int = Field(..., description="Number of workers currently running")
    max_workers: int = Field(..., description="Maximum number of concurrent workers")
    active_jobs: int = Field(..., description="Total number of active jobs (including running)")
    worker_task_running: bool = Field(..., description="Whether the worker task is running")
