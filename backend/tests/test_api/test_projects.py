"""Tests for the project endpoints."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from namesearch.models import User, Project, ProjectMember, ProjectRole, ProjectStatus


class TestProjectsAPI:
    """Test projects API endpoints."""

    def test_create_project(self, client: TestClient, normal_user_token_headers: dict, db: Session):
        """Test creating a new project."""
        project_data = {
            "name": "Test Project",
            "description": "A test project",
            "is_public": False
        }
        
        response = client.post(
            "/api/v1/projects/",
            headers=normal_user_token_headers,
            json=project_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["name"] == project_data["name"]
        assert data["description"] == project_data["description"]
        assert data["is_public"] == project_data["is_public"]
        assert data["status"] == ProjectStatus.ACTIVE.value
        
        # Verify project was created in the database
        project = db.query(Project).filter(Project.id == data["id"]).first()
        assert project is not None
        assert project.name == project_data["name"]

    def test_get_projects(self, client: TestClient, normal_user: User, normal_user_token_headers: dict, db: Session):
        """Test getting projects for the current user."""
        # Create a test project
        project = Project(
            name="Test Project",
            description="A test project",
            owner_id=normal_user.id,
            status=ProjectStatus.ACTIVE
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        response = client.get(
            "/api/v1/projects/",
            headers=normal_user_token_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(p["id"] == project.id for p in data)

    def test_get_project(self, client: TestClient, normal_user: User, normal_user_token_headers: dict, db: Session):
        """Test getting a specific project."""
        # Create a test project
        project = Project(
            name="Test Project",
            description="A test project",
            owner_id=normal_user.id,
            status=ProjectStatus.ACTIVE
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        response = client.get(
            f"/api/v1/projects/{project.id}",
            headers=normal_user_token_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == project.id
        assert data["name"] == project.name
        assert data["description"] == project.description
        assert data["status"] == project.status.value
        assert "stats" in data

    def test_update_project(self, client: TestClient, normal_user: User, normal_user_token_headers: dict, db: Session):
        """Test updating a project."""
        # Create a test project
        project = Project(
            name="Test Project",
            description="A test project",
            owner_id=normal_user.id,
            status=ProjectStatus.ACTIVE
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        update_data = {
            "name": "Updated Project Name",
            "description": "Updated description",
            "is_public": True,
            "status": ProjectStatus.ARCHIVED.value
        }
        
        response = client.put(
            f"/api/v1/projects/{project.id}",
            headers=normal_user_token_headers,
            json=update_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == project.id
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["is_public"] == update_data["is_public"]
        assert data["status"] == update_data["status"]
        
        # Verify project was updated in the database
        db.refresh(project)
        assert project.name == update_data["name"]
        assert project.description == update_data["description"]
        assert project.is_public == update_data["is_public"]
        assert project.status.value == update_data["status"]

    def test_delete_project(self, client: TestClient, normal_user: User, normal_user_token_headers: dict, db: Session):
        """Test deleting a project."""
        # Create a test project
        project = Project(
            name="Test Project",
            description="A test project",
            owner_id=normal_user.id,
            status=ProjectStatus.ACTIVE
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        response = client.delete(
            f"/api/v1/projects/{project.id}",
            headers=normal_user_token_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == project.id
        assert data["status"] == ProjectStatus.DELETED.value
        
        # Verify project was marked as deleted
        db.refresh(project)
        assert project.status == ProjectStatus.DELETED

    def test_get_project_members(self, client: TestClient, normal_user: User, normal_user_token_headers: dict, db: Session):
        """Test getting project members."""
        # Create a test project
        project = Project(
            name="Test Project",
            description="A test project",
            owner_id=normal_user.id,
            status=ProjectStatus.ACTIVE
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # Create a test user
        from namesearch.models.user import User as UserModel
        member = UserModel(
            email="member@example.com",
            hashed_password="hashed_password",
            full_name="Test Member",
            is_active=True
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        
        # Add member to project
        project_member = ProjectMember(
            project_id=project.id,
            user_id=member.id,
            role=ProjectRole.EDITOR
        )
        db.add(project_member)
        db.commit()
        
        response = client.get(
            f"/api/v1/projects/{project.id}/members",
            headers=normal_user_token_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["user"]["id"] == member.id
        assert data[0]["role"] == ProjectRole.EDITOR.value

    def test_add_project_member(self, client: TestClient, normal_user: User, normal_user_token_headers: dict, db: Session):
        """Test adding a member to a project."""
        # Create a test project
        project = Project(
            name="Test Project",
            description="A test project",
            owner_id=normal_user.id,
            status=ProjectStatus.ACTIVE
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # Create a test user to add as member
        from namesearch.models.user import User as UserModel
        new_member = UserModel(
            email="newmember@example.com",
            hashed_password="hashed_password",
            full_name="New Member",
            is_active=True
        )
        db.add(new_member)
        db.commit()
        db.refresh(new_member)
        
        member_data = {
            "user_id": new_member.id,
            "role": ProjectRole.VIEWER.value
        }
        
        response = client.post(
            f"/api/v1/projects/{project.id}/members",
            headers=normal_user_token_headers,
            json=member_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user"]["id"] == new_member.id
        assert data["role"] == member_data["role"]
        
        # Verify member was added to the project
        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == new_member.id
        ).first()
        assert member is not None
        assert member.role.value == member_data["role"]

    def test_update_project_member(self, client: TestClient, normal_user: User, normal_user_token_headers: dict, db: Session):
        """Test updating a project member's role."""
        # Create a test project
        project = Project(
            name="Test Project",
            description="A test project",
            owner_id=normal_user.id,
            status=ProjectStatus.ACTIVE
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # Create a test user
        from namesearch.models.user import User as UserModel
        member = UserModel(
            email="member@example.com",
            hashed_password="hashed_password",
            full_name="Test Member",
            is_active=True
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        
        # Add member to project
        project_member = ProjectMember(
            project_id=project.id,
            user_id=member.id,
            role=ProjectRole.VIEWER
        )
        db.add(project_member)
        db.commit()
        
        update_data = {
            "role": ProjectRole.EDITOR.value
        }
        
        response = client.put(
            f"/api/v1/projects/{project.id}/members/{member.id}",
            headers=normal_user_token_headers,
            json=update_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user"]["id"] == member.id
        assert data["role"] == update_data["role"]
        
        # Verify member's role was updated
        db.refresh(project_member)
        assert project_member.role.value == update_data["role"]

    def test_remove_project_member(self, client: TestClient, normal_user: User, normal_user_token_headers: dict, db: Session):
        """Test removing a member from a project."""
        # Create a test project
        project = Project(
            name="Test Project",
            description="A test project",
            owner_id=normal_user.id,
            status=ProjectStatus.ACTIVE
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # Create a test user
        from namesearch.models.user import User as UserModel
        member = UserModel(
            email="member@example.com",
            hashed_password="hashed_password",
            full_name="Test Member",
            is_active=True
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        
        # Add member to project
        project_member = ProjectMember(
            project_id=project.id,
            user_id=member.id,
            role=ProjectRole.VIEWER
        )
        db.add(project_member)
        db.commit()
        
        response = client.delete(
            f"/api/v1/projects/{project.id}/members/{member.id}",
            headers=normal_user_token_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user"]["id"] == member.id
        
        # Verify member was removed from the project
        member_exists = db.query(ProjectMember).filter(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == member.id
        ).first() is not None
        assert not member_exists
