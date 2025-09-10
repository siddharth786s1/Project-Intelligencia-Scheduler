import pytest
import json
from httpx import AsyncClient
from fastapi import status
from app.main import app
import uuid

pytestmark = pytest.mark.asyncio

async def test_login_success(test_db, client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@testuniversity.edu", "password": "password"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert "user_id" in data
    assert data["role"] == "institution_admin"
    assert "institution_id" in data

async def test_login_invalid_credentials(test_db, client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@testuniversity.edu", "password": "wrong_password"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data

async def test_login_invalid_email(test_db, client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "password"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data

async def test_refresh_token_success(test_db, client):
    # First login to get a refresh token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@testuniversity.edu", "password": "password"},
    )
    refresh_token = login_response.json()["refresh_token"]
    
    # Then use the refresh token to get a new access token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

async def test_refresh_token_invalid(test_db, client):
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_refresh_token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data
