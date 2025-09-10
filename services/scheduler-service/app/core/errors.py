from fastapi import HTTPException, status
from typing import Optional


class ServiceException(Exception):
    """Base exception for service errors"""
    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Optional[dict] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)


class DataServiceException(ServiceException):
    """Exception raised when there's an error communicating with data service"""
    pass


class SchedulingException(ServiceException):
    """Exception raised when there's an error in the scheduling algorithm"""
    pass


class ValidationException(ServiceException):
    """Exception raised when there's a validation error in the input data"""
    def __init__(self, message: str, detail: Optional[dict] = None):
        super().__init__(
            message=message, 
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class OptimizationException(ServiceException):
    """Exception raised when the optimization process fails"""
    pass


class ConstraintViolationException(ServiceException):
    """Exception raised when a constraint is violated"""
    def __init__(self, message: str, constraint_type: str, violated_constraints: list):
        detail = {
            "constraint_type": constraint_type,
            "violated_constraints": violated_constraints
        }
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


def http_exception_from_service_error(error: ServiceException) -> HTTPException:
    """Convert a service exception to a FastAPI HTTPException"""
    return HTTPException(
        status_code=error.status_code,
        detail={
            "message": error.message,
            "detail": error.detail
        }
    )
