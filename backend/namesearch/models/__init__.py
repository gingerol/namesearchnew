"""Database models for the application."""
import logging
import sys
from typing import List, Type, Any, TYPE_CHECKING

# Configure logging
logger = logging.getLogger(__name__)


# Import base first - this must come before any model imports
from .base import Base

# Import enums first
from .domain import TLDType, DomainStatus, SearchStatus

# Then import models without relationships
from .domain import Domain, Search, SearchResult
from .notification import Notification, NotificationType, NotificationStatus

# Then import User model
from .user import User

# Then import models that depend on User
from .project import Project, ProjectMember, ProjectStatus, ProjectRole
from .domain_watch import DomainWatch

# Configure mappers after all models are imported
try:
    from sqlalchemy.orm import configure_mappers
    
    # Configure mappers
    configure_mappers()
    logger.info("SQLAlchemy mappers configured successfully")
except Exception as e:
    logger.error("Error configuring mappers: %s", e, exc_info=True)
    # Re-raise the exception to prevent the app from starting with invalid mappers
    raise

# Define __all__ for explicit exports
__all__: List[str] = [
    # Base
    'Base',
    
    # User models
    'User',
    
    # Domain models
    'Domain',
    'DomainWatch',
    'Search',
    'SearchResult',
    'TLDType',
    'DomainStatus',
    'SearchStatus',
    
    # Project models
    'Project',
    'ProjectMember',
    'ProjectStatus',
    'ProjectRole',
]
