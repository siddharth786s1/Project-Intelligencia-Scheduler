from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Annotated, Dict, Any
from uuid import UUID
import jwt

from app.core.config import settings
from app.db.database import get_db


async def get_current_user(token: str) -> Dict[str, Any]:
    """
    Decode JWT token and return user data
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_token_from_header(
    authorization: Annotated[str, Depends(lambda x: x.headers.get("Authorization"))]
) -> Dict[str, Any]:
    """
    Extract token from Authorization header and get current user
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return await get_current_user(token)


DB = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[Dict[str, Any], Depends(get_current_user_token_from_header)]


def get_institution_id_from_token(current_user: CurrentUser) -> Optional[UUID]:
    """
    Extract institution_id from token data
    """
    if "institution_id" in current_user:
        return UUID(current_user["institution_id"])
    return None


async def get_current_institution_id(
    x_institution_id: Annotated[str, Depends(lambda x: x.headers.get("X-Institution-ID"))],
    db: AsyncSession = Depends(get_db)
) -> UUID:
    """
    Extract institution ID from X-Institution-ID header for testing purposes
    or from JWT token in production
    """
    if settings.TESTING and x_institution_id:
        return UUID(x_institution_id)
    
    # In production, we'd get this from the JWT token
    # For now, we're using the header for simplicity in testing
    if not x_institution_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Institution-ID header is required"
        )
    
    return UUID(x_institution_id)


def check_is_super_admin(current_user: CurrentUser) -> bool:
    """
    Check if user is a super admin
    """
    return current_user.get("is_super_admin", False)


def require_super_admin(current_user: CurrentUser) -> None:
    """
    Verify user is a super admin or raise exception
    """
    if not check_is_super_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can perform this action",
        )
