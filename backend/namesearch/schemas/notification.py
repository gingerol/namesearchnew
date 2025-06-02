"""Pydantic models for notifications."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

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

class NotificationBase(BaseModel):
    """Base notification schema."""
    type: NotificationType
    title: str = Field(..., max_length=255)
    message: str
    data: Dict[str, Any] = {}

class NotificationCreate(NotificationBase):
    """Schema for creating a new notification."""
    user_id: int
    status: NotificationStatus = NotificationStatus.PENDING

class NotificationUpdate(BaseModel):
    """Schema for updating a notification."""
    status: Optional[NotificationStatus] = None
    read: Optional[bool] = None

class NotificationInDBBase(NotificationBase):
    """Base schema for notification in database."""
    id: int
    user_id: int
    status: NotificationStatus
    created_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class Notification(NotificationInDBBase):
    """Notification schema for API responses."""
    pass

class NotificationInDB(NotificationInDBBase):
    """Notification schema for internal use."""
    pass

class NotificationPreferences(BaseModel):
    """Schema for user notification preferences."""
    email_enabled: bool = True
    in_app_enabled: bool = True
    email_frequency: str = "immediate"  # immediate, daily_digest, weekly_digest
    notify_on_available: bool = True
    notify_on_expiring: bool = True
    notify_on_changed: bool = True
    notify_on_expired: bool = True
    notify_on_transferred: bool = True
    expiration_reminder_days: List[int] = [30, 7, 1]

class NotificationPreferencesUpdate(NotificationPreferences):
    """Schema for updating notification preferences."""
    email_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    email_frequency: Optional[str] = None
    notify_on_available: Optional[bool] = None
    notify_on_expiring: Optional[bool] = None
    notify_on_changed: Optional[bool] = None
    notify_on_expired: Optional[bool] = None
    notify_on_transferred: Optional[bool] = None
    expiration_reminder_days: Optional[List[int]] = None
