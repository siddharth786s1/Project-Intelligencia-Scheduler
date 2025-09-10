import pytest
import json
from httpx import AsyncClient
from fastapi import status
import uuid

pytestmark = pytest.mark.asyncio

async def test_get_all_users(test_db, client, super_admin_token_headers):
    response = client.get("/api/v1/users", headers=super_admin_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 2  # At least super admin and institution admin
    assert data["total"] >= 2

async def test_get_users_pagination(test_db, client, super_admin_token_headers):
    response = client.get(
        "/api/v1/users?page=1&page_size=1",
        headers=super_admin_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["total"] >= 2
    assert data["page"] == 1
    assert data["page_size"] == 1
    assert data["total_pages"] >= 2

async def test_get_users_by_role(test_db, client, super_admin_token_headers):
    # First get the role_id for super_admin
    response = client.get("/api/v1/roles", headers=super_admin_token_headers)
    roles = response.json()
    super_admin_role_id = next(role["id"] for role in roles if role["name"] == "super_admin")
    
    # Then filter users by that role
    response = client.get(
        f"/api/v1/users?role_id={super_admin_role_id}",
        headers=super_admin_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1
    assert all(user["role"]["name"] == "super_admin" for user in data["items"])

async def test_get_user_by_id(test_db, client, super_admin_token_headers):
    # First get all users
    response = client.get("/api/v1/users", headers=super_admin_token_headers)
    users = response.json()["items"]
    user_id = users[0]["id"]
    
    # Then get specific user
    response = client.get(f"/api/v1/users/{user_id}", headers=super_admin_token_headers)
    assert response.status_code == status.HTTP_200_OK
    user = response.json()
    assert user["id"] == user_id

async def test_get_user_not_found(test_db, client, super_admin_token_headers):
    nonexistent_user_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/users/{nonexistent_user_id}", headers=super_admin_token_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

async def test_create_user(test_db, client, super_admin_token_headers):
    # First get the role_id for faculty
    response = client.get("/api/v1/roles", headers=super_admin_token_headers)
    roles = response.json()
    faculty_role_id = next(role["id"] for role in roles if role["name"] == "faculty")
    
    # Get test institution ID
    response = client.get(
        "/api/v1/users?page=1&page_size=10",
        headers=super_admin_token_headers
    )
    users = response.json()["items"]
    inst_admin = next(user for user in users if user["role"]["name"] == "institution_admin")
    institution_id = inst_admin["institution_id"]
    
    new_user = {
        "email": "faculty1@testuniversity.edu",
        "password": "password123",
        "first_name": "Faculty",
        "last_name": "Member",
        "role_id": faculty_role_id,
        "institution_id": institution_id
    }
    
    response = client.post(
        "/api/v1/users",
        json=new_user,
        headers=super_admin_token_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    created_user = response.json()
    assert created_user["email"] == new_user["email"]
    assert created_user["first_name"] == new_user["first_name"]
    assert created_user["last_name"] == new_user["last_name"]
    assert created_user["role_id"] == new_user["role_id"]
    assert created_user["institution_id"] == new_user["institution_id"]
    assert "id" in created_user
    assert "password_hash" not in created_user  # Should not return password hash

async def test_update_user(test_db, client, super_admin_token_headers):
    # First get a user to update
    response = client.get("/api/v1/users", headers=super_admin_token_headers)
    users = response.json()["items"]
    user = users[0]
    user_id = user["id"]
    
    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }
    
    response = client.put(
        f"/api/v1/users/{user_id}",
        json=update_data,
        headers=super_admin_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    updated_user = response.json()
    assert updated_user["id"] == user_id
    assert updated_user["first_name"] == update_data["first_name"]
    assert updated_user["last_name"] == update_data["last_name"]

async def test_delete_user(test_db, client, super_admin_token_headers):
    # Create a user to delete
    response = client.get("/api/v1/roles", headers=super_admin_token_headers)
    roles = response.json()
    faculty_role_id = next(role["id"] for role in roles if role["name"] == "faculty")
    
    # Get test institution ID
    response = client.get(
        "/api/v1/users?page=1&page_size=10",
        headers=super_admin_token_headers
    )
    users = response.json()["items"]
    inst_admin = next(user for user in users if user["role"]["name"] == "institution_admin")
    institution_id = inst_admin["institution_id"]
    
    new_user = {
        "email": "to-delete@testuniversity.edu",
        "password": "password123",
        "first_name": "To",
        "last_name": "Delete",
        "role_id": faculty_role_id,
        "institution_id": institution_id
    }
    
    response = client.post(
        "/api/v1/users",
        json=new_user,
        headers=super_admin_token_headers
    )
    created_user = response.json()
    user_id = created_user["id"]
    
    # Delete the user
    response = client.delete(
        f"/api/v1/users/{user_id}",
        headers=super_admin_token_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify user is deleted
    response = client.get(
        f"/api/v1/users/{user_id}",
        headers=super_admin_token_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

async def test_unauthorized_access(test_db, client):
    response = client.get("/api/v1/users")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

async def test_institution_admin_scope(test_db, client, inst_admin_token_headers):
    # Institution admin should only see users from their institution
    response = client.get("/api/v1/users", headers=inst_admin_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    for user in data["items"]:
        # Super admin won't have an institution_id, so skip those
        if user["institution_id"] is not None:
            assert user["institution_id"] == json.loads(
                inst_admin_token_headers["Authorization"].split()[1].split(".")[1] + "=="
            )["institution_id"]
