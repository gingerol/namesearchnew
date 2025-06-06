"""Domain-related Pydantic schemas."""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum

from ..models.domain import TLDType, DomainStatus


class DomainBase(BaseModel):
    """Base domain schema reflecting core identification parts."""
    domain_name_full: str = Field(..., description="Full domain name, e.g., example.com")
    name_part: str = Field(..., description="The part of the domain name before the TLD, e.g., 'example'")
    tld_part: str = Field(..., description="The TLD part of the domain, e.g., 'com' (without the dot)")


class DomainCreate(DomainBase):
    """Schema for creating a new domain record with all necessary fields."""
    # domain_name_full and name_part_length will be derived in CRUD if not provided
    domain_name_full: Optional[str] = Field(None, description="Full domain name, e.g., example.com. Auto-generated if not provided.")
    name_part_length: Optional[int] = Field(None, description="Length of the name_part. Auto-calculated if not provided.")
    tld_type: TLDType = Field(..., description="Type of the TLD (e.g., gTLD, ccTLD)")
    status: DomainStatus = Field(default=DomainStatus.UNKNOWN, description="Current status of the domain")
    is_available: bool = Field(default=False, description="Whether the domain is currently available for registration")
    is_premium: bool = Field(default=False, description="Whether the domain is considered a premium domain")
    price: Optional[float] = Field(None, description="Price of the domain, if applicable")
    currency: Optional[str] = Field(default="USD", description="Currency of the price (e.g., USD, EUR)")
    registered_date: Optional[datetime] = Field(None, description="Date the domain was registered")
    quality_score: Optional[float] = Field(None, description="A generic quality score, 0-100")
    seo_score: Optional[float] = Field(None, description="SEO score, 0-100")
    search_volume: Optional[int] = Field(None, description="Estimated monthly search volume")
    cpc: Optional[float] = Field(None, description="Estimated Cost Per Click")
    language: Optional[str] = Field(None, description="Detected language (e.g., 'en', 'es')")
    whois_data: Optional[Dict[str, Any]] = Field(None, description="Raw WHOIS data as JSON")
    whois_last_updated: Optional[datetime] = Field(None, description="Timestamp of the last WHOIS data update")


class DomainUpdate(BaseModel):
    """Schema for updating an existing domain record. All fields are optional."""
    domain_name_full: Optional[str] = Field(None, description="Full domain name, e.g., example.com")
    name_part: Optional[str] = Field(None, description="The part of the domain name before the TLD, e.g., 'example'")
    tld_part: Optional[str] = Field(None, description="The TLD part of the domain, e.g., 'com' (without the dot)")
    name_part_length: Optional[int] = Field(None, description="Length of the name_part. Should be updated if name_part changes.")
    tld_type: Optional[TLDType] = Field(None, description="Type of the TLD (e.g., gTLD, ccTLD)")
    status: Optional[DomainStatus] = Field(None, description="Current status of the domain")
    is_available: Optional[bool] = Field(None, description="Whether the domain is currently available for registration")
    is_premium: Optional[bool] = Field(None, description="Whether the domain is considered a premium domain")
    price: Optional[float] = Field(None, description="Price of the domain, if applicable")
    currency: Optional[str] = Field(None, description="Currency of the price (e.g., USD, EUR)")
    registered_date: Optional[datetime] = Field(None, description="Date the domain was registered")
    quality_score: Optional[float] = Field(None, description="A generic quality score, 0-100")
    seo_score: Optional[float] = Field(None, description="SEO score, 0-100")
    search_volume: Optional[int] = Field(None, description="Estimated monthly search volume")
    cpc: Optional[float] = Field(None, description="Estimated Cost Per Click")
    language: Optional[str] = Field(None, description="Detected language (e.g., 'en', 'es')")
    whois_data: Optional[Dict[str, Any]] = Field(None, description="Raw WHOIS data as JSON")
    whois_last_updated: Optional[datetime] = Field(None, description="Timestamp of the last WHOIS data update")


class DomainInDBBase(DomainBase):
    """Base schema for domain data retrieved from the database."""
    id: int
    name_part_length: int = Field(..., description="Length of the name_part")
    tld_type: TLDType # In the model, this is not nullable
    status: DomainStatus
    is_premium: bool
    is_available: bool
    price: Optional[float] = None
    currency: Optional[str] = None
    registered_date: Optional[datetime] = None
    quality_score: Optional[float] = None
    seo_score: Optional[float] = None
    search_volume: Optional[int] = None
    cpc: Optional[float] = None
    language: Optional[str] = None
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
    tlds: List[str] = Field(
        default_factory=lambda: ['com', 'io', 'ai', 'co', 'app', 'dev', 'tech', 'net', 'org'],
        description="List of TLDs to check (e.g., ['com', 'io'])"
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of results to return (1-100)"
    )
    check_availability: bool = Field(
        default=True,
        description="Whether to check domain availability (may be slower)"
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


# Schemas for Advanced Domain Search with Filters

class SortOrderEnum(str, Enum):
    ASC = "asc"
    DESC = "desc"


class KeywordMatchType(str, Enum):
    ANY = "any"  # Matches if any of the keywords are present
    ALL = "all"  # Matches if all of the keywords are present
    EXACT = "exact" # Matches if the domain name is an exact match to one of the keywords


class AdvancedDomainSearchRequest(BaseModel):
    """Schema for advanced domain search requests with multiple filters."""
    keywords: Optional[List[str]] = Field(None, description="List of search terms for domain names or keywords related to the domain's content/niche")
    match_type: Optional[KeywordMatchType] = Field(KeywordMatchType.ANY, description="How to match keywords: ANY, ALL, or EXACT. Default is ANY.")
    exclude_keywords: Optional[List[str]] = Field(None, description="List of keywords to exclude from domain names")
    tlds: Optional[List[str]] = Field(None, description="List of TLDs to filter by (e.g., ['com', 'net'], without the dot)")
    tld_types: Optional[List[TLDType]] = Field(None, description="Filter by specific TLD types (e.g., gTLD, ccTLD)")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price for the domain")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price for the domain")
    min_length: Optional[int] = Field(None, ge=1, description="Minimum length of the domain name part (excluding TLD)")
    max_length: Optional[int] = Field(None, ge=1, description="Maximum length of the domain name part (excluding TLD)")

    # Availability filters
    only_available: Optional[bool] = Field(None, description="Filter for domains marked as available")
    only_premium: Optional[bool] = Field(None, description="Filter for domains marked as premium")

    # Domain characteristics
    starts_with: Optional[str] = Field(None, description="Filter for domain names starting with this string")
    ends_with: Optional[str] = Field(None, description="Filter for domain names ending with this string")
    exclude_pattern: Optional[str] = Field(None, description="Pattern or keywords to exclude from domain names")

    # Character types
    allow_numbers: Optional[bool] = Field(None, description="Allow domains containing numbers")
    allow_hyphens: Optional[bool] = Field(None, description="Allow domains containing hyphens")
    allow_special_chars: Optional[bool] = Field(None, description="Allow domains containing special characters (if supported)")

    # Domain quality
    min_quality_score: Optional[float] = Field(None, ge=0, le=100, description="Minimum quality score (e.g., SEO score, custom metric)")
    max_quality_score: Optional[float] = Field(None, ge=0, le=100, description="Maximum quality score")
    min_seo_score: Optional[float] = Field(None, ge=0, le=100, description="Minimum SEO score")
    max_seo_score: Optional[float] = Field(None, ge=0, le=100, description="Maximum SEO score")

    # Registration date
    registered_after: Optional[datetime] = Field(None, description="Filter for domains registered after this date (ISO format)")
    registered_before: Optional[datetime] = Field(None, description="Filter for domains registered before this date (ISO format)")

    # Domain age
    min_age_years: Optional[int] = Field(None, ge=0, description="Minimum age of the domain in years")
    max_age_years: Optional[int] = Field(None, ge=0, description="Maximum age of the domain in years")

    # Popularity
    min_search_volume: Optional[int] = Field(None, ge=0, description="Minimum monthly search volume")
    max_search_volume: Optional[int] = Field(None, ge=0, description="Maximum monthly search volume")
    min_cpc: Optional[float] = Field(None, ge=0, description="Minimum Cost Per Click (CPC) value")
    max_cpc: Optional[float] = Field(None, ge=0, description="Maximum Cost Per Click (CPC) value")

    # Language
    language_codes: Optional[List[str]] = Field(None, description="Filter by domain languages (e.g., ['en', 'es'])")

    # Sorting
    sort_by: Optional[str] = Field(None, description="Field to sort by (e.g., 'price', 'length', 'relevance', 'popularity')")
    sort_order: Optional[SortOrderEnum] = Field(SortOrderEnum.DESC, description="Sort order: 'asc' or 'desc'")

    # Pagination
    page: int = Field(1, ge=1, description="Page number for pagination")
    page_size: int = Field(20, ge=1, le=100, description="Number of results per page")

    @validator('tlds', each_item=True, pre=True, always=True)
    def clean_tld(cls, v):
        if v and isinstance(v, str) and v.startswith('.'):
            return v[1:]
        return v

    class Config:
        schema_extra = {
            "example": {
                "keywords": ["innovate", "ai"],
                "match_type": "all",
                "exclude_keywords": ["data", "cloud"],
                "tlds": ["ai", "com"],
                "tld_types": ["ngtdld", "gtld"],
                "min_price": 100.00,
                "max_price": 1000.00,
                "min_length": 5,
                "max_length": 10,
                "only_available": True,
                "only_premium": False,
                "starts_with": "inno",
                "ends_with": "ai",
                "allow_numbers": True,
                "allow_hyphens": False,
                "min_quality_score": 70,
                "max_quality_score": 95,
                "min_seo_score": 60,
                "max_seo_score": 90,
                "registered_after": "2022-01-01T00:00:00Z",
                "registered_before": "2023-12-31T23:59:59Z",
                "min_age_years": 1,
                "max_age_years": 3,
                "min_search_volume": 1000,
                "max_search_volume": 50000,
                "min_cpc": 0.5,
                "max_cpc": 5.0,
                "language_codes": ["en"],
                "sort_by": "price",
                "sort_order": "asc",
                "page": 1,
                "page_size": 50
            }
        }


class FilteredDomainInfo(BaseModel):
    """Schema for individual domain information in filtered search results."""
    domain_name_full: str = Field(..., description="Full domain name, e.g., 'example.com'")
    name_part: str = Field(..., description="The part of the domain name before the TLD, e.g., 'example'")
    tld_part: str = Field(..., description="The TLD part of the domain, e.g., 'com' (without the dot)")
    name_part_length: int = Field(..., description="Length of the name_part")
    tld_type: TLDType = Field(..., description="Type of the TLD")
    status: DomainStatus = Field(..., description="Current status of the domain")
    is_available: bool = Field(..., description="Whether the domain is available")
    is_premium: bool = Field(..., description="Whether the domain is premium")
    price: Optional[float] = Field(None, description="Price of the domain, if available")
    currency: Optional[str] = Field(None, description="Currency of the price")
    registered_date: Optional[datetime] = Field(None, description="Date the domain was registered")
    quality_score: Optional[float] = Field(None, description="A generic quality score, 0-100")
    seo_score: Optional[float] = Field(None, description="SEO score, 0-100")
    search_volume: Optional[int] = Field(None, description="Estimated monthly search volume")
    cpc: Optional[float] = Field(None, description="Estimated Cost Per Click")
    language: Optional[str] = Field(None, description="Detected language of the domain")

    class Config:
        from_attributes = True # If we map from ORM models
        schema_extra = {
            "example": {
                "domain_name_full": "innovate.ai",
                "name_part": "innovate",
                "tld_part": "ai",
                "price": 499.99,
                "length": 8
            }
        }


class PaginatedFilteredDomainsResponse(BaseModel):
    """Response schema for paginated list of filtered domains."""
    results: List[FilteredDomainInfo] = Field(..., description="List of filtered domain results")
    total_items: int = Field(..., description="Total number of items matching the query")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

    class Config:
        schema_extra = {
            "example": {
                "results": [
                    {
                        "domain_name": "innovate.ai",
                        "name_part": "innovate",
                        "tld_part": "ai",
                        "price": 499.99,
                        "name_part_length": 8,
                        "tld_type": "ngtdld",
                        "status": "available",
                        "is_available": True,
                        "is_premium": True,
                        "currency": "USD",
                        "seo_score": 85.5
                    },
                    {
                        "domain_name_full": "techsolutions.com",
                        "name_part": "techsolutions",
                        "tld_part": "com",
                        "price": 12.99,
                        "name_part_length": 13,
                        "tld_type": "gtld",
                        "status": "registered",
                        "is_available": False,
                        "is_premium": False,
                        "currency": "USD",
                        "seo_score": 70.0
                    }
                ],
                "total_items": 150,
                "page": 1,
                "page_size": 20,
                "total_pages": 8
            }
        }
