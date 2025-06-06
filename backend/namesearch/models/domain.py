"""Domain and search result models."""
from datetime import datetime
from typing import List, Optional
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, JSON, Boolean, Enum as SQLEnum, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class TLDType(str, Enum):
    """TLD type enumeration."""
    GTLD = "gtld"  # Generic TLD (.com, .org, .net)
    CCTLD = "cctld"  # Country code TLD (.uk, .de, .jp)
    GECCTLD = "gecctld"  # Geo-Targeted ccTLD (.io, .co, .me)
    NGTDLD = "ngtdld"  # New gTLD (.app, .dev, .ai)
    INFRASTRUCTURE = "infrastructure"  # Infrastructure TLD (.arpa)


class DomainStatus(str, Enum):
    """Domain status enumeration."""
    AVAILABLE = "available"
    REGISTERED = "registered"
    RESERVED = "reserved"
    PREMIUM = "premium"
    UNKNOWN = "unknown"


class SearchStatus(str, Enum):
    """Search status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class Domain(Base):
    """Domain model for storing domain information."""
    
    __tablename__ = "domains"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Domain identification
    domain_name_full = Column(String(255), unique=True, index=True, nullable=False, comment="Full domain name, e.g., example.com")
    name_part = Column(String(190), index=True, nullable=False, comment="The part of the domain name before the TLD, e.g., 'example'") # Max length of domain label is 63, but keep it reasonable for most cases. Sum of labels + dots <= 253.
    tld_part = Column(String(63), index=True, nullable=False, comment="The TLD part of the domain, e.g., 'com' (without the dot)")
    name_part_length = Column(Integer, index=True, nullable=False, comment="Length of the name_part")
    tld_type = Column(SQLEnum(TLDType), nullable=False, index=True)
    
    # Domain status
    status = Column(SQLEnum(DomainStatus), default=DomainStatus.UNKNOWN, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    is_available = Column(Boolean, default=False, nullable=False)
    
    # Pricing
    price = Column(Float, nullable=True, index=True, comment="Price of the domain, if applicable")
    currency = Column(String(10), default="USD", nullable=True, comment="Currency of the price (e.g., USD, EUR)")

    # Dates & Age
    registered_date = Column(DateTime, nullable=True, index=True, comment="Date the domain was registered")
    # expiration_date can be derived from WHOIS or stored if frequently needed for filtering

    # Metrics & Scores
    quality_score = Column(Float, nullable=True, index=True, comment="A generic quality score, 0-100")
    seo_score = Column(Float, nullable=True, index=True, comment="SEO score, 0-100")
    search_volume = Column(Integer, nullable=True, index=True, comment="Estimated monthly search volume")
    cpc = Column(Float, nullable=True, index=True, comment="Estimated Cost Per Click")

    # Language
    language = Column(String(10), nullable=True, index=True, comment="Detected language of the domain content or target audience (e.g., 'en', 'es')")

    # WHOIS data
    whois_data = Column(JSON, nullable=True)
    whois_last_updated = Column(DateTime, nullable=True)
    
    # Relationships
    searches = relationship("namesearch.models.domain.SearchResult", back_populates="domain")
    
    def __repr__(self) -> str:
        return f"<Domain {self.domain_name_full}>"


class SearchResult(Base):
    """Search result model linking users, searches, and domains."""
    
    __tablename__ = "search_results"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    search_id = Column(Integer, ForeignKey("searches.id"), nullable=False)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    
    # Result data
    is_favorite = Column(Boolean, default=False, nullable=False)
    notes = Column(String(1000), nullable=True)
    
    # Relationships
    user = relationship("namesearch.models.user.User", back_populates="search_results")
    search = relationship("namesearch.models.domain.Search", back_populates="results")
    domain = relationship("namesearch.models.domain.Domain", back_populates="searches")
    
    def __repr__(self) -> str:
        return f"<SearchResult {self.id} for {self.domain.name}>"


class Search(Base):
    """Search model for tracking domain searches."""
    
    __tablename__ = "searches"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Search metadata
    query = Column(String(255), nullable=False)
    search_type = Column(String(50), nullable=False)  # e.g., 'exact', 'suggestion', 'bulk'
    status = Column(SQLEnum(SearchStatus), default=SearchStatus.PENDING, nullable=False)
    results_count = Column(Integer, default=0, nullable=False)
    available_count = Column(Integer, default=0, nullable=False)
    taken_count = Column(Integer, default=0, nullable=False)
    premium_count = Column(Integer, default=0, nullable=False)
    filters = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, server_default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for anonymous searches
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)  # Optional project association
    
    # Relationships
    user = relationship("namesearch.models.user.User", back_populates="searches")
    project = relationship("namesearch.models.project.Project", back_populates="searches")
    results = relationship("namesearch.models.domain.SearchResult", back_populates="search")
    
    def __repr__(self) -> str:
        return f"<Search {self.id} for '{self.query}'>"
