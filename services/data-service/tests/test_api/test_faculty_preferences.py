import json
import uuid
from typing import Dict, List
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.schemas.faculty_preferences import WeekDay, TimeSlotType, ExpertiseLevel, PreferenceLevel

# Test fixture path
@pytest.fixture
async def create_test_subject(client: AsyncClient, app: FastAPI, test_institution_id: uuid.UUID, create_test_department: str):
    # Create a test subject
    subject_data = {
        "name": "Test Subject",
        "code": "TST101",
        "description": "Test subject for faculty preference tests",
        "credit_hours": 4,
        "lecture_hours_per_week": 3,
        "practical_hours_per_week": 1,
        "department_id": create_test_department
    }
    response = await client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    assert response.status_code == 200
    subject = response.json()["data"]
    yield subject["id"]


@pytest.fixture
async def create_test_batch(client: AsyncClient, app: FastAPI, test_institution_id: uuid.UUID, create_test_department: str):
    # Create a test batch
    batch_data = {
        "name": "Test Batch",
        "year": 2023,
        "semester": 1,
        "capacity": 30,
        "department_id": create_test_department
    }
    response = await client.post(
        "/api/v1/batches",
        json=batch_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    assert response.status_code == 200
    batch = response.json()["data"]
    yield batch["id"]


@pytest.fixture
async def create_test_classroom(client: AsyncClient, app: FastAPI, test_institution_id: uuid.UUID, create_test_room_type: str):
    # Create a test classroom
    classroom_data = {
        "name": "Test Classroom",
        "code": "TC101",
        "capacity": 50,
        "building": "Test Building",
        "floor": 1,
        "room_number": "101",
        "room_type_id": create_test_room_type
    }
    response = await client.post(
        "/api/v1/classrooms",
        json=classroom_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    assert response.status_code == 200
    classroom = response.json()["data"]
    yield classroom["id"]


@pytest.fixture
async def create_test_room_type(client: AsyncClient, app: FastAPI, test_institution_id: uuid.UUID):
    # Create a test room type
    room_type_data = {
        "name": "Test Room Type",
        "description": "Test room type for classroom tests"
    }
    response = await client.post(
        "/api/v1/room_types",
        json=room_type_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    assert response.status_code == 200
    room_type = response.json()["data"]
    yield room_type["id"]


# Faculty Availability Tests
async def test_create_faculty_availability(
    client: AsyncClient, 
    app: FastAPI, 
    test_institution_id: uuid.UUID,
    create_test_faculty: str
):
    """Test creating a faculty availability record."""
    availability_data = {
        "faculty_id": create_test_faculty,
        "day_of_week": WeekDay.MONDAY,
        "time_slot": TimeSlotType.MORNING,
        "is_available": True
    }
    
    response = await client.post(
        "/api/v1/faculty-preferences/availability",
        json=availability_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["faculty_id"] == create_test_faculty
    assert data["day_of_week"] == WeekDay.MONDAY
    assert data["time_slot"] == TimeSlotType.MORNING
    assert data["is_available"] is True
    assert "id" in data


async def test_get_faculty_availability(
    client: AsyncClient, 
    app: FastAPI, 
    test_institution_id: uuid.UUID,
    create_test_faculty: str
):
    """Test getting all availability records for a faculty member."""
    # First create an availability record
    availability_data = {
        "faculty_id": create_test_faculty,
        "day_of_week": WeekDay.TUESDAY,
        "time_slot": TimeSlotType.AFTERNOON,
        "is_available": True
    }
    
    await client.post(
        app.url_path_for("create_faculty_availability"),
        json=availability_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    # Now get all availability records
    response = await client.get(
        f"/api/v1/faculty-preferences/availability/{create_test_faculty}",
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(item["day_of_week"] == WeekDay.TUESDAY and 
               item["time_slot"] == TimeSlotType.AFTERNOON for item in data)


# Faculty Subject Expertise Tests
async def test_create_faculty_expertise(
    client: AsyncClient, 
    app: FastAPI, 
    test_institution_id: uuid.UUID,
    create_test_faculty: str,
    create_test_subject: str
):
    """Test creating a faculty subject expertise record."""
    expertise_data = {
        "faculty_id": create_test_faculty,
        "subject_id": create_test_subject,
        "expertise_level": ExpertiseLevel.ADVANCED
    }
    
    response = await client.post(
        "/api/v1/faculty-preferences/expertise",
        json=expertise_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["faculty_id"] == create_test_faculty
    assert data["subject_id"] == create_test_subject
    assert "id" in data


async def test_get_faculty_expertise(
    client: AsyncClient, 
    app: FastAPI, 
    test_institution_id: uuid.UUID,
    create_test_faculty: str,
    create_test_subject: str
):
    """Test getting all subject expertise records for a faculty member."""
    # First create an expertise record
    expertise_data = {
        "faculty_id": create_test_faculty,
        "subject_id": create_test_subject,
        "expertise_level": ExpertiseLevel.EXPERT
    }
    
    await client.post(
        app.url_path_for("create_faculty_expertise"),
        json=expertise_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    # Now get all expertise records
    response = await client.get(
        f"/api/v1/faculty-preferences/expertise/{create_test_faculty}",
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) > 0
    # Check that subject name is included
    assert any(item["subject_id"] == create_test_subject and "subject_name" in item for item in data)


# Faculty Batch Preference Tests
async def test_create_batch_preference(
    client: AsyncClient, 
    app: FastAPI, 
    test_institution_id: uuid.UUID,
    create_test_faculty: str,
    create_test_batch: str
):
    """Test creating a faculty batch preference."""
    preference_data = {
        "faculty_id": create_test_faculty,
        "batch_id": create_test_batch,
        "preference_level": PreferenceLevel.PREFER
    }
    
    response = await client.post(
        "/api/v1/faculty-preferences/batch-preference",
        json=preference_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["faculty_id"] == create_test_faculty
    assert data["batch_id"] == create_test_batch
    assert "id" in data


async def test_get_batch_preferences(
    client: AsyncClient, 
    app: FastAPI, 
    test_institution_id: uuid.UUID,
    create_test_faculty: str,
    create_test_batch: str
):
    """Test getting all batch preferences for a faculty member."""
    # First create a batch preference
    preference_data = {
        "faculty_id": create_test_faculty,
        "batch_id": create_test_batch,
        "preference_level": PreferenceLevel.STRONGLY_PREFER
    }
    
    await client.post(
        app.url_path_for("create_batch_preference"),
        json=preference_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    # Now get all batch preferences
    response = await client.get(
        f"/api/v1/faculty-preferences/batch-preference/{create_test_faculty}",
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) > 0
    # Check that batch name is included
    assert any(item["batch_id"] == create_test_batch and "batch_name" in item for item in data)


# Faculty Classroom Preference Tests
async def test_create_classroom_preference(
    client: AsyncClient, 
    app: FastAPI, 
    test_institution_id: uuid.UUID,
    create_test_faculty: str,
    create_test_classroom: str
):
    """Test creating a faculty classroom preference."""
    preference_data = {
        "faculty_id": create_test_faculty,
        "classroom_id": create_test_classroom,
        "preference_level": PreferenceLevel.PREFER
    }
    
    response = await client.post(
        "/api/v1/faculty-preferences/classroom-preference",
        json=preference_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["faculty_id"] == create_test_faculty
    assert data["classroom_id"] == create_test_classroom
    assert "id" in data


async def test_get_classroom_preferences(
    client: AsyncClient, 
    app: FastAPI, 
    test_institution_id: uuid.UUID,
    create_test_faculty: str,
    create_test_classroom: str
):
    """Test getting all classroom preferences for a faculty member."""
    # First create a classroom preference
    preference_data = {
        "faculty_id": create_test_faculty,
        "classroom_id": create_test_classroom,
        "preference_level": PreferenceLevel.STRONGLY_PREFER
    }
    
    await client.post(
        app.url_path_for("create_classroom_preference"),
        json=preference_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    # Now get all classroom preferences
    response = await client.get(
        f"/api/v1/faculty-preferences/classroom-preference/{create_test_faculty}",
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) > 0
    # Check that classroom name is included
    assert any(item["classroom_id"] == create_test_classroom and "classroom_name" in item for item in data)


# All Faculty Preferences Test
async def test_get_all_faculty_preferences(
    client: AsyncClient, 
    app: FastAPI, 
    test_institution_id: uuid.UUID,
    create_test_faculty: str
):
    """Test getting all preferences for a faculty member."""
    # First ensure we have at least one of each preference type
    # (Assuming previous tests have created these)
    
    response = await client.get(
        f"/api/v1/faculty-preferences/{create_test_faculty}/all-preferences",
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["faculty_id"] == create_test_faculty
    
    # Check that each preference type is present in the response
    assert "availability" in data
    assert "subject_expertise" in data
    assert "batch_preferences" in data
    assert "classroom_preferences" in data
