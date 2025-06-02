"""Project and workspace models."""
from datetime import datetime
from typing import List, Optional
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean, JSON
from sqlalchemy.orm import relationship

from .base import Base


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ProjectRole(str, Enum):
    """Project member role enumeration."""
    VIEWER = "viewer"  # Can view project content
    EDITOR = "editor"  # Can edit project content
    ADMIN = "admin"    # Can manage project settings and members
    OWNER = "owner"    # Project owner with full permissions


class Project(Base):
    """Project model for organizing domain searches and results."""
    
    __tablename__ = "projects"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Project metadata
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default=ProjectStatus.ACTIVE, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    
    # Project settings
    settings = Column(JSON, nullable=True)  # Store project-specific settings
    
    # Relationships
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("namesearch.models.user.User", back_populates="projects")
    
    # Timestamps
    last_accessed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    searches = relationship("namesearch.models.domain.Search", back_populates="project")
    
    def __repr__(self) -> str:
        return f"<Project {self.name} ({self.status})>"


class ProjectMember(Base):
    """Project members model for collaboration."""
    
    __tablename__ = "project_members"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Permissions
    can_edit = Column(Boolean, default=False, nullable=False)
    can_invite = Column(Boolean, default=False, nullable=False)
    can_manage = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<ProjectMember {self.user_id} in project {self.project_id}>"
