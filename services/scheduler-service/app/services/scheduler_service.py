from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID, uuid4
import asyncio
import json
import time
import logging
from datetime import datetime, timedelta

import httpx
from fastapi import HTTPException, status

from app.core.errors import (
    DataServiceException,
    SchedulingException,
    ConstraintViolationException
)
from app.schemas.scheduler import (
    SchedulingStatus,
    SchedulingRequest,
    SchedulingJobStatus
)

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Main service for scheduling operations, coordinating between
    the data service and scheduling algorithms
    """
    
    def __init__(self, data_service_url: str):
        self.data_service_url = data_service_url
        self.active_jobs: Dict[UUID, SchedulingJobStatus] = {}
    
    async def create_scheduling_job(
        self, 
        request: SchedulingRequest,
        auth_headers: Dict[str, str]
    ) -> SchedulingJobStatus:
        """
        Create a new scheduling job and queue it for processing
        """
        job_id = uuid4()
        job_status = SchedulingJobStatus(
            job_id=job_id,
            status=SchedulingStatus.QUEUED,
            message="Job queued for processing",
            created_at=datetime.now().isoformat()
        )
        
        self.active_jobs[job_id] = job_status
        
        # Start job processing in background task
        asyncio.create_task(
            self._process_scheduling_job(job_id, request, auth_headers)
        )
        
        return job_status
    
    async def get_job_status(self, job_id: UUID) -> Optional[SchedulingJobStatus]:
        """
        Get the status of a scheduling job
        """
        return self.active_jobs.get(job_id)
    
    async def _process_scheduling_job(
        self, 
        job_id: UUID,
        request: SchedulingRequest,
        auth_headers: Dict[str, str]
    ):
        """
        Process a scheduling job (this runs in the background)
        """
        try:
            # Update job status
            self.active_jobs[job_id].status = SchedulingStatus.RUNNING
            self.active_jobs[job_id].started_at = datetime.now().isoformat()
            self.active_jobs[job_id].message = "Loading data from data service"
            self.active_jobs[job_id].progress = 10.0
            
            # 1. Fetch data from data service
            data = await self._fetch_scheduling_data(request, auth_headers)
            
            # Update progress
            self.active_jobs[job_id].progress = 30.0
            self.active_jobs[job_id].message = "Running scheduling algorithm"
            
            # 2. Run scheduling algorithm (to be implemented)
            schedule_generation_id, scheduling_results = await self._run_scheduling_algorithm(
                data, request, auth_headers
            )
            
            # Update progress
            self.active_jobs[job_id].progress = 80.0
            self.active_jobs[job_id].message = "Saving schedule to data service"
            
            # 3. Save results back to data service
            await self._save_scheduling_results(schedule_generation_id, scheduling_results, auth_headers)
            
            # Update job status
            self.active_jobs[job_id].status = SchedulingStatus.COMPLETED
            self.active_jobs[job_id].completed_at = datetime.now().isoformat()
            self.active_jobs[job_id].progress = 100.0
            self.active_jobs[job_id].message = "Scheduling completed successfully"
            
            # Add summary information
            self.active_jobs[job_id].schedule_generation_id = schedule_generation_id
            self.active_jobs[job_id].total_sessions = len(scheduling_results["sessions"])
            self.active_jobs[job_id].hard_constraint_violations = scheduling_results["metrics"]["hard_constraint_violations"]
            self.active_jobs[job_id].soft_constraint_violations = scheduling_results["metrics"]["soft_constraint_violations"]
            self.active_jobs[job_id].faculty_satisfaction_score = scheduling_results["metrics"]["faculty_satisfaction_score"]
            self.active_jobs[job_id].batch_satisfaction_score = scheduling_results["metrics"]["batch_satisfaction_score"]
            self.active_jobs[job_id].room_utilization = scheduling_results["metrics"]["room_utilization"]
            
        except Exception as e:
            logger.exception(f"Error processing scheduling job {job_id}: {str(e)}")
            # Update job status
            self.active_jobs[job_id].status = SchedulingStatus.FAILED
            self.active_jobs[job_id].completed_at = datetime.now().isoformat()
            self.active_jobs[job_id].message = "Scheduling failed"
            self.active_jobs[job_id].error = str(e)
    
    async def _fetch_scheduling_data(
        self, 
        request: SchedulingRequest,
        auth_headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Fetch all necessary data from the data service
        """
        try:
            async with httpx.AsyncClient(base_url=self.data_service_url, timeout=30.0) as client:
                # Fetch faculty data
                faculty_response = await client.get(
                    "/api/v1/faculty", 
                    headers=auth_headers,
                    params={"limit": 1000}
                )
                faculty_response.raise_for_status()
                faculty_data = faculty_response.json()["data"]
                
                # Fetch faculty preferences for each faculty
                for faculty in faculty_data:
                    try:
                        pref_response = await client.get(
                            f"/api/v1/faculty-preferences/{faculty['id']}/all-preferences",
                            headers=auth_headers
                        )
                        pref_response.raise_for_status()
                        faculty["preferences"] = pref_response.json()["data"]
                    except httpx.HTTPError as e:
                        logger.warning(f"Error fetching preferences for faculty {faculty['id']}: {str(e)}")
                        faculty["preferences"] = {
                            "availability": [],
                            "subject_expertise": [],
                            "batch_preferences": [],
                            "classroom_preferences": []
                        }
                
                # Fetch batches
                batches_response = await client.get(
                    "/api/v1/batches",
                    headers=auth_headers,
                    params={"limit": 1000}
                )
                batches_response.raise_for_status()
                batches_data = batches_response.json()["data"]
                
                # Fetch subjects
                subjects_response = await client.get(
                    "/api/v1/subjects",
                    headers=auth_headers,
                    params={"limit": 1000}
                )
                subjects_response.raise_for_status()
                subjects_data = subjects_response.json()["data"]
                
                # Fetch classrooms
                classrooms_response = await client.get(
                    "/api/v1/classrooms",
                    headers=auth_headers,
                    params={"limit": 1000}
                )
                classrooms_response.raise_for_status()
                classrooms_data = classrooms_response.json()["data"]
                
                # Fetch time slots
                time_slots_response = await client.get(
                    "/api/v1/time-slots",
                    headers=auth_headers,
                    params={"limit": 1000}
                )
                time_slots_response.raise_for_status()
                time_slots_data = time_slots_response.json()["data"]
                
                # Fetch scheduling constraints
                constraints_response = await client.get(
                    "/api/v1/scheduling-constraints",
                    headers=auth_headers,
                    params={"limit": 1000}
                )
                constraints_response.raise_for_status()
                constraints_data = constraints_response.json()["data"]
                
                # Fetch batch-subject assignments
                batch_subjects_response = await client.get(
                    "/api/v1/batch-subjects",
                    headers=auth_headers,
                    params={"limit": 1000}
                )
                batch_subjects_data = []
                if batch_subjects_response.status_code == 200:
                    batch_subjects_data = batch_subjects_response.json()["data"]
            
            return {
                "faculty": faculty_data,
                "batches": batches_data,
                "subjects": subjects_data,
                "classrooms": classrooms_data,
                "time_slots": time_slots_data,
                "constraints": constraints_data,
                "batch_subjects": batch_subjects_data
            }
        except httpx.HTTPError as e:
            raise DataServiceException(f"Error fetching data from data service: {str(e)}")
    
    async def _run_scheduling_algorithm(
        self,
        data: Dict[str, Any],
        request: SchedulingRequest,
        auth_headers: Dict[str, str]
    ) -> Tuple[UUID, Dict[str, Any]]:
        """
        Run the scheduling algorithm
        """
        # Generate a unique ID for this schedule generation
        schedule_generation_id = uuid4()
        
        # Import the algorithm factory
        from app.algorithms.factory import AlgorithmFactory
        
        # Determine which algorithm to use based on the request
        algorithm_type = request.algorithm_type if hasattr(request, "algorithm_type") else "csp"
        
        # Set algorithm parameters
        algorithm_params = {
            "max_time_in_seconds": 60,  # Default to 60 seconds
            "max_iterations": request.max_iterations if hasattr(request, "max_iterations") else 100,
        }
        
        # Add algorithm-specific parameters
        if algorithm_type == "genetic":
            algorithm_params.update({
                "population_size": 50,
                "generations": 100,
                "mutation_rate": 0.1,
                "elitism": 0.1,
                "tournament_size": 5,
                "time_limit_seconds": 60
            })
        elif algorithm_type == "csp":
            algorithm_params.update({
                "max_time_in_seconds": 60
            })
        
        # Create the algorithm instance
        algorithm = AlgorithmFactory.create(algorithm_type, data, algorithm_params)
        
        if not algorithm:
            raise SchedulingException(f"Invalid algorithm type: {algorithm_type}")
        
        try:
            # Run the algorithm
            logger.info(f"Running {algorithm_type} scheduling algorithm...")
            results = algorithm.run()
            
            # Check if the algorithm was successful
            if results["status"] != "success":
                logger.warning(f"Algorithm failed: {results.get('error', 'Unknown error')}")
                raise SchedulingException(f"Scheduling algorithm failed: {results.get('error', 'Unknown error')}")
            
            # Return the scheduling results
            scheduling_results = {
                "sessions": results["scheduled_sessions"],
                "metrics": results["metrics"]
            }
        except Exception as e:
            logger.exception(f"Error running scheduling algorithm: {str(e)}")
            raise SchedulingException(f"Error running scheduling algorithm: {str(e)}")
        
        return schedule_generation_id, scheduling_results
    
    async def _save_scheduling_results(
        self,
        schedule_generation_id: UUID,
        scheduling_results: Dict[str, Any],
        auth_headers: Dict[str, str]
    ):
        """
        Save scheduling results back to the data service
        """
        try:
            async with httpx.AsyncClient(base_url=self.data_service_url, timeout=30.0) as client:
                # 1. Create a schedule generation record
                schedule_gen_data = {
                    "id": str(schedule_generation_id),
                    "name": f"Schedule Generation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    "description": f"Generated by scheduler service on {datetime.now().isoformat()}",
                    "status": "COMPLETED",
                    "metrics": scheduling_results["metrics"]
                }
                
                schedule_gen_response = await client.post(
                    "/api/v1/schedule-generations",
                    json=schedule_gen_data,
                    headers=auth_headers
                )
                schedule_gen_response.raise_for_status()
                
                # 2. Create scheduled sessions in batches
                sessions = scheduling_results.get("sessions", [])
                batch_size = 50  # Process in batches of 50 to avoid overloading the API
                
                for i in range(0, len(sessions), batch_size):
                    batch = sessions[i:i+batch_size]
                    
                    # Add schedule generation ID to each session
                    for session in batch:
                        session["schedule_generation_id"] = str(schedule_generation_id)
                    
                    # Send the batch to the data service
                    sessions_response = await client.post(
                        "/api/v1/scheduled-sessions/batch-create",
                        json={"sessions": batch},
                        headers=auth_headers
                    )
                    sessions_response.raise_for_status()
                    
                    # Log progress
                    progress = min(100, (i + batch_size) / len(sessions) * 100)
                    logger.info(f"Saved {i + len(batch)} of {len(sessions)} sessions ({progress:.1f}%)")
                
                logger.info(f"Successfully saved {len(sessions)} scheduled sessions")
                
        except httpx.HTTPError as e:
            logger.exception(f"Error saving data to data service: {str(e)}")
            raise DataServiceException(f"Error saving data to data service: {str(e)}")

# Create a singleton instance
scheduler_service = SchedulerService(data_service_url="http://data-service:8000/api/v1")
