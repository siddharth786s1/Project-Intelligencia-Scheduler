import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import get_db
from app.db.database import Base
from app.core.security import create_test_token
import uuid

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_data_service_db"

# Create async test engine
test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Override the get_db dependency
async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
async def test_db():
    # Set testing flag to True
    from app.core.config import settings
    settings.TESTING = True
    
    # Create the test database tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create test data
    async with TestSessionLocal() as session:
        # Create test institution
        test_institution = {
            "id": uuid.uuid4(),
            "name": "Test University",
            "code": "TEST-UNIV",
            "contact_email": "admin@testuniversity.edu",
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }
        
        from app.models.institution import Institution
        db_institution = Institution(**test_institution)
        session.add(db_institution)
        await session.commit()
        await session.refresh(db_institution)
        
        # Create test department
        test_department = {
            "id": uuid.uuid4(),
            "institution_id": db_institution.id,
            "name": "Computer Science",
            "code": "CS",
            "description": "Computer Science and Engineering Department",
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }
        
        from app.models.department import Department
        db_department = Department(**test_department)
        session.add(db_department)
        await session.commit()
    
    yield
    
    # Clean up - drop tables after tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def super_admin_token_headers():
    # Create a token for a super admin user
    token = create_test_token(
        data={
            "sub": "super@example.com",
            "role": "super_admin",
            "institution_id": None
        }
    )
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def institution_admin_token_headers(test_db):
    # Create a token for an institution admin user
    token = create_test_token(
        data={
            "sub": "admin@testuniversity.edu",
            "role": "institution_admin",
            "institution_id": "12345678-1234-1234-1234-123456789012"
        }
    )
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def department_head_token_headers(test_db):
    # Create a token for a department head user
    token = create_test_token(
        data={
            "sub": "head@testuniversity.edu",
            "role": "department_head",
            "institution_id": "12345678-1234-1234-1234-123456789012"
        }
    )
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def faculty_token_headers(test_db):
    # Create a token for a faculty user
    token = create_test_token(
        data={
            "sub": "faculty@testuniversity.edu",
            "role": "faculty",
            "institution_id": "12345678-1234-1234-1234-123456789012"
        }
    )
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_institution_id():
    # Return the UUID of the test institution created in the test_db fixture
    return uuid.UUID("12345678-1234-1234-1234-123456789012")

@pytest.fixture
async def client(test_db):
    # Create an async client for testing
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def create_test_room_type(client, test_institution_id):
    # Create a test room type for classroom tests
    room_type_data = {
        "name": "Lecture Hall",
        "description": "Large room for lectures"
    }
    
    response = await client.post(
        app.url_path_for("create_room_type"),
        json=room_type_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    assert response.status_code == 200
    room_type = response.json()["data"]
    yield room_type["id"]

@pytest.fixture
async def create_test_subject(client, test_institution_id, create_test_department):
    # Create a test subject for faculty tests
    subject_data = {
        "name": "Machine Learning",
        "code": "CS403",
        "description": "Introduction to ML algorithms",
        "credit_hours": 4,
        "lecture_hours_per_week": 3,
        "practical_hours_per_week": 2,
        "department_id": create_test_department
    }
    
    response = await client.post(
        app.url_path_for("create_subject"),
        json=subject_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    assert response.status_code == 200
    subject = response.json()["data"]
    yield subject["id"]

@pytest.fixture
async def create_test_batch(client, test_institution_id, create_test_department):
    # Create a test batch for faculty tests
    batch_data = {
        "name": "CS-2025",
        "year": 2025,
        "semester": 5,
        "capacity": 60,
        "department_id": create_test_department
    }
    
    response = await client.post(
        app.url_path_for("create_batch"),
        json=batch_data,
        headers={"X-Institution-ID": str(test_institution_id)}
    )
    assert response.status_code == 200
    batch = response.json()["data"]
    yield batch["id"]
