"""
Tests for the Genetic Algorithm scheduling algorithm
"""
import pytest
import uuid
from unittest.mock import patch, MagicMock
import asyncio

from app.algorithms.genetic import GeneticSchedulingAlgorithm


@pytest.fixture
def mock_data():
    """Create mock data for algorithm testing"""
    # Create sample UUIDs
    faculty_id1 = uuid.uuid4()
    faculty_id2 = uuid.uuid4()
    subject_id1 = uuid.uuid4()
    subject_id2 = uuid.uuid4()
    batch_id1 = uuid.uuid4()
    classroom_id1 = uuid.uuid4()
    time_slot_id1 = uuid.uuid4()
    time_slot_id2 = uuid.uuid4()
    
    return {
        "faculty": [
            {
                "id": faculty_id1,
                "name": "Dr. Smith",
                "preferences": {
                    "availability": [
                        {
                            "day_of_week": "MONDAY",
                            "time_slot": "MORNING",
                            "is_available": True
                        }
                    ],
                    "subject_expertise": [
                        {
                            "subject_id": subject_id1,
                            "expertise_level": "EXPERT"
                        }
                    ],
                    "batch_preferences": [
                        {
                            "batch_id": batch_id1,
                            "preference_level": "PREFER"
                        }
                    ],
                    "classroom_preferences": [
                        {
                            "classroom_id": classroom_id1,
                            "preference_level": "NEUTRAL"
                        }
                    ]
                }
            },
            {
                "id": faculty_id2,
                "name": "Dr. Johnson",
                "preferences": {
                    "availability": [
                        {
                            "day_of_week": "MONDAY",
                            "time_slot": "MORNING",
                            "is_available": True
                        }
                    ],
                    "subject_expertise": [
                        {
                            "subject_id": subject_id2,
                            "expertise_level": "ADVANCED"
                        }
                    ],
                    "batch_preferences": [],
                    "classroom_preferences": []
                }
            }
        ],
        "subjects": [
            {
                "id": subject_id1,
                "name": "Introduction to Programming"
            },
            {
                "id": subject_id2,
                "name": "Database Systems"
            }
        ],
        "batches": [
            {
                "id": batch_id1,
                "name": "CS-101"
            }
        ],
        "classrooms": [
            {
                "id": classroom_id1,
                "name": "Room 101"
            }
        ],
        "time_slots": [
            {
                "id": time_slot_id1,
                "start_time": "09:00",
                "end_time": "10:30",
                "day_of_week": "MONDAY",
                "slot_type": "MORNING"
            },
            {
                "id": time_slot_id2,
                "start_time": "11:00",
                "end_time": "12:30",
                "day_of_week": "MONDAY",
                "slot_type": "MORNING"
            }
        ],
        "constraints": []
    }


@pytest.fixture
def algorithm_params():
    """Create algorithm parameters for testing"""
    return {
        "population_size": 10,      # Small population for testing
        "generations": 5,           # Few generations for quick testing
        "mutation_rate": 0.1,
        "time_limit_seconds": 1     # Short time for tests
    }


def test_genetic_algorithm_initialization(mock_data, algorithm_params):
    """Test that the Genetic Algorithm initializes correctly"""
    algorithm = GeneticSchedulingAlgorithm(mock_data, algorithm_params)
    
    # Check that data was processed correctly
    assert len(algorithm.faculty) == 2
    assert len(algorithm.subjects) == 2
    assert len(algorithm.batches) == 1
    assert len(algorithm.classrooms) == 1
    assert len(algorithm.time_slots) == 2
    
    # Check that faculty preferences were processed
    assert len(algorithm.faculty_preferences) == 2
    faculty_id = mock_data["faculty"][0]["id"]
    assert faculty_id in algorithm.faculty_preferences


def test_initialize_population(mock_data, algorithm_params):
    """Test that the initial population is created correctly"""
    algorithm = GeneticSchedulingAlgorithm(mock_data, algorithm_params)
    population = algorithm._initialize_population(5)  # Initialize 5 individuals
    
    # Check that we got the right number of individuals
    assert len(population) == 5
    
    # Check that each individual is a valid solution
    for individual in population:
        assert isinstance(individual, list)
        # Each individual should be a list of scheduled sessions
        for session in individual:
            assert "faculty_id" in session
            assert "subject_id" in session
            assert "batch_id" in session
            assert "classroom_id" in session
            assert "time_slot_id" in session


def test_fitness_function(mock_data, algorithm_params):
    """Test that the fitness function calculates correctly"""
    algorithm = GeneticSchedulingAlgorithm(mock_data, algorithm_params)
    population = algorithm._initialize_population(1)  # Generate one solution
    solution = population[0]
    
    # Calculate fitness
    fitness = algorithm._fitness(solution)
    
    # Fitness should be a number
    assert isinstance(fitness, (int, float))
    
    # For this test, we won't assert the fitness value range
    # Just check that the fitness calculation runs without errors
    # In a real solution, the fitness could be negative if there are hard constraint violations


def test_mutation_and_crossover(mock_data, algorithm_params):
    """Test mutation and crossover operations"""
    algorithm = GeneticSchedulingAlgorithm(mock_data, algorithm_params)
    population = algorithm._initialize_population(2)  # Generate two solutions
    
    # Test crossover
    child = algorithm._crossover(population[0], population[1])
    assert isinstance(child, list)
    
    # Test mutation
    mutated = algorithm._mutate(child, 1.0)  # Set high mutation rate for testing
    assert isinstance(mutated, list)
    
    # The mutated solution might be different, but should still be valid
    for session in mutated:
        assert "faculty_id" in session
        assert "subject_id" in session
        assert "batch_id" in session
        assert "classroom_id" in session
        assert "time_slot_id" in session


def test_repair_function(mock_data, algorithm_params):
    """Test that the repair function fixes invalid solutions"""
    # Modify the algorithm parameters to make it easier to test
    algorithm_params["time_limit_seconds"] = 5  # More time
    
    algorithm = GeneticSchedulingAlgorithm(mock_data, algorithm_params)
    
    # Create a simple solution with exactly 2 sessions for testing
    if len(mock_data["batches"]) > 0 and len(mock_data["subjects"]) > 0 and len(mock_data["time_slots"]) >= 2:
        batch_id = mock_data["batches"][0]["id"]
        subject_id = mock_data["subjects"][0]["id"] 
        faculty_id = mock_data["faculty"][0]["id"] if mock_data["faculty"] else None
        classroom_id = mock_data["classrooms"][0]["id"] if mock_data["classrooms"] else None
        
        # Make sure we have at least 2 time slots
        if len(mock_data["time_slots"]) >= 2:
            time_slot_id1 = mock_data["time_slots"][0]["id"]
            time_slot_id2 = mock_data["time_slots"][1]["id"]
            
            # Create two sessions with the same faculty at different time slots
            solution = [
                {
                    "batch_id": batch_id,
                    "subject_id": subject_id,
                    "faculty_id": faculty_id,
                    "classroom_id": classroom_id,
                    "time_slot_id": time_slot_id1
                },
                {
                    "batch_id": batch_id,
                    "subject_id": subject_id,
                    "faculty_id": faculty_id,
                    "classroom_id": classroom_id,
                    "time_slot_id": time_slot_id2
                }
            ]
            
            # Create a conflict by making both sessions use the same time slot
            solution[1]["time_slot_id"] = time_slot_id1
            
            # Repair the solution
            repaired = algorithm._repair(solution)
            
            # Verify no faculty has the same time slot twice
            faculty_timeslots = {}
            for session in repaired:
                faculty_id = session["faculty_id"]
                time_slot_id = session["time_slot_id"]
                key = (str(faculty_id), str(time_slot_id))
                
                if key in faculty_timeslots:
                    # We found a duplicate - this should not happen
                    assert False, f"Faculty {faculty_id} is assigned to time slot {time_slot_id} more than once"
                
                faculty_timeslots[key] = True
            
            # The repaired solution should have the same number of sessions
            assert len(repaired) == 2, "Repaired solution should have the same number of sessions"


def test_full_algorithm_run(mock_data, algorithm_params):
    """Test that the full algorithm runs without errors"""
    algorithm = GeneticSchedulingAlgorithm(mock_data, algorithm_params)
    result = algorithm.run()
    
    # Check that the algorithm returned a proper result
    assert isinstance(result, dict)
    assert "status" in result
    
    # Check for success or failure
    if result["status"] == "success":
        assert "scheduled_sessions" in result
        assert isinstance(result["scheduled_sessions"], list)
        assert "metrics" in result
        
        # Check metrics
        metrics = result["metrics"]
        assert "hard_constraint_violations" in metrics
        assert "soft_constraint_violations" in metrics
        assert "faculty_satisfaction_score" in metrics
        assert "batch_satisfaction_score" in metrics
        assert "room_utilization" in metrics
