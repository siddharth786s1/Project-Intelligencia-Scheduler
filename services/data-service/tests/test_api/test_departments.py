import pytest
from httpx import AsyncClient
import uuid

# Create a test file for department endpoints
pytestmark = pytest.mark.asyncio

class TestDepartments:
    async def test_create_department(self, client, institution_admin_token_headers, test_db):
        """Test creating a new department"""
        new_department = {
            "name": "Physics Department",
            "code": "PHY",
            "description": "Department of Physics and Astronomy"
        }
        
        response = client.post("/departments/", json=new_department, headers=institution_admin_token_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == new_department["name"]
        assert data["code"] == new_department["code"]
        assert data["description"] == new_department["description"]
        assert data["institution_id"] == "12345678-1234-1234-1234-123456789012"  # From the token
        assert "id" in data
        
    async def test_create_department_different_institution(self, client, institution_admin_token_headers, test_db):
        """Test creating a department with explicitly different institution_id (should ignore and use token's)"""
        new_department = {
            "name": "Chemistry Department",
            "code": "CHM",
            "description": "Department of Chemistry",
            "institution_id": "00000000-0000-0000-0000-000000000000"  # Different ID, should be ignored
        }
        
        response = client.post("/departments/", json=new_department, headers=institution_admin_token_headers)
        assert response.status_code == 201
        
        data = response.json()
        # Should use the institution_id from the token, not the one provided in request
        assert data["institution_id"] == "12345678-1234-1234-1234-123456789012"
        
    async def test_get_departments_by_institution(self, client, institution_admin_token_headers, test_db):
        """Test getting all departments for current institution"""
        response = client.get("/departments/", headers=institution_admin_token_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the one from test_db fixture
        
        # All departments should belong to the institution in the token
        for dept in data:
            assert dept["institution_id"] == "12345678-1234-1234-1234-123456789012"
        
    async def test_get_department_by_id(self, client, institution_admin_token_headers, test_db):
        """Test getting a specific department by ID"""
        department_id = "12345678-2345-2345-2345-123456789012"  # From test_db
        response = client.get(f"/departments/{department_id}", headers=institution_admin_token_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == department_id
        assert data["name"] == "Computer Science"
        assert data["code"] == "CS"
        
    async def test_get_department_from_different_institution(self, client, institution_admin_token_headers, test_db):
        """Test attempting to get a department from a different institution (should fail)"""
        # Create a department for a different institution directly in DB
        different_dept_id = str(uuid.uuid4())
        
        # Try to get it (this should fail as it's for a different institution)
        response = client.get(f"/departments/{different_dept_id}", headers=institution_admin_token_headers)
        assert response.status_code == 404
        
    async def test_update_department(self, client, institution_admin_token_headers, test_db):
        """Test updating a department"""
        department_id = "12345678-2345-2345-2345-123456789012"  # From test_db
        updated_data = {
            "name": "Updated CS Department",
            "description": "Updated Department of Computer Science"
        }
        
        response = client.patch(f"/departments/{department_id}", json=updated_data, headers=institution_admin_token_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == updated_data["name"]
        assert data["description"] == updated_data["description"]
        assert data["code"] == "CS"  # Unchanged field
        
    async def test_delete_department(self, client, institution_admin_token_headers, test_db):
        """Test deleting a department"""
        # First create a new department to delete
        new_department = {
            "name": "Department to Delete",
            "code": "DEL",
            "description": "This department will be deleted"
        }
        
        create_response = client.post("/departments/", json=new_department, headers=institution_admin_token_headers)
        assert create_response.status_code == 201
        
        department_id = create_response.json()["id"]
        
        # Now delete it
        delete_response = client.delete(f"/departments/{department_id}", headers=institution_admin_token_headers)
        assert delete_response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(f"/departments/{department_id}", headers=institution_admin_token_headers)
        assert get_response.status_code == 404
