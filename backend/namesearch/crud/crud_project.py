"""CRUD operations for projects."""
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from ..models.project import Project, ProjectMember
from ..models.user import User
from .base import CRUDBase
from ..schemas.project import (
    ProjectCreate, 
    ProjectUpdate, 
    ProjectMemberCreate, 
    ProjectMemberUpdate
)


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    """CRUD operations for projects with additional project-specific methods."""
    
    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        """Get projects by owner ID."""
        return (
            db.query(Project)
            .filter(Project.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_user_projects(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        """Get all projects where the user is a member."""
        return (
            db.query(Project)
            .join(Project.members)
            .filter(ProjectMember.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_with_owner(
        self, db: Session, *, obj_in: ProjectCreate, owner_id: int
    ) -> Project:
        """Create a new project with an owner."""
        db_obj = Project(
            **obj_in.dict(exclude_unset=True),
            owner_id=owner_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def add_member(
        self, 
        db: Session, 
        *, 
        project_id: int, 
        user_id: int, 
        member_in: ProjectMemberCreate
    ) -> ProjectMember:
        """Add a member to a project."""
        db_obj = ProjectMember(
            **member_in.dict(),
            project_id=project_id,
            user_id=user_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_member(
        self, 
        db: Session, 
        *, 
        project_id: int, 
        user_id: int, 
        member_in: Union[ProjectMemberUpdate, Dict[str, Any]]
    ) -> ProjectMember:
        """Update a project member's permissions."""
        db_obj = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
            .first()
        )
        
        if not db_obj:
            raise ValueError("Project member not found")
        
        if isinstance(member_in, dict):
            update_data = member_in
        else:
            update_data = member_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove_member(self, db: Session, *, project_id: int, user_id: int) -> ProjectMember:
        """Remove a member from a project."""
        db_obj = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
            .first()
        )
        
        if not db_obj:
            raise ValueError("Project member not found")
        
        db.delete(db_obj)
        db.commit()
        return db_obj
    
    def get_members(
        self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Get all members of a project."""
        return (
            db.query(User)
            .join(ProjectMember, User.id == ProjectMember.user_id)
            .filter(ProjectMember.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def is_member(
        self, db: Session, *, project_id: int, user_id: int
    ) -> bool:
        """Check if a user is a member of a project."""
        return (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
            .first()
            is not None
        )


# Create a singleton instance
project = CRUDProject(Project)
