from pydantic import BaseModel, Field
from typing import Optional
import uuid

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    institution_id: Optional[uuid.UUID] = None
    exp: int

class LoginRequest(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., example="password123")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str
    user_id: uuid.UUID
    role: str
    institution_id: Optional[uuid.UUID] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str
