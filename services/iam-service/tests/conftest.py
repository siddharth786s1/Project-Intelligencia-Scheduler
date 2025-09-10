import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import get_db
from app.db.database import Base
from app.models.user import User
from app.models.role import Role
from app.models.tenant import Institution
import uuid

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_iam_db"

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
        # Create roles
        super_admin_role = Role(
            name="super_admin",
            description="Super Administrator with full system access"
        )
        institution_admin_role = Role(
            name="institution_admin",
            description="Institution Administrator"
        )
        department_head_role = Role(
            name="department_head",
            description="Head of Department"
        )
        faculty_role = Role(
            name="faculty",
            description="Faculty Member"
        )
        
        session.add(super_admin_role)
        session.add(institution_admin_role)
        session.add(department_head_role)
        session.add(faculty_role)
        await session.commit()
        
        # Create test institution
        test_institution = Institution(
            name="Test University",
            code="TEST-UNIV",
            contact_email="admin@testuniversity.edu"
        )
        session.add(test_institution)
        await session.commit()
        
        # Refresh to get IDs
        await session.refresh(super_admin_role)
        await session.refresh(institution_admin_role)
        await session.refresh(test_institution)
        
        # Create test users
        super_admin = User(
            email="super@example.com",
            password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
            first_name="Super",
            last_name="Admin",
            role_id=super_admin_role.id
        )
        
        inst_admin = User(
            email="admin@testuniversity.edu",
            password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
            first_name="Inst",
            last_name="Admin",
            role_id=institution_admin_role.id,
            institution_id=test_institution.id
        )
        
        session.add(super_admin)
        session.add(inst_admin)
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
    return {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJzdXBlckBleGFtcGxlLmNvbSIsInJvbGUiOiJzdXBlcl9hZG1pbiIsImluc3RpdHV0aW9uX2lkIjpudWxsLCJleHAiOjIxNDc0ODM2NDd9.fake_token_for_testing"}

@pytest.fixture
def inst_admin_token_headers(test_db):
    return {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbkB0ZXN0dW5pdmVyc2l0eS5lZHUiLCJyb2xlIjoiaW5zdGl0dXRpb25fYWRtaW4iLCJpbnN0aXR1dGlvbl9pZCI6IjEyMzQ1Njc4LTEyMzQtMTIzNC0xMjM0LTEyMzQ1Njc4OTAxMiIsImV4cCI6MjE0NzQ4MzY0N30.fake_token_for_testing_inst_admin"}
