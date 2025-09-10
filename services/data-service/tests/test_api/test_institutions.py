import pytest
from httpx import AsyncClient
import uuid

# Create a test file for institution endpoints
pytestmark = pytest.mark.asyncio

class TestInstitutions:
    async def test_create_institution_super_admin(self, client, super_admin_token_headers, test_db):
        """Test creating a new institution by super admin"""
        new_institution = {
            "name": "New University",
            "code": "NEW-UNI",
            "contact_email": "contact@newuniversity.edu",
            "address": "123 New Street",
            "city": "New City",
            "state": "New State",
            "country": "New Country",
            "postal_code": "12345"
        }
        
        response = client.post("/institutions/", json=new_institution, headers=super_admin_token_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == new_institution["name"]
        assert data["code"] == new_institution["code"]
        assert data["contact_email"] == new_institution["contact_email"]
        assert "id" in data
        
    async def test_create_institution_not_super_admin(self, client, institution_admin_token_headers, test_db):
        """Test creating a new institution by non-super admin (should fail)"""
        new_institution = {
            "name": "Unauthorized University",
            "code": "UNAUTH",
            "contact_email": "contact@unauthorized.edu"
        }
        
        response = client.post("/institutions/", json=new_institution, headers=institution_admin_token_headers)
        assert response.status_code == 403
        
    async def test_get_all_institutions_super_admin(self, client, super_admin_token_headers, test_db):
        """Test getting all institutions by super admin"""
        response = client.get("/institutions/", headers=super_admin_token_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the one from test_db fixture
        
    async def test_get_institution_by_id(self, client, super_admin_token_headers, test_db):
        """Test getting a specific institution by ID"""
        institution_id = "12345678-1234-1234-1234-123456789012"
        response = client.get(f"/institutions/{institution_id}", headers=super_admin_token_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == institution_id
        assert data["name"] == "Test University"
        assert data["code"] == "TEST-UNIV"
        
    async def test_get_nonexistent_institution(self, client, super_admin_token_headers, test_db):
        """Test getting a non-existent institution"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/institutions/{fake_id}", headers=super_admin_token_headers)
        assert response.status_code == 404
        
    async def test_update_institution(self, client, super_admin_token_headers, test_db):
        """Test updating an institution"""
        institution_id = "12345678-1234-1234-1234-123456789012"
        updated_data = {
            "name": "Updated University Name",
            "address": "Updated Address",
            "city": "Updated City"
        }
        
        response = client.patch(f"/institutions/{institution_id}", json=updated_data, headers=super_admin_token_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == updated_data["name"]
        assert data["address"] == updated_data["address"]
        assert data["city"] == updated_data["city"]
        assert data["code"] == "TEST-UNIV"  # Unchanged field
        
    async def test_delete_institution(self, client, super_admin_token_headers, test_db):
        """Test deleting an institution"""
        # First create a new institution to delete
        new_institution = {
            "name": "Delete University",
            "code": "DEL-UNI",
            "contact_email": "delete@university.edu"
        }
        
        create_response = client.post("/institutions/", json=new_institution, headers=super_admin_token_headers)
        assert create_response.status_code == 201
        
        institution_id = create_response.json()["id"]
        
        # Now delete it
        delete_response = client.delete(f"/institutions/{institution_id}", headers=super_admin_token_headers)
        assert delete_response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(f"/institutions/{institution_id}", headers=super_admin_token_headers)
        assert get_response.status_code == 404
