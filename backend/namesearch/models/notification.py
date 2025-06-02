"""Notification models for domain monitoring."""
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from namesearch.models.base import Base

class NotificationType(str, Enum):
    """Types of notifications that can be sent."""
    DOMAIN_AVAILABLE = "domain_available"
    DOMAIN_EXPIRING = "domain_expiring"
    DOMAIN_CHANGED = "domain_changed"
    DOMAIN_EXPIRED = "domain_expired"
    DOMAIN_TRANSFERRED = "domain_transferred"

class NotificationStatus(str, Enum):
    """Status of a notification."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"

class Notification(Base):
    """Model for storing notifications."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(SQLEnum(NotificationType), nullable=False)
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING, nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, default={}, nullable=False)  # Additional context data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.id} - {self.type} - {self.status}>"
