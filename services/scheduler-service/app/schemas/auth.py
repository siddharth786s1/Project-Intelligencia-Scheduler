from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID


class TokenPayload(BaseModel):
    sub: str
    email: str
    role: str
    tenant_id: str
    institution_id: str
    exp: int


class CurrentUser(BaseModel):
    id: str
    email: str
    role: str
    tenant_id: str
    institution_id: str
