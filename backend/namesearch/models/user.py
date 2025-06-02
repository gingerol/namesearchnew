"""User database model."""
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey, event
from sqlalchemy.orm import relationship, backref

from namesearch.models.base import Base

# Import password functions at the top level
from ..core.password import get_password_hash, verify_password

# Use TYPE_CHECKING for type hints only
if TYPE_CHECKING:
    from .domain_watch import DomainWatch
    from .project import Project
    from .domain import Search, SearchResult


class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships - using string literals with full module paths to avoid circular imports
    projects = relationship("namesearch.models.project.Project", back_populates="owner", cascade="all, delete-orphan", lazy='selectin')
    domain_watches = relationship("namesearch.models.domain_watch.DomainWatch", back_populates="user", cascade="all, delete-orphan", lazy='selectin')
    search_results = relationship("namesearch.models.domain.SearchResult", back_populates="user", lazy='selectin')
    searches = relationship("namesearch.models.domain.Search", back_populates="user", lazy='selectin')
    notifications = relationship("namesearch.models.notification.Notification", back_populates="user", cascade="all, delete-orphan", lazy='selectin')
    
    def set_password(self, password: str) -> None:
        """Set the hashed password."""
        self.hashed_password = get_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return verify_password(password, self.hashed_password)
    
    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"
