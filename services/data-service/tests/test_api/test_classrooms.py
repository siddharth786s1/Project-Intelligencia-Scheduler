import pytest
from fastapi import status

pytestmark = pytest.mark.asyncio

async def test_get_classrooms(test_db, client, super_admin_token_headers):
    response = client.get("/api/v1/classrooms", headers=super_admin_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data

async def test_create_classroom(test_db, client, super_admin_token_headers):
    # Get institution id and room type id
    inst_resp = client.get("/api/v1/institutions", headers=super_admin_token_headers)
    inst_id = inst_resp.json()["items"][0]["id"]
    # Assume room type exists or create one
    room_type = {"name": "Lecture Hall", "institution_id": inst_id}
    rt_resp = client.post("/api/v1/room_types", json=room_type, headers=super_admin_token_headers)
    room_type_id = rt_resp.json()["id"]
    new_classroom = {
        "name": "Room 101",
        "capacity": 60,
        "room_type_id": room_type_id,
        "institution_id": inst_id
    }
    response = client.post("/api/v1/classrooms", json=new_classroom, headers=super_admin_token_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == new_classroom["name"]
    assert data["capacity"] == new_classroom["capacity"]
    assert data["room_type_id"] == room_type_id

async def test_get_classroom_by_id(test_db, client, super_admin_token_headers):
    response = client.get("/api/v1/classrooms", headers=super_admin_token_headers)
    if not response.json()["items"]:
        return
    classroom_id = response.json()["items"][0]["id"]
    response = client.get(f"/api/v1/classrooms/{classroom_id}", headers=super_admin_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == classroom_id

async def test_update_classroom(test_db, client, super_admin_token_headers):
    response = client.get("/api/v1/classrooms", headers=super_admin_token_headers)
    if not response.json()["items"]:
        return
    classroom_id = response.json()["items"][0]["id"]
    update_data = {"name": "Updated Room"}
    response = client.put(f"/api/v1/classrooms/{classroom_id}", json=update_data, headers=super_admin_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Room"

async def test_delete_classroom(test_db, client, super_admin_token_headers):
    # Create a new classroom to delete
    inst_resp = client.get("/api/v1/institutions", headers=super_admin_token_headers)
    inst_id = inst_resp.json()["items"][0]["id"]
    room_type = {"name": "Delete Room Type", "institution_id": inst_id}
    rt_resp = client.post("/api/v1/room_types", json=room_type, headers=super_admin_token_headers)
    room_type_id = rt_resp.json()["id"]
    new_classroom = {
        "name": "Delete Room",
        "capacity": 30,
        "room_type_id": room_type_id,
        "institution_id": inst_id
    }
    response = client.post("/api/v1/classrooms", json=new_classroom, headers=super_admin_token_headers)
    classroom_id = response.json()["id"]
    # Delete
    response = client.delete(f"/api/v1/classrooms/{classroom_id}", headers=super_admin_token_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    # Verify deletion
    response = client.get(f"/api/v1/classrooms/{classroom_id}", headers=super_admin_token_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
