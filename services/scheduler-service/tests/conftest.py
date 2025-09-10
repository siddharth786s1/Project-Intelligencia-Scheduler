"""
Pytest fixtures for the scheduler service tests
"""
import pytest
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any

from app.schemas.scheduler import SchedulingRequest, AlgorithmType


@pytest.fixture
def test_data():
    """Common test data"""
    return {
        "faculty_id": uuid.uuid4(),
        "subject_id": uuid.uuid4(),
        "batch_id": uuid.uuid4(),
        "classroom_id": uuid.uuid4(),
        "time_slot_id": uuid.uuid4(),
        "institution_id": uuid.uuid4()
    }


@pytest.fixture
def auth_headers(test_data):
    """Authentication headers for testing"""
    return {
        "Authorization": "Bearer test-token",
        "X-Institution-ID": str(test_data["institution_id"])
    }


@pytest.fixture
def scheduling_request():
    """Sample scheduling request for testing"""
    return SchedulingRequest(
        name="Test Schedule",
        description="Test schedule for unit testing",
        academic_term="Fall 2025",
        start_date="2025-09-01",
        end_date="2025-12-15",
        algorithm_type=AlgorithmType.CSP,
        max_iterations=50
    )
