"""Project endpoints."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .... import crud, models
from ....core.security import get_current_active_user
from ....db.session import get_db
from ....schemas.project import (
    Project, ProjectCreate, ProjectUpdate, ProjectStatus,
    ProjectMember, ProjectMemberCreate, ProjectMemberUpdate,
    ProjectStats, ProjectWithStats
)

router = APIRouter()


@router.get("/", response_model=List[Project])
def read_projects(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve projects for the current user.
    """
    # Get both owned projects and projects where user is a member
    owned_projects = crud.project.get_multi_by_owner(
        db, owner_id=current_user.id, skip=skip, limit=limit
    )
    member_projects = crud.project.get_user_projects(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    
    # Merge and deduplicate projects
    project_ids = set()
    projects = []
    
    for project in owned_projects + member_projects:
        if project.id not in project_ids:
            project_ids.add(project.id)
            projects.append(project)
    
    return projects


@router.post("/", response_model=Project)
def create_project(
    *,
    db: Session = Depends(get_db),
    project_in: ProjectCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new project.
    """
    project = crud.project.create_with_owner(
        db=db, obj_in=project_in, owner_id=current_user.id
    )
    return project


@router.get("/{project_id}", response_model=ProjectWithStats)
def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific project by ID.
    """
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user has access to this project
    if project.owner_id != current_user.id and not crud.project.is_member(
        db, project_id=project_id, user_id=current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this project"
        )
    
    # Get project stats
    # TODO: Implement actual stats calculation
    stats = ProjectStats()
    
    return {**project.__dict__, "stats": stats}


@router.put("/{project_id}", response_model=Project)
def update_project(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    project_in: ProjectUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Update a project.
    """
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Only owner can update the project
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can update the project"
        )
    
    project = crud.project.update(db, db_obj=project, obj_in=project_in)
    return project


@router.delete("/{project_id}", response_model=Project)
def delete_project(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a project.
    """
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Only owner can delete the project
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can delete the project"
        )
    
    # Instead of deleting, mark as deleted
    project = crud.project.update(
        db, 
        db_obj=project, 
        obj_in={"status": ProjectStatus.DELETED}
    )
    return project


# Project Members

@router.get("/{project_id}/members", response_model=List[ProjectMember])
def get_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get all members of a project.
    """
    # Check if project exists and user has access
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id and not crud.project.is_member(
        db, project_id=project_id, user_id=current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this project"
        )
    
    # Get members with their user details
    members = crud.project.get_members(db, project_id=project_id)
    return members


@router.post("/{project_id}/members", response_model=ProjectMember)
def add_project_member(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    member_in: ProjectMemberCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Add a member to a project.
    """
    # Check if project exists and user is the owner
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can add members"
        )
    
    # Check if user exists and is not already a member
    user = crud.user.get(db, id=member_in.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if crud.project.is_member(db, project_id=project_id, user_id=member_in.user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this project"
        )
    
    # Add member to project
    member = crud.project.add_member(
        db, project_id=project_id, user_id=member_in.user_id, member_in=member_in
    )
    return member


@router.put("/{project_id}/members/{user_id}", response_model=ProjectMember)
def update_project_member(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    user_id: int,
    member_in: ProjectMemberUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Update a project member's permissions.
    """
    # Check if project exists and user is the owner
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can update member permissions"
        )
    
    # Update member permissions
    member = crud.project.update_member(
        db, project_id=project_id, user_id=user_id, member_in=member_in
    )
    return member


@router.delete("/{project_id}/members/{user_id}", response_model=ProjectMember)
def remove_project_member(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    user_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Remove a member from a project.
    """
    # Check if project exists and user is the owner
    project = crud.project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Allow users to remove themselves from projects
    if project.owner_id != current_user.id and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can remove other members"
        )
    
    # Don't allow removing the owner
    if project.owner_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the project owner"
        )
    
    # Remove member from project
    member = crud.project.remove_member(
        db, project_id=project_id, user_id=user_id
    )
    return member
