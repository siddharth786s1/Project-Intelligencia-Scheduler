from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.auth import TokenPayload, CurrentUser


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.AUTH_SERVICE_URL}/auth/login"
)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """
    Validate JWT token and return current user information
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        # Check if token has expired
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Return current user from token payload
    return CurrentUser(
        id=token_data.sub,
        email=token_data.email,
        role=token_data.role,
        tenant_id=token_data.tenant_id,
        institution_id=token_data.institution_id
    )


async def get_current_institution_id(
    current_user: CurrentUser = Depends(get_current_user),
) -> str:
    """
    Get the institution ID of the current user
    """
    return current_user.institution_id


async def verify_admin_access(
    current_user: CurrentUser = Depends(get_current_user),
) -> bool:
    """
    Verify if the current user has admin access
    """
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return True
