import pytest
from fastapi import status

pytestmark = pytest.mark.asyncio

async def test_get_subjects(test_db, client, super_admin_token_headers):
    response = client.get("/api/v1/subjects", headers=super_admin_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data

async def test_create_subject(test_db, client, super_admin_token_headers):
    # Get department id
    dept_resp = client.get("/api/v1/departments", headers=super_admin_token_headers)
    dept_id = dept_resp.json()["items"][0]["id"]
    new_subject = {
        "department_id": dept_id,
        "code": "CS101",
        "name": "Intro to CS",
        "credits": 4,
        "lecture_hours_per_week": 3
    }
    response = client.post("/api/v1/subjects", json=new_subject, headers=super_admin_token_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == new_subject["name"]
    assert data["code"] == new_subject["code"]
    assert data["department_id"] == dept_id

async def test_get_batches(test_db, client, super_admin_token_headers):
    response = client.get("/api/v1/batches", headers=super_admin_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data

async def test_create_batch(test_db, client, super_admin_token_headers):
    # Get department id
    dept_resp = client.get("/api/v1/departments", headers=super_admin_token_headers)
    dept_id = dept_resp.json()["items"][0]["id"]
    new_batch = {
        "department_id": dept_id,
        "name": "Batch 2025",
        "academic_year": "2025-2026",
        "semester": 1,
        "strength": 60
    }
    response = client.post("/api/v1/batches", json=new_batch, headers=super_admin_token_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == new_batch["name"]
    assert data["department_id"] == dept_id
    assert data["academic_year"] == new_batch["academic_year"]
    assert data["semester"] == new_batch["semester"]
    assert data["strength"] == new_batch["strength"]
