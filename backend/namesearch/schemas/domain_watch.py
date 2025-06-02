"""Pydantic models for Domain Watch functionality."""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, validator

class DomainWatchBase(BaseModel):
    """Base schema for domain watch."""
    domain: str = Field(..., description="Domain name to watch")
    is_active: bool = Field(True, description="Whether the watch is active")
    check_frequency: int = Field(
        60, 
        description="Frequency of checks in minutes",
        ge=5,
        le=1440  # 24 hours
    )
    
    @validator('domain')
    def validate_domain(cls, v):
        """Validate domain format."""
        if not v or len(v) > 253:
            raise ValueError("Invalid domain length")
        if '..' in v or v.startswith('.') or v.endswith('.'):
            raise ValueError("Invalid domain format")
        return v.lower()

class DomainWatchCreate(DomainWatchBase):
    """Schema for creating a new domain watch."""
    pass

class DomainWatchUpdate(DomainWatchBase):
    """Schema for updating a domain watch."""
    is_active: Optional[bool] = None
    check_frequency: Optional[int] = Field(
        None, 
        ge=5,
        le=1440,
        description="Frequency of checks in minutes"
    )

class DomainWatchInDBBase(DomainWatchBase):
    """Base schema for domain watch in database."""
    id: int
    user_id: int
    last_checked: Optional[datetime] = None
    last_status: Optional[str] = None
    whois_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class DomainWatch(DomainWatchInDBBase):
    """Schema for returning domain watch data."""
    pass

class DomainWatchInDB(DomainWatchInDBBase):
    """Schema for domain watch in database (internal use)."""
    pass
