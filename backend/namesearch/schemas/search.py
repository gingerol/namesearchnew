"""Search-related Pydantic schemas."""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field, HttpUrl

from .domain import DomainResponse
from .user import UserResponse


class SearchStatus(str, Enum):
    """Search status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

class SearchBase(BaseModel):
    """Base search schema."""
    query: str = Field(..., description="Search query string")
    search_type: str = Field("exact", description="Type of search (exact, suggestion, bulk)")
    status: SearchStatus = Field(SearchStatus.PENDING, description="Current status of the search")
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Search filters"
    )
    error: Optional[str] = Field(None, description="Error message if search failed")

class SearchCreate(SearchBase):
    """Schema for creating a new search."""
    user_id: Optional[int] = Field(
        None, 
        description="ID of the user who performed the search"
    )


class SearchUpdate(BaseModel):
    """Schema for updating a search."""
    status: Optional[SearchStatus] = None
    error: Optional[str] = None
    results_count: Optional[int] = None
    available_count: Optional[int] = None
    taken_count: Optional[int] = None
    premium_count: Optional[int] = None
    completed_at: Optional[datetime] = None

class SearchInDBBase(SearchBase):
    """Base search schema for database operations."""
    id: int
    user_id: Optional[int] = None
    project_id: Optional[int] = None
    results_count: int = 0
    available_count: int = 0
    taken_count: int = 0
    premium_count: int = 0
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SearchInDB(SearchInDBBase):
    """Search schema for database operations."""
    pass


class SearchResponse(SearchInDBBase):
    """Search response schema for API responses."""
    user: Optional[UserResponse] = None
    project: Optional[Any] = None  # Avoid circular import
    
    class Config:
        from_attributes = True


class SearchResultBase(BaseModel):
    """Base search result schema."""
    is_favorite: bool = False
    notes: Optional[str] = None


class SearchResultCreate(SearchResultBase):
    """Schema for creating a new search result."""
    search_id: int
    domain_id: int


class SearchResultUpdate(SearchResultBase):
    """Schema for updating a search result."""
    pass


class SearchResultInDBBase(SearchResultBase):
    """Base schema for search result in database."""
    id: int
    search_id: int
    domain_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SearchResultResponse(SearchResultInDBBase):
    """Search result response schema for API responses."""
    domain: DomainResponse
    
    class Config:
        from_attributes = True


# Aliases for backward compatibility
Search = SearchResponse
SearchResult = SearchResultResponse
SearchResults = List[SearchResultResponse]

class SearchHistory(BaseModel):
    """Search history response schema."""
    searches: List[SearchResponse]
    total: int
    skip: int
    limit: int


class SearchStats(BaseModel):
    """Search statistics."""
    total_searches: int = 0
    completed_searches: int = 0
    failed_searches: int = 0
    total_domains_found: int = 0
    available_domains: int = 0
    premium_domains: int = 0
    searches_by_type: Dict[str, int] = {}
    searches_by_status: Dict[str, int] = {}
