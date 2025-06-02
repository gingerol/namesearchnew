"""Database models for domain watching functionality."""
from datetime import datetime
from typing import Dict, Any, Optional, TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base

class DomainWatch(Base):
    """Model for tracking domain availability changes."""
    __tablename__ = "domain_watches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    domain = Column(String(255), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    check_frequency = Column(Integer, default=60, nullable=False)  # in minutes
    last_checked = Column(DateTime, nullable=True)
    last_status = Column(String(20), nullable=True)  # 'available', 'taken', 'unknown'
    whois_data = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("namesearch.models.user.User", back_populates="domain_watches")
    
    def __repr__(self) -> str:
        return f"<DomainWatch {self.domain} (User {self.user_id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "domain": self.domain,
            "is_active": self.is_active,
            "check_frequency": self.check_frequency,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "last_status": self.last_status,
            "whois_data": self.whois_data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
