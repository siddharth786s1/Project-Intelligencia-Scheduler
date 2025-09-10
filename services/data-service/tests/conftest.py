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
