"""Standard API response formatting utilities."""
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field
from fastapi import status
from fastapi.responses import JSONResponse

# Generic type for response data
T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    """Standard response model for API endpoints."""
    success: bool = Field(..., description="Indicates if the request was successful")
    data: Optional[T] = Field(None, description="Response data")
    error: Optional[Dict[str, Any]] = Field(
        None, 
        description="Error details if the request failed"
    )
    meta: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional metadata about the response"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"key": "value"},
                "error": None,
                "meta": {"count": 1, "page": 1, "total_pages": 1}
            }
        }


class PaginatedResponse(ResponseModel[T]):
    """Response model for paginated data."""
    meta: Dict[str, Any] = Field(
        ...,
        description="Pagination metadata"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}],
                "error": None,
                "meta": {
                    "page": 1,
                    "page_size": 10,
                    "total_items": 2,
                    "total_pages": 1,
                    "has_next": False,
                    "has_previous": False
                }
            }
        }


def create_response(
    data: Any = None,
    status_code: int = status.HTTP_200_OK,
    success: bool = True,
    error: Optional[Union[Dict[str, Any], str, Exception]] = None,
    meta: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> JSONResponse:
    """
    Create a standardized JSON response.
    
    Args:
        data: The response data.
        status_code: HTTP status code.
        success: Whether the request was successful.
        error: Error details if the request failed.
        meta: Additional metadata about the response.
        headers: Additional headers to include in the response.
        
    Returns:
        JSONResponse: A FastAPI JSONResponse with the standardized format.
    """
    # Format error if it's an exception
    if isinstance(error, Exception):
        error = {
            "type": error.__class__.__name__,
            "detail": str(error),
        }
    elif isinstance(error, str):
        error = {"message": error}
    
    # Create response data
    response_data = ResponseModel(
        success=success,
        data=data,
        error=error,
        meta=meta or {}
    )
    
    # Set default headers if not provided
    if headers is None:
        headers = {}
    
    # Add CORS headers if not already set
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }
    
    # Only add CORS headers if they're not already set
    for key, value in cors_headers.items():
        if key not in headers:
            headers[key] = value
    
    return JSONResponse(
        content=response_data.dict(exclude_none=True),
        status_code=status_code,
        headers=headers,
    )


def success_response(
    data: Any = None,
    status_code: int = status.HTTP_200_OK,
    meta: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> JSONResponse:
    """
    Create a successful response.
    
    Args:
        data: The response data.
        status_code: HTTP status code (default: 200).
        meta: Additional metadata.
        headers: Additional headers.
        
    Returns:
        JSONResponse: A successful JSON response.
    """
    return create_response(
        data=data,
        status_code=status_code,
        success=True,
        meta=meta,
        headers=headers,
    )


def error_response(
    error: Union[Dict[str, Any], str, Exception],
    status_code: int = status.HTTP_400_BAD_REQUEST,
    data: Any = None,
    meta: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> JSONResponse:
    """
    Create an error response.
    
    Args:
        error: Error details.
        status_code: HTTP status code (default: 400).
        data: Optional additional data.
        meta: Additional metadata.
        headers: Additional headers.
        
    Returns:
        JSONResponse: An error JSON response.
    """
    return create_response(
        data=data,
        status_code=status_code,
        success=False,
        error=error,
        meta=meta,
        headers=headers,
    )


def not_found_response(
    item: str = "Resource",
    headers: Optional[Dict[str, str]] = None,
) -> JSONResponse:
    """
    Create a 404 Not Found response.
    
    Args:
        item: The name of the item that wasn't found.
        headers: Additional headers.
        
    Returns:
        JSONResponse: A 404 error response.
    """
    return error_response(
        error={"message": f"{item} not found"},
        status_code=status.HTTP_404_NOT_FOUND,
        headers=headers,
    )


def unauthorized_response(
    detail: str = "Not authenticated",
    headers: Optional[Dict[str, str]] = None,
) -> JSONResponse:
    """
    Create a 401 Unauthorized response.
    
    Args:
        detail: Error detail message.
        headers: Additional headers.
        
    Returns:
        JSONResponse: A 401 error response.
    """
    if headers is None:
        headers = {}
    headers["WWW-Authenticate"] = "Bearer"
    
    return error_response(
        error={"message": detail},
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers=headers,
    )


def forbidden_response(
    detail: str = "Insufficient permissions",
    headers: Optional[Dict[str, str]] = None,
) -> JSONResponse:
    """
    Create a 403 Forbidden response.
    
    Args:
        detail: Error detail message.
        headers: Additional headers.
        
    Returns:
        JSONResponse: A 403 error response.
    """
    return error_response(
        error={"message": detail},
        status_code=status.HTTP_403_FORBIDDEN,
        headers=headers,
    )


def validation_error_response(
    errors: List[Dict[str, Any]],
    status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
    headers: Optional[Dict[str, str]] = None,
) -> JSONResponse:
    """
    Create a validation error response.
    
    Args:
        errors: List of validation errors.
        status_code: HTTP status code (default: 422).
        headers: Additional headers.
        
    Returns:
        JSONResponse: A validation error response.
    """
    return error_response(
        error={
            "message": "Validation error",
            "errors": errors,
        },
        status_code=status_code,
        headers=headers,
    )


def paginated_response(
    items: List[Any],
    total_items: int,
    page: int,
    page_size: int,
    **kwargs: Any,
) -> JSONResponse:
    """
    Create a paginated response.
    
    Args:
        items: List of items for the current page.
        total_items: Total number of items across all pages.
        page: Current page number (1-based).
        page_size: Number of items per page.
        **kwargs: Additional metadata to include.
        
    Returns:
        JSONResponse: A paginated response.
    """
    total_pages = (total_items + page_size - 1) // page_size if page_size > 0 else 1
    
    meta = {
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
        **kwargs,
    }
    
    return success_response(
        data=items,
        meta=meta,
    )
