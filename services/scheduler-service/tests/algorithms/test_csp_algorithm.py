"""
Tests for the CSP scheduling algorithm
"""
import pytest
import uuid
from unittest.mock import patch, MagicMock
import asyncio

from app.algorithms.csp import CSPSchedulingAlgorithm


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
        "max_time_in_seconds": 5  # Short time for tests
    }


def test_csp_algorithm_initialization(mock_data, algorithm_params):
    """Test that the CSP algorithm initializes correctly"""
    algorithm = CSPSchedulingAlgorithm(mock_data, algorithm_params)
    
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
    
    # Check that lookups were created
    assert len(algorithm.faculty_by_id) == 2
    assert len(algorithm.subject_by_id) == 2
    assert len(algorithm.batch_by_id) == 1
    assert len(algorithm.classroom_by_id) == 1
    assert len(algorithm.time_slot_by_id) == 2


@patch("app.algorithms.csp.cp_model")
def test_csp_algorithm_run(mock_cp_model, mock_data, algorithm_params):
    """Test running the CSP algorithm with mocked OR-Tools"""
    # Create a mock solver
    mock_solver = MagicMock()
    mock_cp_model.CpSolver.return_value = mock_solver
    
    # Mock solver status and value function
    mock_solver.Solve.return_value = mock_cp_model.OPTIMAL
    mock_solver.Value.return_value = 1  # All variables are true
    
    # Initialize and run the algorithm
    algorithm = CSPSchedulingAlgorithm(mock_data, algorithm_params)
    result = algorithm.run()
    
    # Check that the algorithm ran successfully
    assert result["status"] == "success"
    assert "sessions" in result
    assert "metrics" in result
    
    # Check that the solver was called
    mock_solver.Solve.assert_called_once()
    
    # Check that sessions were created
    assert isinstance(result["sessions"], list)
    
    # Check that metrics were calculated
    metrics = result["metrics"]
    assert "hard_constraint_violations" in metrics
    assert "soft_constraint_violations" in metrics
    assert "faculty_satisfaction_score" in metrics
    assert "batch_satisfaction_score" in metrics
    assert "room_utilization" in metrics
