from typing import Dict, List, Any, Tuple, Optional, Callable
from uuid import UUID, uuid4
import logging
import random
from datetime import datetime, time

import numpy as np
from deap import base, creator, tools, algorithms

from app.services.algorithms.base import SchedulingAlgorithm, ConstraintType
from app.core.errors import SchedulingException, OptimizationException

logger = logging.getLogger(__name__)


class GeneticAlgorithmScheduler(SchedulingAlgorithm):
    """
    Genetic Algorithm scheduler for timetable optimization
    """
    
    def __init__(self, data: Dict[str, Any], params: Dict[str, Any]):
        super().__init__(data, params)
        
        # Parameters for the genetic algorithm
        self.population_size = params.get("population_size", 100)
        self.max_generations = params.get("max_generations", 200)
        self.mutation_rate = params.get("mutation_rate", 0.1)
        self.crossover_rate = params.get("crossover_rate", 0.8)
        
        # If an initial solution is provided, use it
        self.initial_solution = data.get("initial_solution", [])
        
        # Initialize indices for entities
        self.faculty_indices = {f["id"]: i for i, f in enumerate(self.faculty)}
        self.batch_indices = {b["id"]: i for i, b in enumerate(self.batches)}
        self.classroom_indices = {c["id"]: i for i, c in enumerate(self.classrooms)}
        self.subject_indices = {s["id"]: i for i, s in enumerate(self.subjects)}
        self.time_slot_indices = {t["id"]: i for i, t in enumerate(self.time_slots)}
        
        # DEAP components
        self.toolbox = None
        
    def run(self) -> Dict[str, Any]:
        """
        Run the genetic algorithm scheduler
        """
        logger.info("Running genetic algorithm scheduler")
        
        # If no initial solution, use empty list
        if not self.initial_solution:
            logger.warning("No initial solution provided, starting with random population")
        
        # Setup the genetic algorithm
        self._setup_genetic_algorithm()
        
        # Run the genetic algorithm
        logger.info(f"Running GA with population={self.population_size}, generations={self.max_generations}")
        pop, log = algorithms.eaSimple(
            self.toolbox.population(n=self.population_size),
            self.toolbox,
            cxpb=self.crossover_rate,
            mutpb=self.mutation_rate,
            ngen=self.max_generations,
            stats=self._setup_stats(),
            halloffame=tools.HallOfFame(1),
            verbose=True
        )
        
        # Get the best individual
        best = tools.selBest(pop, 1)[0]
        
        # Convert the best individual to a schedule
        schedule = self._individual_to_schedule(best)
        
        # Calculate metrics
        metrics = self._calculate_metrics(schedule)
        
        return {
            "sessions": schedule,
            "metrics": metrics
        }
    
    def _setup_genetic_algorithm(self):
        """
        Setup the genetic algorithm components
        """
        # Create fitness and individual classes
        if not hasattr(creator, "FitnessMulti"):
            creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0, 1.0, 1.0))
        
        if not hasattr(creator, "Individual"):
            creator.create("Individual", list, fitness=creator.FitnessMulti)
        
        # Initialize toolbox
        self.toolbox = base.Toolbox()
        
        # Register gene (allele) generation
        self._register_gene_generation()
        
        # Register individual generation
        self._register_individual_generation()
        
        # Register operators
        self._register_operators()
    
    def _register_gene_generation(self):
        """
        Register gene (allele) generation functions
        """
        # Define a gene as a tuple (faculty_idx, batch_idx, subject_idx, classroom_idx, time_slot_idx)
        
        # Helper function to create a random gene
        def random_gene():
            f = random.randint(0, len(self.faculty) - 1)
            b = random.randint(0, len(self.batches) - 1)
            s = random.randint(0, len(self.subjects) - 1)
            c = random.randint(0, len(self.classrooms) - 1)
            t = random.randint(0, len(self.time_slots) - 1)
            return (f, b, s, c, t)
        
        # Register gene generation function
        self.toolbox.register("gene", random_gene)
    
    def _register_individual_generation(self):
        """
        Register individual generation functions
        """
        # If we have an initial solution, use it to create the initial individual
        if self.initial_solution:
            # Helper function to create an individual from the initial solution
            def create_initial_individual():
                genes = []
                for session in self.initial_solution:
                    f = self.faculty_indices.get(session["faculty_id"], 0)
                    b = self.batch_indices.get(session["batch_id"], 0)
                    s = self.subject_indices.get(session["subject_id"], 0)
                    c = self.classroom_indices.get(session["classroom_id"], 0)
                    t = self.time_slot_indices.get(session["time_slot_id"], 0)
                    genes.append((f, b, s, c, t))
                return creator.Individual(genes)
            
            # Register individual generation function
            self.toolbox.register("individual", create_initial_individual)
        else:
            # Generate random individuals
            self.toolbox.register(
                "individual", 
                tools.initRepeat, 
                creator.Individual, 
                self.toolbox.gene, 
                n=20  # Starting with 20 sessions per individual
            )
        
        # Register population generation function
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
    
    def _register_operators(self):
        """
        Register genetic operators (selection, crossover, mutation, evaluation)
        """
        # Register selection operator (tournament selection)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        
        # Register custom crossover operator
        self.toolbox.register("mate", self._custom_crossover)
        
        # Register custom mutation operator
        self.toolbox.register("mutate", self._custom_mutation)
        
        # Register evaluation function
        self.toolbox.register("evaluate", self._evaluate_schedule)
    
    def _custom_crossover(self, ind1, ind2):
        """
        Custom crossover operator for timetables
        """
        # Simple one-point crossover
        if len(ind1) > 1 and len(ind2) > 1:
            cxpoint = random.randint(1, min(len(ind1), len(ind2)) - 1)
            ind1[cxpoint:], ind2[cxpoint:] = ind2[cxpoint:], ind1[cxpoint:]
        return ind1, ind2
    
    def _custom_mutation(self, individual):
        """
        Custom mutation operator for timetables
        """
        if len(individual) == 0:
            return individual,
            
        # Choose a random gene to mutate
        idx = random.randint(0, len(individual) - 1)
        
        # Choose what to mutate (faculty, classroom, or time slot)
        mutation_type = random.choice(["faculty", "classroom", "time_slot"])
        
        if mutation_type == "faculty":
            # Mutate faculty
            f = random.randint(0, len(self.faculty) - 1)
            individual[idx] = (f, individual[idx][1], individual[idx][2], individual[idx][3], individual[idx][4])
        elif mutation_type == "classroom":
            # Mutate classroom
            c = random.randint(0, len(self.classrooms) - 1)
            individual[idx] = (individual[idx][0], individual[idx][1], individual[idx][2], c, individual[idx][4])
        else:
            # Mutate time slot
            t = random.randint(0, len(self.time_slots) - 1)
            individual[idx] = (individual[idx][0], individual[idx][1], individual[idx][2], individual[idx][3], t)
            
        return individual,
    
    def _evaluate_schedule(self, individual):
        """
        Evaluate the fitness of a schedule
        
        Returns a tuple with:
        - hard_violations: Number of hard constraint violations (minimize)
        - soft_violations: Number of soft constraint violations (minimize)
        - faculty_satisfaction: Faculty satisfaction score (maximize)
        - batch_satisfaction: Batch satisfaction score (maximize)
        """
        hard_violations = 0
        soft_violations = 0
        
        # Convert individual to schedule for easier processing
        schedule = self._individual_to_schedule(individual)
        
        # Check for time conflicts
        hard_violations += self._count_time_conflicts(schedule)
        
        # Check for faculty availability violations
        hard_violations += self._count_faculty_availability_violations(schedule)
        
        # Check for classroom capacity violations
        hard_violations += self._count_classroom_capacity_violations(schedule)
        
        # Count soft constraint violations
        soft_violations += self._count_soft_constraint_violations(schedule)
        
        # Calculate satisfaction scores
        faculty_satisfaction = self._calculate_faculty_satisfaction(schedule)
        batch_satisfaction = self._calculate_batch_satisfaction(schedule)
        
        return hard_violations, soft_violations, faculty_satisfaction, batch_satisfaction
    
    def _setup_stats(self):
        """
        Setup statistics for the GA
        """
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("min", np.min, axis=0)
        stats.register("avg", np.mean, axis=0)
        stats.register("std", np.std, axis=0)
        stats.register("max", np.max, axis=0)
        return stats
    
    def _individual_to_schedule(self, individual) -> List[Dict[str, Any]]:
        """
        Convert an individual to a schedule
        """
        schedule = []
        
        for gene in individual:
            f_idx, b_idx, s_idx, c_idx, t_idx = gene
            
            # Get the original entity IDs
            faculty_id = next((id for id, i in self.faculty_indices.items() if i == f_idx), None)
            batch_id = next((id for id, i in self.batch_indices.items() if i == b_idx), None)
            subject_id = next((id for id, i in self.subject_indices.items() if i == s_idx), None)
            classroom_id = next((id for id, i in self.classroom_indices.items() if i == c_idx), None)
            time_slot_id = next((id for id, i in self.time_slot_indices.items() if i == t_idx), None)
            
            # Skip if any ID is not found
            if not faculty_id or not batch_id or not subject_id or not classroom_id or not time_slot_id:
                continue
            
            # Get names for better readability
            faculty_name = next((f["name"] for f in self.faculty if f["id"] == faculty_id), "Unknown")
            batch_name = next((b["name"] for b in self.batches if b["id"] == batch_id), "Unknown")
            subject_name = next((s["name"] for s in self.subjects if s["id"] == subject_id), "Unknown")
            classroom_name = next((c["name"] for c in self.classrooms if c["id"] == classroom_id), "Unknown")
            
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
            
            schedule.append(session)
        
        return schedule
    
    def _count_time_conflicts(self, schedule: List[Dict[str, Any]]) -> int:
        """
        Count the number of time conflicts in the schedule
        """
        conflicts = 0
        
        # Check faculty time conflicts
        faculty_times = {}
        for session in schedule:
            faculty_id = session["faculty_id"]
            time_slot_id = session["time_slot_id"]
            key = f"{faculty_id}_{time_slot_id}"
            
            if key in faculty_times:
                conflicts += 1
            else:
                faculty_times[key] = True
        
        # Check batch time conflicts
        batch_times = {}
        for session in schedule:
            batch_id = session["batch_id"]
            time_slot_id = session["time_slot_id"]
            key = f"{batch_id}_{time_slot_id}"
            
            if key in batch_times:
                conflicts += 1
            else:
                batch_times[key] = True
        
        # Check classroom time conflicts
        classroom_times = {}
        for session in schedule:
            classroom_id = session["classroom_id"]
            time_slot_id = session["time_slot_id"]
            key = f"{classroom_id}_{time_slot_id}"
            
            if key in classroom_times:
                conflicts += 1
            else:
                classroom_times[key] = True
        
        return conflicts
    
    def _count_faculty_availability_violations(self, schedule: List[Dict[str, Any]]) -> int:
        """
        Count the number of faculty availability violations
        """
        violations = 0
        
        for session in schedule:
            faculty_id = session["faculty_id"]
            time_slot_id = session["time_slot_id"]
            
            # Find the faculty
            faculty = next((f for f in self.faculty if f["id"] == faculty_id), None)
            if faculty:
                unavailable_slots = faculty.get("unavailable_time_slots", [])
                if time_slot_id in unavailable_slots:
                    violations += 1
        
        return violations
    
    def _count_classroom_capacity_violations(self, schedule: List[Dict[str, Any]]) -> int:
        """
        Count the number of classroom capacity violations
        """
        violations = 0
        
        for session in schedule:
            batch_id = session["batch_id"]
            classroom_id = session["classroom_id"]
            
            # Find the batch and classroom
            batch = next((b for b in self.batches if b["id"] == batch_id), None)
            classroom = next((c for c in self.classrooms if c["id"] == classroom_id), None)
            
            if batch and classroom:
                batch_size = batch.get("size", 0)
                classroom_capacity = classroom.get("capacity", 0)
                
                if batch_size > classroom_capacity:
                    violations += 1
        
        return violations
    
    def _count_soft_constraint_violations(self, schedule: List[Dict[str, Any]]) -> int:
        """
        Count the number of soft constraint violations
        """
        # Placeholder implementation
        # In a real implementation, we would count violations of soft constraints
        return len(self.constraints) // 3  # Placeholder
    
    def _calculate_faculty_satisfaction(self, schedule: List[Dict[str, Any]]) -> float:
        """
        Calculate the faculty satisfaction score
        """
        # Placeholder implementation
        # In a real implementation, we would calculate based on preferences
        return 80.0 + random.random() * 20.0  # Placeholder
    
    def _calculate_batch_satisfaction(self, schedule: List[Dict[str, Any]]) -> float:
        """
        Calculate the batch satisfaction score
        """
        # Placeholder implementation
        # In a real implementation, we would calculate based on preferences
        return 80.0 + random.random() * 20.0  # Placeholder
    
    def _calculate_metrics(self, schedule: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate metrics for the generated schedule
        """
        # Evaluate the schedule
        hard_violations, soft_violations, faculty_satisfaction, batch_satisfaction = \
            self._evaluate_schedule(self._schedule_to_individual(schedule))
        
        # Calculate room utilization
        room_utilization = self._calculate_room_utilization(schedule)
        
        return {
            "hard_constraint_violations": hard_violations,
            "soft_constraint_violations": soft_violations,
            "faculty_satisfaction_score": faculty_satisfaction,
            "batch_satisfaction_score": batch_satisfaction,
            "room_utilization": room_utilization
        }
    
    def _schedule_to_individual(self, schedule: List[Dict[str, Any]]) -> List[Tuple[int, int, int, int, int]]:
        """
        Convert a schedule back to an individual (list of genes)
        """
        individual = []
        
        for session in schedule:
            f_idx = self.faculty_indices.get(session["faculty_id"], 0)
            b_idx = self.batch_indices.get(session["batch_id"], 0)
            s_idx = self.subject_indices.get(session["subject_id"], 0)
            c_idx = self.classroom_indices.get(session["classroom_id"], 0)
            t_idx = self.time_slot_indices.get(session["time_slot_id"], 0)
            
            individual.append((f_idx, b_idx, s_idx, c_idx, t_idx))
        
        return individual
    
    def _calculate_room_utilization(self, schedule: List[Dict[str, Any]]) -> float:
        """
        Calculate the room utilization percentage
        """
        # Placeholder implementation
        # In a real implementation, we would calculate based on:
        # - Number of time slots used out of all available
        # - Classroom capacity utilization
        return 70.0 + random.random() * 30.0  # Placeholder
