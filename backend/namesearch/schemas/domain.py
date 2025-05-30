"""Domain-related Pydantic schemas."""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum

from ..models.domain import TLDType, DomainStatus


class DomainBase(BaseModel):
    """Base domain schema."""
    name: str = Field(..., description="Domain name (without TLD)")
    tld: str = Field(..., description="Top-level domain (e.g., 'com', 'io')")


class DomainCreate(DomainBase):
    """Schema for creating a new domain record."""
    tld_type: TLDType = Field(..., description="Type of the TLD (e.g., gTLD, ccTLD)")
    is_available: bool = False
    status: DomainStatus = DomainStatus.UNKNOWN


class DomainUpdate(BaseModel):
    """Schema for updating a domain record."""
    status: Optional[DomainStatus] = None
    is_premium: Optional[bool] = None
    is_available: Optional[bool] = None
    whois_data: Optional[Dict[str, Any]] = None


class DomainInDBBase(DomainBase):
    """Base schema for domain in database."""
    id: int
    tld_type: Optional[TLDType] = None
    status: DomainStatus = DomainStatus.UNKNOWN
    is_premium: bool = False
    is_available: bool = False
    whois_last_updated: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DomainInDB(DomainInDBBase):
    """Schema for domain in database with WHOIS data."""
    whois_data: Optional[Dict[str, Any]] = None


class DomainResponse(DomainInDBBase):
    """Domain response schema for API responses."""
    pass

# Alias for backward compatibility
DomainPublic = DomainResponse


class DomainSearchQuery(BaseModel):
    """Schema for domain search query."""
    query: str = Field(..., description="Domain name or keyword to search")
    tlds: Optional[List[str]] = Field(
        default=None,
        description="List of TLDs to check (default: ['.com', '.io', etc.])"
    )
    check_availability: bool = Field(
        default=True,
        description="Whether to check domain availability"
    )
    include_whois: bool = Field(
        default=False,
        description="Whether to include WHOIS data in the response"
    )




class DomainSearchResult(BaseModel):
    """Schema for domain search result."""
    domain: str
    tld: str
    is_available: bool
    status: DomainStatus
    is_premium: bool = False
    price: Optional[float] = None
    currency: str = "USD"
    whois_data: Optional[Dict[str, Any]] = None


class DomainBulkSearchResponse(BaseModel):
    """Response schema for bulk domain search."""
    results: List[DomainSearchResult]
    total: int
    available: int
    taken: int
    premium: int
