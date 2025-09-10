from typing import Generic, TypeVar, List, Dict, Any, Optional
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")

class ResponseBase(BaseModel):
    success: bool = True
    message: Optional[str] = None

class DataResponse(ResponseBase, Generic[T]):
    data: T

class PaginatedResponse(GenericModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    details: Optional[Dict[str, Any]] = None
