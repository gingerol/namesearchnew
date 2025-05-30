"""Tests for the project CRUD operations."""
import pytest
from sqlalchemy.orm import Session

from namesearch import crud, models, schemas
from namesearch.models.project import ProjectStatus, ProjectRole
from tests.test_utils import random_lower_string, create_test_user


def test_create_project(db: Session, normal_user: models.User) -> None:
    """Test creating a new project."""
    project_data = {
        "name": "Test Project",
        "description": "A test project",
        "is_public": False,
        "status": ProjectStatus.ACTIVE.value
    }
    
    project = crud.project.create_with_owner(
        db, 
        obj_in=schemas.ProjectCreate(**project_data),
        owner_id=normal_user.id
    )
    
    assert project.name == project_data["name"]
    assert project.description == project_data["description"]
    assert project.is_public == project_data["is_public"]
    assert project.status == project_data["status"]
    assert project.owner_id == normal_user.id


def test_get_project(db: Session, normal_user: models.User) -> None:
    """Test getting a project by ID."""
    # Create a test project
    project_data = {
        "name": "Test Project",
        "description": "A test project",
        "is_public": False,
        "status": ProjectStatus.ACTIVE.value
    }
    project = crud.project.create_with_owner(
        db, 
        obj_in=schemas.ProjectCreate(**project_data),
        owner_id=normal_user.id
    )
    
    # Test getting the project by ID
    project_by_id = crud.project.get(db, id=project.id)
    assert project_by_id
    assert project_by_id.name == project.name
    assert project_by_id.id == project.id
    
    # Test getting a non-existent project
    non_existent_project = crud.project.get(db, id=999999)
    assert non_existent_project is None


def test_get_project_by_owner(db: Session, normal_user: models.User) -> None:
    """Test getting projects by owner."""
    # Create some test projects
    for i in range(5):
        project_data = {
            "name": f"Test Project {i}",
            "description": f"A test project {i}",
            "is_public": i % 2 == 0,  # Alternate between public and private
            "status": ProjectStatus.ACTIVE.value
        }
        crud.project.create_with_owner(
            db, 
            obj_in=schemas.ProjectCreate(**project_data),
            owner_id=normal_user.id
        )
    
    # Test getting projects by owner
    projects = crud.project.get_multi_by_owner(
        db, 
        owner_id=normal_user.id,
        skip=0, 
        limit=10
    )
    
    assert len(projects) == 5
    assert all(p.owner_id == normal_user.id for p in projects)


def test_get_public_projects(db: Session, normal_user: models.User) -> None:
    """Test getting public projects."""
    # Create some test projects
    for i in range(5):
        project_data = {
            "name": f"Test Project {i}",
            "description": f"A test project {i}",
            "is_public": i % 2 == 0,  # Alternate between public and private
            "status": ProjectStatus.ACTIVE.value
        }
        crud.project.create_with_owner(
            db, 
            obj_in=schemas.ProjectCreate(**project_data),
            owner_id=normal_user.id
        )
    
    # Test getting public projects
    public_projects = crud.project.get_multi_public(
        db, 
        skip=0, 
        limit=10
    )
    
    assert len(public_projects) == 3  # 3 out of 5 are public
    assert all(p.is_public is True for p in public_projects)


def test_update_project(db: Session, normal_user: models.User) -> None:
    """Test updating a project."""
    # Create a test project
    project_data = {
        "name": "Test Project",
        "description": "A test project",
        "is_public": False,
        "status": ProjectStatus.ACTIVE.value
    }
    project = crud.project.create_with_owner(
        db, 
        obj_in=schemas.ProjectCreate(**project_data),
        owner_id=normal_user.id
    )
    
    # Update the project
    update_data = {
        "name": "Updated Project Name",
        "description": "Updated description",
        "is_public": True,
        "status": ProjectStatus.ARCHIVED.value
    }
    
    updated_project = crud.project.update(
        db, 
        db_obj=project, 
        obj_in=schemas.ProjectUpdate(**update_data)
    )
    
    assert updated_project.name == update_data["name"]
    assert updated_project.description == update_data["description"]
    assert updated_project.is_public == update_data["is_public"]
    assert updated_project.status == update_data["status"]


def test_remove_project(db: Session, normal_user: models.User) -> None:
    """Test removing a project."""
    # Create a test project
    project_data = {
        "name": "Test Project",
        "description": "A test project",
        "is_public": False,
        "status": ProjectStatus.ACTIVE.value
    }
    project = crud.project.create_with_owner(
        db, 
        obj_in=schemas.ProjectCreate(**project_data),
        owner_id=normal_user.id
    )
    
    # Remove the project
    removed_project = crud.project.remove(db, id=project.id)
    
    assert removed_project.id == project.id
    assert removed_project.name == project.name
    
    # Verify the project was removed
    assert crud.project.get(db, id=project.id) is None


def test_add_project_member(db: Session, normal_user: models.User) -> None:
    """Test adding a member to a project."""
    # Create a test project
    project_data = {
        "name": "Test Project",
        "description": "A test project",
        "is_public": False,
        "status": ProjectStatus.ACTIVE.value
    }
    project = crud.project.create_with_owner(
        db, 
        obj_in=schemas.ProjectCreate(**project_data),
        owner_id=normal_user.id
    )
    
    # Create a test user to add as member
    member = create_test_user(db)
    
    # Add member to project
    member_data = {
        "user_id": member.id,
        "role": ProjectRole.EDITOR.value
    }
    
    project_member = crud.project.add_member(
        db, 
        project_id=project.id, 
        user_id=member.id, 
        member_in=schemas.ProjectMemberCreate(**member_data)
    )
    
    assert project_member.project_id == project.id
    assert project_member.user_id == member.id
    assert project_member.role == member_data["role"]
    
    # Verify the member was added to the project
    assert crud.project.is_member(db, project_id=project.id, user_id=member.id) is True


def test_update_project_member(db: Session, normal_user: models.User) -> None:
    """Test updating a project member's role."""
    # Create a test project
    project_data = {
        "name": "Test Project",
        "description": "A test project",
        "is_public": False,
        "status": ProjectStatus.ACTIVE.value
    }
    project = crud.project.create_with_owner(
        db, 
        obj_in=schemas.ProjectCreate(**project_data),
        owner_id=normal_user.id
    )
    
    # Create a test user to add as member
    member = create_test_user(db)
    
    # Add member to project as VIEWER
    member_data = {
        "user_id": member.id,
        "role": ProjectRole.VIEWER.value
    }
    project_member = crud.project.add_member(
        db, 
        project_id=project.id, 
        user_id=member.id, 
        member_in=schemas.ProjectMemberCreate(**member_data)
    )
    
    # Update member role to EDITOR
    update_data = {
        "role": ProjectRole.EDITOR.value
    }
    
    updated_member = crud.project.update_member(
        db, 
        project_id=project.id, 
        user_id=member.id, 
        member_in=schemas.ProjectMemberUpdate(**update_data)
    )
    
    assert updated_member.role == update_data["role"]
    
    # Verify the member's role was updated
    member_role = crud.project.get_member_role(db, project_id=project.id, user_id=member.id)
    assert member_role == update_data["role"]


def test_remove_project_member(db: Session, normal_user: models.User) -> None:
    """Test removing a member from a project."""
    # Create a test project
    project_data = {
        "name": "Test Project",
        "description": "A test project",
        "is_public": False,
        "status": ProjectStatus.ACTIVE.value
    }
    project = crud.project.create_with_owner(
        db, 
        obj_in=schemas.ProjectCreate(**project_data),
        owner_id=normal_user.id
    )
    
    # Create a test user to add as member
    member = create_test_user(db)
    
    # Add member to project
    member_data = {
        "user_id": member.id,
        "role": ProjectRole.VIEWER.value
    }
    project_member = crud.project.add_member(
        db, 
        project_id=project.id, 
        user_id=member.id, 
        member_in=schemas.ProjectMemberCreate(**member_data)
    )
    
    # Remove member from project
    removed_member = crud.project.remove_member(
        db, 
        project_id=project.id, 
        user_id=member.id
    )
    
    assert removed_member.project_id == project.id
    assert removed_member.user_id == member.id
    
    # Verify the member was removed from the project
    assert crud.project.is_member(db, project_id=project.id, user_id=member.id) is False
