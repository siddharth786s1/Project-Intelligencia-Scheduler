from typing import Dict, List, Any, Tuple, Optional
from uuid import UUID, uuid4
import logging
from datetime import datetime, time

from ortools.sat.python import cp_model
import numpy as np

from app.services.algorithms.base import SchedulingAlgorithm, ConstraintType
from app.core.errors import SchedulingException, ConstraintViolationException

logger = logging.getLogger(__name__)


class CSPScheduler(SchedulingAlgorithm):
    """
    Constraint Satisfaction Problem (CSP) scheduler implementation
    using Google OR-Tools CP-SAT solver
    """
    
    def __init__(self, data: Dict[str, Any], params: Dict[str, Any]):
        super().__init__(data, params)
        
        # Initialize indices for entities
        self.faculty_indices = {f["id"]: i for i, f in enumerate(self.faculty)}
        self.batch_indices = {b["id"]: i for i, b in enumerate(self.batches)}
        self.classroom_indices = {c["id"]: i for i, c in enumerate(self.classrooms)}
        self.subject_indices = {s["id"]: i for i, s in enumerate(self.subjects)}
        self.time_slot_indices = {t["id"]: i for i, t in enumerate(self.time_slots)}
        
        # Get counts
        self.num_faculty = len(self.faculty)
        self.num_batches = len(self.batches)
        self.num_classrooms = len(self.classrooms)
        self.num_subjects = len(self.subjects)
        self.num_time_slots = len(self.time_slots)
        
        # Track assignments
        self.batch_subject_assignments = self._get_batch_subject_assignments()
        self.faculty_subject_assignments = self._get_faculty_subject_assignments()
        
        # Model and variables
        self.model = None
        self.variables = {}
        self.assignments = []
        
    def _get_batch_subject_assignments(self) -> List[Tuple[int, int]]:
        """
        Get all batch-subject pairs that need to be scheduled
        """
        assignments = []
        for batch in self.batches:
            for subject_id in batch.get("subjects", []):
                if subject_id in self.subject_indices:
                    assignments.append(
                        (self.batch_indices[batch["id"]], self.subject_indices[subject_id])
                    )
        return assignments
    
    def _get_faculty_subject_assignments(self) -> List[Tuple[int, int]]:
        """
        Get all faculty-subject pairs based on expertise
        """
        assignments = []
        for faculty in self.faculty:
            for subject_id in faculty.get("subject_expertise", []):
                if subject_id in self.subject_indices:
                    assignments.append(
                        (self.faculty_indices[faculty["id"]], self.subject_indices[subject_id])
                    )
        return assignments
        
    def run(self) -> Dict[str, Any]:
        """
        Run the CSP scheduling algorithm
        """
        logger.info("Running CSP scheduler")
        
        # Create the model
        self.model = cp_model.CpModel()
        
        # Create variables
        self._create_variables()
        
        # Add constraints
        self._add_hard_constraints()
        self._add_soft_constraints()
        
        # Create a solver and solve the model
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.params.get("timeout_seconds", 300)
        
        logger.info("Solving the model...")
        status = solver.Solve(self.model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            logger.info(f"Solution found with status: {status}")
            return self._build_solution(solver)
        else:
            logger.error(f"No solution found, status: {status}")
            raise SchedulingException("Failed to find a feasible schedule")
    
    def _create_variables(self):
        """
        Create decision variables for the CSP model
        """
        # Main decision variable: is a session scheduled for
        # faculty f, batch b, subject s, classroom c, time slot t?
        for f in range(self.num_faculty):
            for b, s in self.batch_subject_assignments:
                # Check if faculty can teach this subject
                if (f, s) not in self.faculty_subject_assignments:
                    continue
                    
                for c in range(self.num_classrooms):
                    for t in range(self.num_time_slots):
                        var_name = f"session_f{f}_b{b}_s{s}_c{c}_t{t}"
                        self.variables[var_name] = self.model.NewBoolVar(var_name)
    
    def _add_hard_constraints(self):
        """
        Add hard constraints to the model
        """
        # Hard constraint 1: Faculty can only teach one session at a time
        self._add_faculty_time_conflict_constraint()
        
        # Hard constraint 2: Batch can only attend one session at a time
        self._add_batch_time_conflict_constraint()
        
        # Hard constraint 3: Classroom can only host one session at a time
        self._add_classroom_time_conflict_constraint()
        
        # Hard constraint 4: Each batch-subject pair must be scheduled
        self._add_batch_subject_assignment_constraint()
        
        # Hard constraint 5: Respect faculty availability
        self._add_faculty_availability_constraint()
        
        # Hard constraint 6: Respect classroom capacity
        self._add_classroom_capacity_constraint()
    
    def _add_faculty_time_conflict_constraint(self):
        """
        Faculty can only teach one session at a time
        """
        for f in range(self.num_faculty):
            for t in range(self.num_time_slots):
                # Get all session variables for this faculty at this time
                session_vars = []
                for b, s in self.batch_subject_assignments:
                    if (f, s) not in self.faculty_subject_assignments:
                        continue
                        
                    for c in range(self.num_classrooms):
                        var_name = f"session_f{f}_b{b}_s{s}_c{c}_t{t}"
                        if var_name in self.variables:
                            session_vars.append(self.variables[var_name])
                
                # Faculty can teach at most one session at this time
                if session_vars:
                    self.model.Add(sum(session_vars) <= 1)
    
    def _add_batch_time_conflict_constraint(self):
        """
        Batch can only attend one session at a time
        """
        for b in range(self.num_batches):
            for t in range(self.num_time_slots):
                # Get all session variables for this batch at this time
                session_vars = []
                for s in range(self.num_subjects):
                    if (b, s) not in self.batch_subject_assignments:
                        continue
                        
                    for f in range(self.num_faculty):
                        if (f, s) not in self.faculty_subject_assignments:
                            continue
                            
                        for c in range(self.num_classrooms):
                            var_name = f"session_f{f}_b{b}_s{s}_c{c}_t{t}"
                            if var_name in self.variables:
                                session_vars.append(self.variables[var_name])
                
                # Batch can attend at most one session at this time
                if session_vars:
                    self.model.Add(sum(session_vars) <= 1)
    
    def _add_classroom_time_conflict_constraint(self):
        """
        Classroom can only host one session at a time
        """
        for c in range(self.num_classrooms):
            for t in range(self.num_time_slots):
                # Get all session variables for this classroom at this time
                session_vars = []
                for f in range(self.num_faculty):
                    for b, s in self.batch_subject_assignments:
                        if (f, s) not in self.faculty_subject_assignments:
                            continue
                            
                        var_name = f"session_f{f}_b{b}_s{s}_c{c}_t{t}"
                        if var_name in self.variables:
                            session_vars.append(self.variables[var_name])
                
                # Classroom can host at most one session at this time
                if session_vars:
                    self.model.Add(sum(session_vars) <= 1)
    
    def _add_batch_subject_assignment_constraint(self):
        """
        Each batch-subject pair must be scheduled
        """
        for b, s in self.batch_subject_assignments:
            # Get all session variables for this batch-subject pair
            session_vars = []
            for f in range(self.num_faculty):
                if (f, s) not in self.faculty_subject_assignments:
                    continue
                    
                for c in range(self.num_classrooms):
                    for t in range(self.num_time_slots):
                        var_name = f"session_f{f}_b{b}_s{s}_c{c}_t{t}"
                        if var_name in self.variables:
                            session_vars.append(self.variables[var_name])
            
            # Each batch-subject pair must be scheduled at least once
            if session_vars:
                self.model.Add(sum(session_vars) >= 1)
    
    def _add_faculty_availability_constraint(self):
        """
        Respect faculty availability
        """
        # Faculty availability is encoded as a list of available time slots
        for f_idx, faculty in enumerate(self.faculty):
            unavailable_slots = faculty.get("unavailable_time_slots", [])
            
            for time_slot_id in unavailable_slots:
                if time_slot_id in self.time_slot_indices:
                    t = self.time_slot_indices[time_slot_id]
                    
                    # Faculty cannot teach in this time slot
                    for b, s in self.batch_subject_assignments:
                        if (f_idx, s) not in self.faculty_subject_assignments:
                            continue
                            
                        for c in range(self.num_classrooms):
                            var_name = f"session_f{f_idx}_b{b}_s{s}_c{c}_t{t}"
                            if var_name in self.variables:
                                self.model.Add(self.variables[var_name] == 0)
    
    def _add_classroom_capacity_constraint(self):
        """
        Ensure classroom has enough capacity for batch
        """
        for b_idx, batch in enumerate(self.batches):
            batch_size = batch.get("size", 0)
            
            for c_idx, classroom in enumerate(self.classrooms):
                classroom_capacity = classroom.get("capacity", 0)
                
                # Skip if classroom is too small
                if batch_size > classroom_capacity:
                    for s in range(self.num_subjects):
                        if (b_idx, s) not in self.batch_subject_assignments:
                            continue
                            
                        for f in range(self.num_faculty):
                            if (f, s) not in self.faculty_subject_assignments:
                                continue
                                
                            for t in range(self.num_time_slots):
                                var_name = f"session_f{f}_b{b_idx}_s{s}_c{c_idx}_t{t}"
                                if var_name in self.variables:
                                    self.model.Add(self.variables[var_name] == 0)
    
    def _add_soft_constraints(self):
        """
        Add soft constraints to the model as objective terms
        """
        # This is just a placeholder for now
        # In a real implementation, we would add soft constraints
        # with appropriate weights for optimization
        pass
    
    def _build_solution(self, solver) -> Dict[str, Any]:
        """
        Build the solution from the solver results
        """
        scheduled_sessions = []
        
        # Extract scheduled sessions from the solution
        for var_name, var in self.variables.items():
            if solver.Value(var) == 1:
                # Parse the variable name to get indices
                # Format: session_f{f}_b{b}_s{s}_c{c}_t{t}
                parts = var_name.split('_')
                f_idx = int(parts[1][1:])
                b_idx = int(parts[2][1:])
                s_idx = int(parts[3][1:])
                c_idx = int(parts[4][1:])
                t_idx = int(parts[5][1:])
                
                # Get the original entity IDs
                faculty_id = next(id for id, i in self.faculty_indices.items() if i == f_idx)
                batch_id = next(id for id, i in self.batch_indices.items() if i == b_idx)
                subject_id = next(id for id, i in self.subject_indices.items() if i == s_idx)
                classroom_id = next(id for id, i in self.classroom_indices.items() if i == c_idx)
                time_slot_id = next(id for id, i in self.time_slot_indices.items() if i == t_idx)
                
                # Get names for better readability
                faculty_name = next(f for f in self.faculty if f["id"] == faculty_id)["name"]
                batch_name = next(b for b in self.batches if b["id"] == batch_id)["name"]
                subject_name = next(s for s in self.subjects if s["id"] == subject_id)["name"]
                classroom_name = next(c for c in self.classrooms if c["id"] == classroom_id)["name"]
                
                # Create session
                session = {
                    "id": str(uuid4()),
                    "faculty_id": faculty_id,
                    "faculty_name": faculty_name,
                    "batch_id": batch_id,
                    "batch_name": batch_name,
                    "subject_id": subject_id,
                    "subject_name": subject_name,
                    "classroom_id": classroom_id,
                    "classroom_name": classroom_name,
                    "time_slot_id": time_slot_id,
                    "is_canceled": False
                }
                
                scheduled_sessions.append(session)
        
        # Calculate metrics
        metrics = self._calculate_metrics(scheduled_sessions)
        
        return {
            "sessions": scheduled_sessions,
            "metrics": metrics
        }
    
    def _calculate_metrics(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate metrics for the generated schedule
        """
        # Placeholder implementation
        # In a real implementation, we would calculate metrics based on:
        # - Hard constraint violations (should be 0 for a valid solution)
        # - Soft constraint violations
        # - Faculty satisfaction
        # - Batch satisfaction
        # - Classroom utilization
        
        return {
            "hard_constraint_violations": 0,
            "soft_constraint_violations": len(self.constraints) // 2,  # Placeholder
            "faculty_satisfaction_score": 85.5,  # Placeholder
            "batch_satisfaction_score": 90.2,  # Placeholder
            "room_utilization": 78.4  # Placeholder
        }
