from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import DB, CurrentUser, get_institution_id_from_token
from app.core.errors import EntityNotFound
from app.db.database import get_db
from app.schemas.response import PaginatedResponse, SuccessResponse
