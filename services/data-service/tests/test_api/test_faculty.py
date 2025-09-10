import json
import uuid
from typing import Dict, List
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.models.faculty import Faculty

# Test data for faculty
test_faculty_data = {
    "name": "Test Faculty",
    "employee_id": "EMP123",
    "email": "test.faculty@example.com",
    "phone": "1234567890",
    "designation": "Associate Professor",
    "weekly_load_hours": 40
}

@pytest.fixture
async def create_test_department(client: AsyncClient, app: FastAPI, test_institution_id: uuid.UUID):
    # Create a test department
    department_data = {
        "name": "Test Department",
        "code": "TD",
        "description": "Test department for faculty tests"
    }
    response = await client.post(
        "/api/v1/departments",
        json=department_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    assert response.status_code == 200
    department = response.json()["data"]
    yield department["id"]


@pytest.fixture
async def create_test_faculty(client: AsyncClient, app: FastAPI, test_institution_id: uuid.UUID, create_test_department: str):
    # Create test faculty with the test department
    faculty_data = {**test_faculty_data, "department_id": create_test_department}
    
    response = await client.post(
        app.url_path_for("create_faculty"),
        json=faculty_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    assert response.status_code == 200
    faculty = response.json()["data"]
    yield faculty["id"]


async def test_create_faculty(
    client: AsyncClient, 
    app: FastAPI, 
    test_institution_id: uuid.UUID,
    create_test_department: str
):
    """Test creating a new faculty member."""
    # Create faculty data with test department
    faculty_data = {**test_faculty_data, "department_id": create_test_department}
    
    response = await client.post(
        "/api/v1/faculty",
        json=faculty_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == faculty_data["name"]
    assert data["employee_id"] == faculty_data["employee_id"]
    assert data["email"] == faculty_data["email"]
    assert data["department_id"] == create_test_department
    assert data["institution_id"] == str(test_institution_id)
    assert "id" in data


async def test_get_all_faculty(
    client: AsyncClient, 
    app: FastAPI, 
    test_institution_id: uuid.UUID,
    create_test_faculty: str
):
    """Test getting all faculty members."""
    response = await client.get(
        "/api/v1/faculty",
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0
    assert data["count"] > 0


async def test_get_faculty(
    client: AsyncClient, 
    app: FastAPI, 
    test_institution_id: uuid.UUID,
    create_test_faculty: str
):
    """Test getting a specific faculty member."""
    response = await client.get(
        f"/api/v1/faculty/{create_test_faculty}",
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == create_test_faculty
    assert data["name"] == test_faculty_data["name"]
    assert data["employee_id"] == test_faculty_data["employee_id"]


async def test_get_faculty_details(
    client: AsyncClient, 
    app: FastAPI, 
    test_institution_id: uuid.UUID,
    create_test_faculty: str
):
    """Test getting a faculty member with department details."""
    response = await client.get(
        f"/api/v1/faculty/{create_test_faculty}/details",
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == create_test_faculty
    assert data["name"] == test_faculty_data["name"]
    assert "department_name" in data
    assert data["department_name"] == "Test Department"


async def test_update_faculty(
    client: AsyncClient, 
    app: FastAPI, 
    test_institution_id: uuid.UUID,
    create_test_faculty: str
):
    """Test updating a faculty member."""
    update_data = {
        "name": "Updated Faculty Name",
        "designation": "Professor"
    }
    
    response = await client.put(
        f"/api/v1/faculty/{create_test_faculty}",
        json=update_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == create_test_faculty
    assert data["name"] == update_data["name"]
    assert data["designation"] == update_data["designation"]
    # Ensure other fields weren't changed
    assert data["employee_id"] == test_faculty_data["employee_id"]
    assert data["email"] == test_faculty_data["email"]


async def test_delete_faculty(
    client: AsyncClient, 
    app: FastAPI, 
    test_institution_id: uuid.UUID,
    create_test_faculty: str
):
    """Test deleting a faculty member."""
    response = await client.delete(
        f"/api/v1/faculty/{create_test_faculty}",
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert data is True
    
    # Verify the faculty no longer exists
    response = await client.get(
        f"/api/v1/faculty/{create_test_faculty}",
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    assert response.status_code == 404
