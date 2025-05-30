"""Project-related Pydantic schemas."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

from .user import User, UserResponse
from .domain import DomainPublic


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    is_public: bool = Field(False, description="Whether the project is publicly visible")
    settings: Optional[Dict[str, Any]] = Field(
        None,
        description="Project-specific settings"
    )


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    status: Optional[ProjectStatus] = Field(None, description="Project status")
    is_public: Optional[bool] = Field(None, description="Project visibility")
    settings: Optional[Dict[str, Any]] = Field(
        None,
        description="Project-specific settings"
    )


class ProjectInDBBase(ProjectBase):
    """Base schema for project in database."""
    id: int
    owner_id: int
    status: ProjectStatus = ProjectStatus.ACTIVE
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime

    class Config:
        from_attributes = True


class ProjectInDB(ProjectInDBBase):
    """Project schema for database operations."""
    settings: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ProjectMemberBase(BaseModel):
    """Base schema for project members."""
    can_edit: bool = Field(False, description="Can edit project content")
    can_invite: bool = Field(False, description="Can invite new members")
    can_manage: bool = Field(False, description="Can manage project settings")


class ProjectMemberCreate(ProjectMemberBase):
    """Schema for adding a project member."""
    user_id: int = Field(..., description="User ID to add to the project")


class ProjectMemberUpdate(ProjectMemberBase):
    """Schema for updating project member permissions."""
    pass


class ProjectMember(ProjectMemberBase):
    """Schema for project member with user details."""
    user: User
    joined_at: datetime

    class Config:
        from_attributes = True


class ProjectMemberResponse(ProjectMember):
    """Project member response schema for API responses."""
    user: UserResponse
    
    class Config:
        from_attributes = True


class ProjectResponse(ProjectInDBBase):
    """Project response schema for API responses."""
    owner: User
    members: List[ProjectMember] = []
    domain_count: int = 0
    search_count: int = 0

# Alias for backward compatibility
Project = ProjectResponse


class ProjectStats(BaseModel):
    """Project statistics."""
    total_domains: int = 0
    available_domains: int = 0
    premium_domains: int = 0
    total_searches: int = 0
    member_count: int = 0


class ProjectWithStats(Project):
    """Project schema with detailed statistics."""
    stats: ProjectStats


class ProjectSearchQuery(BaseModel):
    """Schema for searching within a project."""
    query: str = Field(..., description="Search query")
    status: Optional[str] = Field(None, description="Filter by domain status")
    is_available: Optional[bool] = Field(None, description="Filter by availability")
    is_premium: Optional[bool] = Field(None, description="Filter by premium status")
    limit: int = Field(50, ge=1, le=500, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Pagination offset")
