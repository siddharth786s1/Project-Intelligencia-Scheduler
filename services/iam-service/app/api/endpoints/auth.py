from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    get_current_user,
    get_current_active_superuser,
    get_current_institution_admin,
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.errors import (
    CredentialsException,
    InvalidCredentialsException,
    UserNotFoundException,
)
from app.db.database import get_db
from app.db.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest
from app.models.user import User

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest, db: AsyncSession = Depends(get_db)
):
    """Authenticate a user and return JWT token."""
    # Get user from database
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(request.email)
    
    # Validate user and password
    if not user or not verify_password(request.password, user.password_hash):
        raise InvalidCredentialsException()
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login time
    await user_repo.update(user.id, {"last_login": datetime.utcnow()})
    
    # Create tokens
    token_data = {
        "sub": user.email,
        "role": user.role.name,
        "institution_id": str(user.institution_id) if user.institution_id else None,
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Return tokens and user info
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=30 * 60,  # 30 minutes in seconds
        refresh_token=refresh_token,
        user_id=user.id,
        role=user.role.name,
        institution_id=user.institution_id,
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    """Refresh an access token using a refresh token."""
    try:
        # Decode refresh token
        payload = decode_token(request.refresh_token)
        email = payload.get("sub")
        
        if not email:
            raise CredentialsException()
        
        # Get user from database
        user_repo = UserRepository(db)
        user = await user_repo.get_by_email(email)
        
        if not user:
            raise UserNotFoundException()
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new tokens
        token_data = {
            "sub": user.email,
            "role": user.role.name,
            "institution_id": str(user.institution_id) if user.institution_id else None,
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Return tokens and user info
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=30 * 60,  # 30 minutes in seconds
            refresh_token=refresh_token,
            user_id=user.id,
            role=user.role.name,
            institution_id=user.institution_id,
        )
    
    except:
        raise CredentialsException()
