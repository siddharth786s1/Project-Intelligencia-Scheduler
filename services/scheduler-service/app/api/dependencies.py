from fastapi import Depends, Request
from typing import AsyncGenerator, Optional

import httpx
from httpx import AsyncClient, Response
from uuid import UUID

from app.core.security import get_current_user, get_current_institution_id
from app.core.config import settings
from app.core.errors import DataServiceException
from app.schemas.auth import CurrentUser


async def get_data_service_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Dependency for getting a data service HTTP client
    """
    async with httpx.AsyncClient(base_url=settings.DATA_SERVICE_URL) as client:
        yield client


async def forward_auth_header(request: Request) -> dict:
    """
    Extract the Authorization header from the original request to forward to other services
    """
    auth_header = request.headers.get("Authorization")
    if auth_header:
        return {"Authorization": auth_header}
    return {}


async def fetch_data_from_service(
    client: AsyncClient, 
    endpoint: str, 
    headers: dict,
    params: Optional[dict] = None,
    method: str = "GET",
    json_data: Optional[dict] = None
) -> dict:
    """
    Helper function to fetch data from the data service with error handling
    """
    try:
        if method == "GET":
            response = await client.get(endpoint, headers=headers, params=params)
        elif method == "POST":
            response = await client.post(endpoint, headers=headers, json=json_data)
        elif method == "PUT":
            response = await client.put(endpoint, headers=headers, json=json_data)
        elif method == "DELETE":
            response = await client.delete(endpoint, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        raise DataServiceException(
            message=f"Error fetching data from service: {exc.response.text}",
            status_code=exc.response.status_code
        )
    except httpx.RequestError as exc:
        raise DataServiceException(
            message=f"Network error when communicating with service: {str(exc)}"
        )
