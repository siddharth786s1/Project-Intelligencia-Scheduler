"""
Constraint Satisfaction Programming algorithm implementation for scheduling.
Uses Google OR-Tools for solving the constraint satisfaction problem.
"""
import logging
from typing import Dict, Any, List, Set, Tuple
from uuid import UUID, uuid4

try:
    from ortools.sat.python import cp_model
except ImportError:
    logging.error("Google OR-Tools is not installed. Please install it with: pip install ortools")

from app.algorithms.base import BaseSchedulingAlgorithm

logger = logging.getLogger(__name__)


class CSPSchedulingAlgorithm(BaseSchedulingAlgorithm):
    """
    Scheduling algorithm using Constraint Satisfaction Programming (CSP).
    Uses Google OR-Tools CP-SAT solver to find a solution that satisfies all constraints.
    """
    
    def run(self) -> Dict[str, Any]:
        """
        Run the CSP scheduling algorithm.
        
        Returns:
            A dictionary containing the scheduling results and metrics.
        """
        logger.info("Starting CSP scheduling algorithm...")
        
        # Initialize the CP model
        model = cp_model.CpModel()
        
        # Create variables for the scheduling problem
        variables = self._create_variables(model)
        
        # Add hard constraints
        hard_constraints = self._add_hard_constraints(model, variables)
        
        # Add soft constraints (preferences)
        soft_constraints = self._add_soft_constraints(model, variables)
        
        # Set up the objective function
        self._set_objective(model, variables, soft_constraints)
        
        # Solve the model
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.parameters.get("max_time_in_seconds", 60)
        
        logger.info("Solving CSP model...")
        status = solver.Solve(model)
        
        # Process the solution
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            logger.info(f"Solution found with status: {status}")
            scheduled_sessions = self._extract_solution(solver, variables)
            metrics = self._calculate_metrics(solver, variables, scheduled_sessions, hard_constraints, soft_constraints)
            return {
                "scheduled_sessions": scheduled_sessions,
                "metrics": metrics,
                "status": "success"
            }
        else:
            logger.warning(f"No solution found. Status: {status}")
            return {
                "scheduled_sessions": [],
                "metrics": {
                    "hard_constraint_violations": len(self.constraints),
                    "soft_constraint_violations": 0,
                    "faculty_satisfaction_score": 0.0,
                    "batch_satisfaction_score": 0.0,
                    "room_utilization": 0.0
                },
                "status": "failed",
                "error": f"No solution found. Solver status: {status}"
            }
    
    def _create_variables(self, model: cp_model.CpModel) -> Dict[str, Any]:
        """
        Create variables for the CSP model.
        
        Args:
            model: The CP model
            
        Returns:
            A dictionary of variables needed for the scheduling problem
        """
        variables = {
            "assignments": {},  # (batch_id, subject_id, time_slot_id, faculty_id, classroom_id) -> bool var
            "faculty_assignments": {},  # (faculty_id, time_slot_id) -> bool var
            "classroom_assignments": {},  # (classroom_id, time_slot_id) -> bool var
            "batch_assignments": {},  # (batch_id, time_slot_id) -> bool var
        }
        
        # Create assignment variables
        for batch in self.batches:
            batch_id = batch["id"]
            
            for subject in self.subjects:
                subject_id = subject["id"]
                
                # Skip if this subject is not for this batch
                if not self._is_subject_for_batch(subject_id, batch_id):
                    continue
                
                for time_slot in self.time_slots:
                    time_slot_id = time_slot["id"]
                    
                    for faculty in self.faculty:
                        faculty_id = faculty["id"]
                        
                        # Skip if faculty doesn't have expertise in this subject
                        if not self._has_faculty_expertise(faculty_id, subject_id):
                            continue
                        
                        for classroom in self.classrooms:
                            classroom_id = classroom["id"]
                            
                            # Skip if classroom type doesn't match subject requirement
                            if not self._is_classroom_suitable(classroom_id, subject_id):
                                continue
                            
                            # Create a binary variable for this assignment
                            var_name = f"assign_b{batch_id}_s{subject_id}_t{time_slot_id}_f{faculty_id}_c{classroom_id}"
                            variables["assignments"][(batch_id, subject_id, time_slot_id, faculty_id, classroom_id)] = model.NewBoolVar(var_name)
        
        # Create convenience variables for faculty, classroom and batch assignments to time slots
        for faculty in self.faculty:
            faculty_id = faculty["id"]
            for time_slot in self.time_slots:
                time_slot_id = time_slot["id"]
                var_name = f"faculty_{faculty_id}_time_{time_slot_id}"
                variables["faculty_assignments"][(faculty_id, time_slot_id)] = model.NewBoolVar(var_name)
        
        for classroom in self.classrooms:
            classroom_id = classroom["id"]
            for time_slot in self.time_slots:
                time_slot_id = time_slot["id"]
                var_name = f"classroom_{classroom_id}_time_{time_slot_id}"
                variables["classroom_assignments"][(classroom_id, time_slot_id)] = model.NewBoolVar(var_name)
        
        for batch in self.batches:
            batch_id = batch["id"]
            for time_slot in self.time_slots:
                time_slot_id = time_slot["id"]
                var_name = f"batch_{batch_id}_time_{time_slot_id}"
                variables["batch_assignments"][(batch_id, time_slot_id)] = model.NewBoolVar(var_name)
        
        # Create constraints to link the convenience variables
        for faculty in self.faculty:
            faculty_id = faculty["id"]
            for time_slot in self.time_slots:
                time_slot_id = time_slot["id"]
                
                # Faculty is assigned to a time slot if they are teaching any batch/subject in that time slot
                assignment_vars = []
                for assignment_key, assignment_var in variables["assignments"].items():
                    batch_id, subject_id, ts_id, f_id, classroom_id = assignment_key
                    if f_id == faculty_id and ts_id == time_slot_id:
                        assignment_vars.append(assignment_var)
                
                if assignment_vars:
                    model.Add(variables["faculty_assignments"][(faculty_id, time_slot_id)] == sum(assignment_vars) >= 1)
        
        # Similar constraints for classrooms and batches
        for classroom in self.classrooms:
            classroom_id = classroom["id"]
            for time_slot in self.time_slots:
                time_slot_id = time_slot["id"]
                
                assignment_vars = []
                for assignment_key, assignment_var in variables["assignments"].items():
                    batch_id, subject_id, ts_id, faculty_id, c_id = assignment_key
                    if c_id == classroom_id and ts_id == time_slot_id:
                        assignment_vars.append(assignment_var)
                
                if assignment_vars:
                    model.Add(variables["classroom_assignments"][(classroom_id, time_slot_id)] == sum(assignment_vars) >= 1)
        
        for batch in self.batches:
            batch_id = batch["id"]
            for time_slot in self.time_slots:
                time_slot_id = time_slot["id"]
                
                assignment_vars = []
                for assignment_key, assignment_var in variables["assignments"].items():
                    b_id, subject_id, ts_id, faculty_id, classroom_id = assignment_key
                    if b_id == batch_id and ts_id == time_slot_id:
                        assignment_vars.append(assignment_var)
                
                if assignment_vars:
                    model.Add(variables["batch_assignments"][(batch_id, time_slot_id)] == sum(assignment_vars) >= 1)
        
        return variables
    
    def _add_hard_constraints(self, model: cp_model.CpModel, variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Add hard constraints to the model.
        
        Args:
            model: The CP model
            variables: The variables created for the model
            
        Returns:
            A list of hard constraint descriptors for later reference
        """
        hard_constraints = []
        
        # 1. Faculty can only teach one class at a time
        for faculty in self.faculty:
            faculty_id = faculty["id"]
            for time_slot in self.time_slots:
                time_slot_id = time_slot["id"]
                
                assignments = []
                for key, var in variables["assignments"].items():
                    batch_id, subject_id, ts_id, f_id, classroom_id = key
                    if f_id == faculty_id and ts_id == time_slot_id:
                        assignments.append(var)
                
                if assignments:
                    constraint = {
                        "type": "faculty_one_class_at_a_time",
                        "faculty_id": faculty_id,
                        "time_slot_id": time_slot_id
                    }
                    hard_constraints.append(constraint)
                    model.Add(sum(assignments) <= 1)
        
        # 2. Classroom can only have one class at a time
        for classroom in self.classrooms:
            classroom_id = classroom["id"]
            for time_slot in self.time_slots:
                time_slot_id = time_slot["id"]
                
                assignments = []
                for key, var in variables["assignments"].items():
                    batch_id, subject_id, ts_id, f_id, c_id = key
                    if c_id == classroom_id and ts_id == time_slot_id:
                        assignments.append(var)
                
                if assignments:
                    constraint = {
                        "type": "classroom_one_class_at_a_time",
                        "classroom_id": classroom_id,
                        "time_slot_id": time_slot_id
                    }
                    hard_constraints.append(constraint)
                    model.Add(sum(assignments) <= 1)
        
        # 3. Batch can only have one class at a time
        for batch in self.batches:
            batch_id = batch["id"]
            for time_slot in self.time_slots:
                time_slot_id = time_slot["id"]
                
                assignments = []
                for key, var in variables["assignments"].items():
                    b_id, subject_id, ts_id, faculty_id, classroom_id = key
                    if b_id == batch_id and ts_id == time_slot_id:
                        assignments.append(var)
                
                if assignments:
                    constraint = {
                        "type": "batch_one_class_at_a_time",
                        "batch_id": batch_id,
                        "time_slot_id": time_slot_id
                    }
                    hard_constraints.append(constraint)
                    model.Add(sum(assignments) <= 1)
        
        # 4. Faculty must be available during the assigned time slot
        for faculty in self.faculty:
            faculty_id = faculty["id"]
            for time_slot in self.time_slots:
                time_slot_id = time_slot["id"]
                
                # Skip if we can't check availability
                if faculty_id not in self.faculty_preferences:
                    continue
                
                availability = self.faculty_preferences[faculty_id]["availability"]
                day = self.time_slot_by_id[time_slot_id].get("day_of_week")
                slot_type = self.time_slot_by_id[time_slot_id].get("slot_type")
                
                # If faculty is not available, they can't be assigned
                if day in availability and slot_type in availability[day]:
                    is_available = availability[day][slot_type]
                    if not is_available:
                        for key, var in variables["assignments"].items():
                            batch_id, subject_id, ts_id, f_id, classroom_id = key
                            if f_id == faculty_id and ts_id == time_slot_id:
                                constraint = {
                                    "type": "faculty_availability",
                                    "faculty_id": faculty_id,
                                    "time_slot_id": time_slot_id
                                }
                                hard_constraints.append(constraint)
                                model.Add(var == 0)
        
        # 5. All required subjects must be scheduled for each batch
        for batch in self.batches:
            batch_id = batch["id"]
            required_subjects = self._get_required_subjects_for_batch(batch_id)
            
            for subject_id in required_subjects:
                assignments = []
                for key, var in variables["assignments"].items():
                    b_id, s_id, time_slot_id, faculty_id, classroom_id = key
                    if b_id == batch_id and s_id == subject_id:
                        assignments.append(var)
                
                if assignments:
                    constraint = {
                        "type": "batch_subject_requirement",
                        "batch_id": batch_id,
                        "subject_id": subject_id
                    }
                    hard_constraints.append(constraint)
                    model.Add(sum(assignments) >= 1)
        
        return hard_constraints
    
    def _add_soft_constraints(self, model: cp_model.CpModel, variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Add soft constraints (preferences) to the model.
        
        Args:
            model: The CP model
            variables: The variables created for the model
            
        Returns:
            A list of soft constraint descriptors for later reference
        """
        soft_constraints = []
        
        # 1. Faculty subject expertise preference
        for faculty in self.faculty:
            faculty_id = faculty["id"]
            if faculty_id not in self.faculty_preferences:
                continue
                
            subject_expertise = self.faculty_preferences[faculty_id]["subject_expertise"]
            
            for subject_id, expertise_level in subject_expertise.items():
                # Find all assignments for this faculty and subject
                for key, var in variables["assignments"].items():
                    batch_id, s_id, time_slot_id, f_id, classroom_id = key
                    if f_id == faculty_id and s_id == subject_id:
                        constraint = {
                            "type": "faculty_subject_expertise",
                            "faculty_id": faculty_id,
                            "subject_id": subject_id,
                            "weight": expertise_level,
                            "variable": var
                        }
                        soft_constraints.append(constraint)
        
        # 2. Faculty batch preference
        for faculty in self.faculty:
            faculty_id = faculty["id"]
            if faculty_id not in self.faculty_preferences:
                continue
                
            batch_preferences = self.faculty_preferences[faculty_id]["batch_preferences"]
            
            for batch_id, preference_level in batch_preferences.items():
                # Find all assignments for this faculty and batch
                for key, var in variables["assignments"].items():
                    b_id, subject_id, time_slot_id, f_id, classroom_id = key
                    if f_id == faculty_id and b_id == batch_id:
                        constraint = {
                            "type": "faculty_batch_preference",
                            "faculty_id": faculty_id,
                            "batch_id": batch_id,
                            "weight": preference_level,
                            "variable": var
                        }
                        soft_constraints.append(constraint)
        
        # 3. Faculty classroom preference
        for faculty in self.faculty:
            faculty_id = faculty["id"]
            if faculty_id not in self.faculty_preferences:
                continue
                
            classroom_preferences = self.faculty_preferences[faculty_id]["classroom_preferences"]
            
            for classroom_id, preference_level in classroom_preferences.items():
                # Find all assignments for this faculty and classroom
                for key, var in variables["assignments"].items():
                    batch_id, subject_id, time_slot_id, f_id, c_id = key
                    if f_id == faculty_id and c_id == classroom_id:
                        constraint = {
                            "type": "faculty_classroom_preference",
                            "faculty_id": faculty_id,
                            "classroom_id": classroom_id,
                            "weight": preference_level,
                            "variable": var
                        }
                        soft_constraints.append(constraint)
        
        return soft_constraints
    
    def _set_objective(self, model: cp_model.CpModel, variables: Dict[str, Any], soft_constraints: List[Dict[str, Any]]):
        """
        Set up the objective function to maximize preference satisfaction.
        
        Args:
            model: The CP model
            variables: The variables created for the model
            soft_constraints: List of soft constraint descriptors
        """
        objective_terms = []
        
        # Add soft constraint terms to the objective
        for constraint in soft_constraints:
            weight = constraint["weight"]
            var = constraint["variable"]
            
            # Scale the weight appropriately (multiply by variable)
            objective_terms.append(weight * var)
        
        # Set the objective to maximize the sum of preference weights
        if objective_terms:
            model.Maximize(sum(objective_terms))
    
    def _extract_solution(self, solver: cp_model.CpSolver, variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract the solution from the solver.
        
        Args:
            solver: The CP solver with a solution
            variables: The variables created for the model
            
        Returns:
            A list of scheduled sessions
        """
        scheduled_sessions = []
        
        for key, var in variables["assignments"].items():
            if solver.Value(var) == 1:
                batch_id, subject_id, time_slot_id, faculty_id, classroom_id = key
                
                # Create a scheduled session
                session = {
                    "id": str(uuid4()),
                    "batch_id": str(batch_id),
                    "subject_id": str(subject_id),
                    "time_slot_id": str(time_slot_id),
                    "faculty_id": str(faculty_id),
                    "classroom_id": str(classroom_id),
                    "status": "SCHEDULED",
                    "day_of_week": self.time_slot_by_id[time_slot_id].get("day_of_week"),
                    "start_time": self.time_slot_by_id[time_slot_id].get("start_time"),
                    "end_time": self.time_slot_by_id[time_slot_id].get("end_time"),
                    "batch_name": self.batch_by_id[batch_id].get("name"),
                    "subject_name": self.subject_by_id[subject_id].get("name"),
                    "faculty_name": self.faculty_by_id[faculty_id].get("name"),
                    "classroom_name": self.classroom_by_id[classroom_id].get("name"),
                }
                
                scheduled_sessions.append(session)
        
        return scheduled_sessions
    
    def _calculate_metrics(
        self, 
        solver: cp_model.CpSolver, 
        variables: Dict[str, Any],
        scheduled_sessions: List[Dict[str, Any]],
        hard_constraints: List[Dict[str, Any]],
        soft_constraints: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate metrics for the schedule.
        
        Args:
            solver: The CP solver with a solution
            variables: The variables created for the model
            scheduled_sessions: The extracted scheduled sessions
            hard_constraints: List of hard constraint descriptors
            soft_constraints: List of soft constraint descriptors
            
        Returns:
            A dictionary of metrics about the schedule quality
        """
        # Count hard constraint violations (should be 0 for a feasible solution)
        hard_violations = 0
        
        # Count soft constraint violations and calculate satisfaction scores
        soft_violations = 0
        total_soft_constraints = len(soft_constraints)
        satisfied_soft_constraints = 0
        
        faculty_satisfaction_scores = {}
        batch_satisfaction_scores = {}
        
        for constraint in soft_constraints:
            var = constraint["variable"]
            weight = constraint["weight"]
            constraint_type = constraint["type"]
            
            # Check if the constraint is satisfied (variable is 1)
            if solver.Value(var) == 1:
                satisfied_soft_constraints += 1
                
                # Update faculty satisfaction
                if constraint_type == "faculty_subject_expertise":
                    faculty_id = constraint["faculty_id"]
                    if faculty_id not in faculty_satisfaction_scores:
                        faculty_satisfaction_scores[faculty_id] = []
                    faculty_satisfaction_scores[faculty_id].append(weight)
                
                elif constraint_type == "faculty_batch_preference":
                    faculty_id = constraint["faculty_id"]
                    if faculty_id not in faculty_satisfaction_scores:
                        faculty_satisfaction_scores[faculty_id] = []
                    faculty_satisfaction_scores[faculty_id].append(weight)
                    
                    batch_id = constraint["batch_id"]
                    if batch_id not in batch_satisfaction_scores:
                        batch_satisfaction_scores[batch_id] = []
                    batch_satisfaction_scores[batch_id].append(weight)
                
                elif constraint_type == "faculty_classroom_preference":
                    faculty_id = constraint["faculty_id"]
                    if faculty_id not in faculty_satisfaction_scores:
                        faculty_satisfaction_scores[faculty_id] = []
                    faculty_satisfaction_scores[faculty_id].append(weight)
            else:
                soft_violations += 1
        
        # Calculate average faculty and batch satisfaction scores
        faculty_satisfaction = 0.0
        if faculty_satisfaction_scores:
            faculty_scores = []
            for faculty_id, scores in faculty_satisfaction_scores.items():
                faculty_scores.append(sum(scores) / len(scores))
            faculty_satisfaction = (sum(faculty_scores) / len(faculty_scores) + 2) * 20  # Scale to 0-100
        
        batch_satisfaction = 0.0
        if batch_satisfaction_scores:
            batch_scores = []
            for batch_id, scores in batch_satisfaction_scores.items():
                batch_scores.append(sum(scores) / len(scores))
            batch_satisfaction = (sum(batch_scores) / len(batch_scores) + 2) * 20  # Scale to 0-100
        
        # Calculate room utilization
        total_slots = len(self.time_slots) * len(self.classrooms)
        used_slots = len({(session["classroom_id"], session["time_slot_id"]) for session in scheduled_sessions})
        room_utilization = (used_slots / total_slots) * 100 if total_slots > 0 else 0.0
        
        return {
            "hard_constraint_violations": hard_violations,
            "soft_constraint_violations": soft_violations,
            "faculty_satisfaction_score": faculty_satisfaction,
            "batch_satisfaction_score": batch_satisfaction,
            "room_utilization": room_utilization,
            "total_sessions": len(scheduled_sessions),
            "total_faculty_used": len({session["faculty_id"] for session in scheduled_sessions}),
            "total_classrooms_used": len({session["classroom_id"] for session in scheduled_sessions})
        }
    
    # Helper methods
    def _is_subject_for_batch(self, subject_id: UUID, batch_id: UUID) -> bool:
        """Check if a subject is required for a batch."""
        # In a real implementation, this would check the subject-batch association
        # For now, we'll assume all subjects can be assigned to all batches
        return True
    
    def _has_faculty_expertise(self, faculty_id: UUID, subject_id: UUID) -> bool:
        """Check if a faculty has expertise in a subject."""
        if faculty_id not in self.faculty_preferences:
            return True  # Assume faculty can teach any subject if we don't have preference data
            
        subject_expertise = self.faculty_preferences[faculty_id]["subject_expertise"]
        return subject_id in subject_expertise
    
    def _is_classroom_suitable(self, classroom_id: UUID, subject_id: UUID) -> bool:
        """Check if a classroom is suitable for a subject."""
        # In a real implementation, this would check classroom type against subject requirements
        # For now, we'll assume all classrooms can be used for all subjects
        return True
    
    def _get_required_subjects_for_batch(self, batch_id: UUID) -> Set[UUID]:
        """Get the set of subjects required for a batch."""
        # In a real implementation, this would fetch the required subjects for the batch
        # For now, we'll return all subjects
        return {subject["id"] for subject in self.subjects}
