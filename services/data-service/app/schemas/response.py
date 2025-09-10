from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict

DataType = TypeVar("DataType")


class ResponseBase(BaseModel):
    message: str


class DataResponse(ResponseBase, Generic[DataType]):
    data: DataType


class PaginatedResponseBase(BaseModel):
    count: int
    page: int
    page_size: int
    pages: int
    

class PaginatedResponse(PaginatedResponseBase, Generic[DataType]):
    items: List[DataType]


class SuccessResponse(ResponseBase):
    pass


class ErrorResponse(ResponseBase):
    error_code: Optional[str] = None
    details: Optional[List[str]] = None
