"""
Genetic Algorithm implementation for scheduling.
Uses evolutionary principles to find an optimal or near-optimal solution.
"""
import logging
import random
from typing import Dict, Any, List, Tuple, Set
from uuid import UUID, uuid4
import time

from app.algorithms.base import BaseSchedulingAlgorithm

logger = logging.getLogger(__name__)


class GeneticSchedulingAlgorithm(BaseSchedulingAlgorithm):
    """
    Scheduling algorithm using Genetic Algorithm (GA).
    Uses evolutionary principles to find an optimal or near-optimal solution.
    """
    
    def run(self) -> Dict[str, Any]:
        """
        Run the genetic algorithm for scheduling.
        
        Returns:
            A dictionary containing the scheduling results and metrics.
        """
        logger.info("Starting Genetic Algorithm scheduling...")
        
        # Set algorithm parameters
        population_size = self.parameters.get("population_size", 50)
        generations = self.parameters.get("generations", 100)
        mutation_rate = self.parameters.get("mutation_rate", 0.1)
        elitism = self.parameters.get("elitism", 0.1)  # Percentage of best solutions to keep
        tournament_size = self.parameters.get("tournament_size", 5)
        time_limit_seconds = self.parameters.get("time_limit_seconds", 60)
        
        # Initialize population
        logger.info("Initializing population...")
        population = self._initialize_population(population_size)
        
        # Evaluate initial population
        population = [(individual, self._fitness(individual)) for individual in population]
        population.sort(key=lambda x: x[1], reverse=True)
        
        best_solution = population[0][0]
        best_fitness = population[0][1]
        
        # Run evolution
        start_time = time.time()
        current_generation = 0
        
        logger.info(f"Starting evolution for {generations} generations or {time_limit_seconds} seconds...")
        
        while current_generation < generations and (time.time() - start_time) < time_limit_seconds:
            # Create next generation
            next_generation = []
            
            # Elitism: keep best individuals
            elite_count = int(elitism * population_size)
            next_generation.extend([individual for individual, _ in population[:elite_count]])
            
            # Create rest of population through selection, crossover and mutation
            while len(next_generation) < population_size:
                parent1 = self._tournament_selection(population, tournament_size)
                parent2 = self._tournament_selection(population, tournament_size)
                
                child = self._crossover(parent1, parent2)
                child = self._mutate(child, mutation_rate)
                
                # Validate and repair child if necessary
                child = self._repair(child)
                
                next_generation.append(child)
            
            # Evaluate new population
            population = [(individual, self._fitness(individual)) for individual in next_generation]
            population.sort(key=lambda x: x[1], reverse=True)
            
            # Update best solution if we have a new best
            if population[0][1] > best_fitness:
                best_solution = population[0][0]
                best_fitness = population[0][1]
                logger.info(f"New best solution found at generation {current_generation} with fitness {best_fitness}")
            
            current_generation += 1
            
            if current_generation % 10 == 0:
                logger.info(f"Generation {current_generation}: Best fitness = {best_fitness}")
        
        logger.info(f"Genetic algorithm completed after {current_generation} generations")
        logger.info(f"Best fitness: {best_fitness}")
        
        # Convert best solution to scheduled sessions
        scheduled_sessions = self._solution_to_sessions(best_solution)
        
        # Calculate metrics
        metrics = self._solution_metrics(best_solution, scheduled_sessions)
        
        return {
            "scheduled_sessions": scheduled_sessions,
            "metrics": metrics,
            "status": "success"
        }
    
    def _initialize_population(self, population_size: int) -> List[List[Dict[str, Any]]]:
        """
        Initialize a random population of scheduling solutions.
        
        Args:
            population_size: Size of the population to generate
            
        Returns:
            A list of scheduling solutions, where each solution is a list of session assignments
        """
        population = []
        
        # Generate population_size random solutions
        for _ in range(population_size):
            solution = []
            
            # Create assignments for each batch-subject pair
            for batch in self.batches:
                batch_id = batch["id"]
                required_subjects = self._get_required_subjects_for_batch(batch_id)
                
                for subject_id in required_subjects:
                    # Find suitable faculty members for this subject
                    suitable_faculty = [
                        faculty["id"] for faculty in self.faculty
                        if self._has_faculty_expertise(faculty["id"], subject_id)
                    ]
                    
                    if not suitable_faculty:
                        continue  # Skip if no suitable faculty
                    
                    # Find suitable classrooms for this subject
                    suitable_classrooms = [
                        classroom["id"] for classroom in self.classrooms
                        if self._is_classroom_suitable(classroom["id"], subject_id)
                    ]
                    
                    if not suitable_classrooms:
                        continue  # Skip if no suitable classrooms
                    
                    # Randomly assign time slot, faculty and classroom
                    time_slot_id = random.choice([ts["id"] for ts in self.time_slots])
                    faculty_id = random.choice(suitable_faculty)
                    classroom_id = random.choice(suitable_classrooms)
                    
                    # Create session assignment
                    session = {
                        "batch_id": batch_id,
                        "subject_id": subject_id,
                        "time_slot_id": time_slot_id,
                        "faculty_id": faculty_id,
                        "classroom_id": classroom_id
                    }
                    
                    solution.append(session)
            
            population.append(solution)
        
        return population
    
    def _fitness(self, solution: List[Dict[str, Any]]) -> float:
        """
        Calculate the fitness of a solution.
        
        Args:
            solution: A scheduling solution (list of session assignments)
            
        Returns:
            A fitness score, higher is better
        """
        # Calculate hard constraint violations
        hard_violations = self._count_hard_violations(solution)
        
        # If any hard constraints are violated, return a very low fitness
        if hard_violations > 0:
            return -1000 * hard_violations
        
        # Calculate soft constraint satisfaction
        faculty_satisfaction = self._calculate_faculty_satisfaction(solution)
        batch_satisfaction = self._calculate_batch_satisfaction(solution)
        room_utilization = self._calculate_room_utilization(solution)
        
        # Combine into overall fitness (weighted sum)
        fitness = (
            0.4 * faculty_satisfaction +
            0.4 * batch_satisfaction +
            0.2 * room_utilization
        )
        
        return fitness
    
    def _count_hard_violations(self, solution: List[Dict[str, Any]]) -> int:
        """
        Count the number of hard constraint violations in a solution.
        
        Args:
            solution: A scheduling solution (list of session assignments)
            
        Returns:
            Number of hard constraint violations
        """
        violations = 0
        
        # Track assignments to detect conflicts
        faculty_assignments = {}  # (faculty_id, time_slot_id) -> count
        classroom_assignments = {}  # (classroom_id, time_slot_id) -> count
        batch_assignments = {}  # (batch_id, time_slot_id) -> count
        
        # Track which batch-subject pairs are scheduled
        scheduled_batch_subjects = {}  # (batch_id, subject_id) -> count
        
        for session in solution:
            batch_id = session["batch_id"]
            subject_id = session["subject_id"]
            time_slot_id = session["time_slot_id"]
            faculty_id = session["faculty_id"]
            classroom_id = session["classroom_id"]
            
            # Check faculty availability
            if not self._is_faculty_available(faculty_id, time_slot_id):
                violations += 1
            
            # Track assignments for conflict detection
            faculty_key = (faculty_id, time_slot_id)
            classroom_key = (classroom_id, time_slot_id)
            batch_key = (batch_id, time_slot_id)
            batch_subject_key = (batch_id, subject_id)
            
            faculty_assignments[faculty_key] = faculty_assignments.get(faculty_key, 0) + 1
            classroom_assignments[classroom_key] = classroom_assignments.get(classroom_key, 0) + 1
            batch_assignments[batch_key] = batch_assignments.get(batch_key, 0) + 1
            scheduled_batch_subjects[batch_subject_key] = scheduled_batch_subjects.get(batch_subject_key, 0) + 1
            
            # Check faculty expertise
            if not self._has_faculty_expertise(faculty_id, subject_id):
                violations += 1
            
            # Check classroom suitability
            if not self._is_classroom_suitable(classroom_id, subject_id):
                violations += 1
        
        # Count violations for multiple assignments
        for key, count in faculty_assignments.items():
            if count > 1:
                violations += (count - 1)
                
        for key, count in classroom_assignments.items():
            if count > 1:
                violations += (count - 1)
                
        for key, count in batch_assignments.items():
            if count > 1:
                violations += (count - 1)
        
        # Check if all required batch-subject pairs are scheduled
        for batch in self.batches:
            batch_id = batch["id"]
            required_subjects = self._get_required_subjects_for_batch(batch_id)
            
            for subject_id in required_subjects:
                batch_subject_key = (batch_id, subject_id)
                if batch_subject_key not in scheduled_batch_subjects:
                    violations += 1
        
        return violations
    
    def _calculate_faculty_satisfaction(self, solution: List[Dict[str, Any]]) -> float:
        """
        Calculate faculty satisfaction score based on preferences.
        
        Args:
            solution: A scheduling solution (list of session assignments)
            
        Returns:
            Faculty satisfaction score (0-100)
        """
        if not solution:
            return 0.0
            
        faculty_scores = {}
        
        for session in solution:
            faculty_id = session["faculty_id"]
            subject_id = session["subject_id"]
            batch_id = session["batch_id"]
            classroom_id = session["classroom_id"]
            
            # Skip if we don't have preference data for this faculty
            if faculty_id not in self.faculty_preferences:
                continue
                
            preferences = self.faculty_preferences[faculty_id]
            
            # Initialize score for this faculty if not already done
            if faculty_id not in faculty_scores:
                faculty_scores[faculty_id] = []
            
            # Add subject expertise score (1-5)
            if subject_id in preferences["subject_expertise"]:
                expertise_level = preferences["subject_expertise"][subject_id]
                faculty_scores[faculty_id].append(expertise_level)
            
            # Add batch preference score (-2 to +2)
            if batch_id in preferences["batch_preferences"]:
                batch_preference = preferences["batch_preferences"][batch_id]
                faculty_scores[faculty_id].append(batch_preference)
            
            # Add classroom preference score (-2 to +2)
            if classroom_id in preferences["classroom_preferences"]:
                classroom_preference = preferences["classroom_preferences"][classroom_id]
                faculty_scores[faculty_id].append(classroom_preference)
        
        # Calculate average score for each faculty
        average_scores = []
        for faculty_id, scores in faculty_scores.items():
            if scores:
                average_scores.append(sum(scores) / len(scores))
        
        # Convert to 0-100 scale
        if average_scores:
            # Scale from [-2, 5] to [0, 100]
            satisfaction = (sum(average_scores) / len(average_scores) + 2) * (100 / 7)
            return max(0, min(100, satisfaction))
        else:
            return 50.0  # Neutral if no preference data
    
    def _calculate_batch_satisfaction(self, solution: List[Dict[str, Any]]) -> float:
        """
        Calculate batch satisfaction score.
        
        Args:
            solution: A scheduling solution (list of session assignments)
            
        Returns:
            Batch satisfaction score (0-100)
        """
        # For now, we'll use a simple metric: the percentage of required subjects that are scheduled
        if not self.batches:
            return 0.0
            
        total_required = 0
        total_scheduled = 0
        
        for batch in self.batches:
            batch_id = batch["id"]
            required_subjects = self._get_required_subjects_for_batch(batch_id)
            total_required += len(required_subjects)
            
            scheduled_subjects = {
                session["subject_id"] for session in solution
                if session["batch_id"] == batch_id
            }
            
            total_scheduled += len(scheduled_subjects.intersection(required_subjects))
        
        if total_required > 0:
            return (total_scheduled / total_required) * 100
        else:
            return 100.0
    
    def _calculate_room_utilization(self, solution: List[Dict[str, Any]]) -> float:
        """
        Calculate room utilization percentage.
        
        Args:
            solution: A scheduling solution (list of session assignments)
            
        Returns:
            Room utilization percentage (0-100)
        """
        total_slots = len(self.time_slots) * len(self.classrooms)
        if total_slots == 0:
            return 0.0
            
        # Count unique (classroom, time_slot) combinations
        used_slots = set()
        for session in solution:
            classroom_id = session["classroom_id"]
            time_slot_id = session["time_slot_id"]
            used_slots.add((classroom_id, time_slot_id))
        
        return (len(used_slots) / total_slots) * 100
    
    def _tournament_selection(self, population: List[Tuple[List[Dict[str, Any]], float]], tournament_size: int) -> List[Dict[str, Any]]:
        """
        Select an individual using tournament selection.
        
        Args:
            population: List of (individual, fitness) tuples
            tournament_size: Number of individuals in each tournament
            
        Returns:
            The selected individual
        """
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda x: x[1])[0]
    
    def _crossover(self, parent1: List[Dict[str, Any]], parent2: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create a child by combining two parents.
        
        Args:
            parent1: First parent solution
            parent2: Second parent solution
            
        Returns:
            Child solution
        """
        if not parent1 or not parent2:
            return parent1 if parent1 else parent2
            
        # Create a mapping of (batch_id, subject_id) to session for each parent
        parent1_map = {
            (session["batch_id"], session["subject_id"]): session
            for session in parent1
        }
        
        parent2_map = {
            (session["batch_id"], session["subject_id"]): session
            for session in parent2
        }
        
        # Create child by taking sessions from either parent
        child = []
        all_keys = set(parent1_map.keys()).union(parent2_map.keys())
        
        for key in all_keys:
            # If this batch-subject pair exists in both parents, randomly choose one
            if key in parent1_map and key in parent2_map:
                chosen_parent = random.choice([parent1_map, parent2_map])
                child.append(chosen_parent[key].copy())
            
            # If it only exists in one parent, take it from there
            elif key in parent1_map:
                child.append(parent1_map[key].copy())
            else:
                child.append(parent2_map[key].copy())
        
        return child
    
    def _mutate(self, solution: List[Dict[str, Any]], mutation_rate: float) -> List[Dict[str, Any]]:
        """
        Mutate a solution by randomly changing some assignments.
        
        Args:
            solution: A scheduling solution
            mutation_rate: Probability of mutation for each session
            
        Returns:
            Mutated solution
        """
        mutated_solution = []
        
        for session in solution:
            # Clone the session
            new_session = session.copy()
            
            # Decide whether to mutate this session
            if random.random() < mutation_rate:
                # Choose what to mutate (time slot, faculty, or classroom)
                mutation_type = random.choice(["time_slot", "faculty", "classroom"])
                
                if mutation_type == "time_slot":
                    # Change the time slot
                    new_session["time_slot_id"] = random.choice([ts["id"] for ts in self.time_slots])
                    
                elif mutation_type == "faculty":
                    # Find suitable faculty members for this subject
                    suitable_faculty = [
                        faculty["id"] for faculty in self.faculty
                        if self._has_faculty_expertise(faculty["id"], session["subject_id"])
                    ]
                    
                    if suitable_faculty:
                        new_session["faculty_id"] = random.choice(suitable_faculty)
                    
                elif mutation_type == "classroom":
                    # Find suitable classrooms for this subject
                    suitable_classrooms = [
                        classroom["id"] for classroom in self.classrooms
                        if self._is_classroom_suitable(classroom["id"], session["subject_id"])
                    ]
                    
                    if suitable_classrooms:
                        new_session["classroom_id"] = random.choice(suitable_classrooms)
            
            mutated_solution.append(new_session)
        
        return mutated_solution
    
    def _repair(self, solution: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Repair a solution by resolving conflicts.
        
        Args:
            solution: A scheduling solution
            
        Returns:
            Repaired solution
        """
        # Track assignments to detect conflicts
        faculty_conflicts = {}  # (faculty_id, time_slot_id) -> [indices]
        classroom_conflicts = {}  # (classroom_id, time_slot_id) -> [indices]
        batch_conflicts = {}  # (batch_id, time_slot_id) -> [indices]
        
        # Find all conflicts
        for i, session in enumerate(solution):
            batch_id = session["batch_id"]
            time_slot_id = session["time_slot_id"]
            faculty_id = session["faculty_id"]
            classroom_id = session["classroom_id"]
            
            faculty_key = (faculty_id, time_slot_id)
            classroom_key = (classroom_id, time_slot_id)
            batch_key = (batch_id, time_slot_id)
            
            if faculty_key not in faculty_conflicts:
                faculty_conflicts[faculty_key] = []
            faculty_conflicts[faculty_key].append(i)
            
            if classroom_key not in classroom_conflicts:
                classroom_conflicts[classroom_key] = []
            classroom_conflicts[classroom_key].append(i)
            
            if batch_key not in batch_conflicts:
                batch_conflicts[batch_key] = []
            batch_conflicts[batch_key].append(i)
        
        # Resolve conflicts by changing time slots for some sessions
        repaired_solution = solution.copy()
        
        # Helper function to find a non-conflicting time slot
        def find_non_conflicting_time_slot(session_index, current_solution):
            session = current_solution[session_index]
            batch_id = session["batch_id"]
            faculty_id = session["faculty_id"]
            classroom_id = session["classroom_id"]
            
            # Try each time slot
            for time_slot in self.time_slots:
                time_slot_id = time_slot["id"]
                
                # Check if this time slot would cause conflicts
                faculty_key = (faculty_id, time_slot_id)
                classroom_key = (classroom_id, time_slot_id)
                batch_key = (batch_id, time_slot_id)
                
                faculty_conflict = faculty_key in faculty_conflicts and len(faculty_conflicts[faculty_key]) > 0
                classroom_conflict = classroom_key in classroom_conflicts and len(classroom_conflicts[classroom_key]) > 0
                batch_conflict = batch_key in batch_conflicts and len(batch_conflicts[batch_key]) > 0
                
                if not (faculty_conflict or classroom_conflict or batch_conflict):
                    return time_slot_id
            
            # If no non-conflicting time slot found, return a random one
            return random.choice([ts["id"] for ts in self.time_slots])
        
        # Resolve faculty conflicts
        for key, indices in faculty_conflicts.items():
            if len(indices) > 1:
                # Keep one session at this time slot, move others
                keep_index = random.choice(indices)
                for move_index in indices:
                    if move_index != keep_index:
                        new_time_slot = find_non_conflicting_time_slot(move_index, repaired_solution)
                        repaired_solution[move_index]["time_slot_id"] = new_time_slot
        
        # Resolve classroom conflicts
        for key, indices in classroom_conflicts.items():
            if len(indices) > 1:
                # Keep one session at this classroom, move others
                keep_index = random.choice(indices)
                for move_index in indices:
                    if move_index != keep_index:
                        # Find another suitable classroom
                        subject_id = repaired_solution[move_index]["subject_id"]
                        suitable_classrooms = [
                            classroom["id"] for classroom in self.classrooms
                            if self._is_classroom_suitable(classroom["id"], subject_id)
                        ]
                        
                        if suitable_classrooms:
                            repaired_solution[move_index]["classroom_id"] = random.choice(suitable_classrooms)
        
        # Resolve batch conflicts
        for key, indices in batch_conflicts.items():
            if len(indices) > 1:
                # Keep one session at this time slot, move others
                keep_index = random.choice(indices)
                for move_index in indices:
                    if move_index != keep_index:
                        new_time_slot = find_non_conflicting_time_slot(move_index, repaired_solution)
                        repaired_solution[move_index]["time_slot_id"] = new_time_slot
        
        return repaired_solution
    
    def _solution_to_sessions(self, solution: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert a genetic algorithm solution to scheduled session format.
        
        Args:
            solution: A scheduling solution
            
        Returns:
            List of formatted scheduled sessions
        """
        scheduled_sessions = []
        
        for session in solution:
            batch_id = session["batch_id"]
            subject_id = session["subject_id"]
            time_slot_id = session["time_slot_id"]
            faculty_id = session["faculty_id"]
            classroom_id = session["classroom_id"]
            
            # Create a scheduled session
            formatted_session = {
                "id": str(uuid4()),
                "batch_id": str(batch_id),
                "subject_id": str(subject_id),
                "time_slot_id": str(time_slot_id),
                "faculty_id": str(faculty_id),
                "classroom_id": str(classroom_id),
                "status": "SCHEDULED",
            }
            
            # Add additional information if available
            if time_slot_id in self.time_slot_by_id:
                time_slot = self.time_slot_by_id[time_slot_id]
                formatted_session["day_of_week"] = time_slot.get("day_of_week")
                formatted_session["start_time"] = time_slot.get("start_time")
                formatted_session["end_time"] = time_slot.get("end_time")
            
            if batch_id in self.batch_by_id:
                formatted_session["batch_name"] = self.batch_by_id[batch_id].get("name")
            
            if subject_id in self.subject_by_id:
                formatted_session["subject_name"] = self.subject_by_id[subject_id].get("name")
            
            if faculty_id in self.faculty_by_id:
                formatted_session["faculty_name"] = self.faculty_by_id[faculty_id].get("name")
            
            if classroom_id in self.classroom_by_id:
                formatted_session["classroom_name"] = self.classroom_by_id[classroom_id].get("name")
            
            scheduled_sessions.append(formatted_session)
        
        return scheduled_sessions
    
    def _solution_metrics(self, solution: List[Dict[str, Any]], scheduled_sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate metrics for a solution.
        
        Args:
            solution: A scheduling solution
            scheduled_sessions: Formatted scheduled sessions
            
        Returns:
            A dictionary of metrics
        """
        # Hard constraint violations
        hard_violations = self._count_hard_violations(solution)
        
        # Faculty and batch satisfaction
        faculty_satisfaction = self._calculate_faculty_satisfaction(solution)
        batch_satisfaction = self._calculate_batch_satisfaction(solution)
        
        # Room utilization
        room_utilization = self._calculate_room_utilization(solution)
        
        # Count soft constraint violations (faculty teaching non-preferred subjects/batches/classrooms)
        soft_violations = 0
        for session in solution:
            faculty_id = session["faculty_id"]
            if faculty_id not in self.faculty_preferences:
                continue
                
            preferences = self.faculty_preferences[faculty_id]
            
            # Subject preference
            subject_id = session["subject_id"]
            if subject_id in preferences["subject_expertise"]:
                expertise_level = preferences["subject_expertise"][subject_id]
                if expertise_level < 3:  # Below INTERMEDIATE
                    soft_violations += 1
            
            # Batch preference
            batch_id = session["batch_id"]
            if batch_id in preferences["batch_preferences"]:
                batch_preference = preferences["batch_preferences"][batch_id]
                if batch_preference < 0:  # DISLIKE or STRONGLY_DISLIKE
                    soft_violations += 1
            
            # Classroom preference
            classroom_id = session["classroom_id"]
            if classroom_id in preferences["classroom_preferences"]:
                classroom_preference = preferences["classroom_preferences"][classroom_id]
                if classroom_preference < 0:  # DISLIKE or STRONGLY_DISLIKE
                    soft_violations += 1
        
        return {
            "hard_constraint_violations": hard_violations,
            "soft_constraint_violations": soft_violations,
            "faculty_satisfaction_score": faculty_satisfaction,
            "batch_satisfaction_score": batch_satisfaction,
            "room_utilization": room_utilization,
            "total_sessions": len(scheduled_sessions),
            "total_faculty_used": len({session["faculty_id"] for session in solution}),
            "total_classrooms_used": len({session["classroom_id"] for session in solution})
        }
    
    # Helper methods
    def _is_faculty_available(self, faculty_id: UUID, time_slot_id: UUID) -> bool:
        """Check if a faculty is available at a given time slot."""
        if faculty_id not in self.faculty_preferences:
            return True  # Assume available if we don't have preference data
            
        availability = self.faculty_preferences[faculty_id]["availability"]
        
        if time_slot_id not in self.time_slot_by_id:
            return True  # Can't check if we don't have time slot data
            
        time_slot = self.time_slot_by_id[time_slot_id]
        day = time_slot.get("day_of_week")
        slot_type = time_slot.get("slot_type")
        
        if day in availability and slot_type in availability[day]:
            return availability[day][slot_type]
        
        return True  # Default to available
    
    def _get_required_subjects_for_batch(self, batch_id: UUID) -> Set[UUID]:
        """Get the set of subjects required for a batch."""
        # In a real implementation, this would fetch the required subjects for the batch
        # For now, we'll return all subjects
        return {subject["id"] for subject in self.subjects}
    
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
