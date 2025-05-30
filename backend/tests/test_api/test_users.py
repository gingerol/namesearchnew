"""Tests for the users endpoints."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from namesearch.core.security import create_access_token
from namesearch.models.user import User


@pytest.mark.usefixtures("db")
class TestUsersAPI:
    """Test users API endpoints."""

    def test_read_users_me(self, client: TestClient, normal_user_token_headers: dict):
        """Test retrieving the current user."""
        response = client.get(
            "/api/v1/users/me", 
            headers=normal_user_token_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "email" in data
        assert "id" in data
        assert "is_active" in data
        assert data["is_active"] is True
        assert "is_superuser" in data
        assert "full_name" in data

    def test_update_user_me(
        self, 
        client: TestClient, 
        normal_user: User, 
        normal_user_token_headers: dict,
        db: Session
    ):
        """Test updating the current user."""
        update_data = {
            "full_name": "Updated Name",
            "email": "updated@example.com",
            "password": "newpassword123"
        }
        
        response = client.put(
            "/api/v1/users/me",
            headers=normal_user_token_headers,
            json=update_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["email"] == update_data["email"]
        
        # Verify password was updated
        db.refresh(normal_user)
        assert normal_user.verify_password(update_data["password"])

    def test_read_users(self, client: TestClient, superuser_token_headers: dict):
        """Test retrieving all users (admin only)."""
        response = client.get(
            "/api/v1/users/", 
            headers=superuser_token_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_read_user_by_id(
        self, 
        client: TestClient, 
        normal_user: User, 
        superuser_token_headers: dict
    ):
        """Test retrieving a user by ID (admin only)."""
        response = client.get(
            f"/api/v1/users/{normal_user.id}",
            headers=superuser_token_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == normal_user.id
        assert data["email"] == normal_user.email

    def test_create_user(self, client: TestClient, superuser_token_headers: dict, db: Session):
        """Test creating a new user (admin only)."""
        user_data = {
            "email": "newuser@example.com",
            "password": "testpassword123",
            "full_name": "New User"
        }
        response = client.post(
            "/api/v1/users/",
            headers=superuser_token_headers,
            json=user_data
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        assert "hashed_password" not in data
        
        # Verify user was created in the database
        user = db.query(User).filter(User.email == user_data["email"]).first()
        assert user is not None
        assert user.verify_password(user_data["password"])

    def test_update_user(
        self, 
        client: TestClient, 
        normal_user: User, 
        superuser_token_headers: dict,
        db: Session
    ):
        """Test updating a user (admin only)."""
        update_data = {
            "email": "updated_by_admin@example.com",
            "full_name": "Updated by Admin",
            "is_active": False,
            "is_superuser": True
        }
        
        response = client.put(
            f"/api/v1/users/{normal_user.id}",
            headers=superuser_token_headers,
            json=update_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == update_data["email"]
        assert data["full_name"] == update_data["full_name"]
        assert data["is_active"] == update_data["is_active"]
        assert data["is_superuser"] == update_data["is_superuser"]
        
        # Verify user was updated in the database
        db.refresh(normal_user)
        assert normal_user.email == update_data["email"]
        assert normal_user.full_name == update_data["full_name"]
        assert normal_user.is_active == update_data["is_active"]
        assert normal_user.is_superuser == update_data["is_superuser"]

    def test_delete_user(
        self, 
        client: TestClient, 
        normal_user: User, 
        superuser_token_headers: dict,
        db: Session
    ):
        """Test deleting a user (admin only)."""
        # Create a user to delete
        user_data = {
            "email": "tobedeleted@example.com",
            "password": "testpassword123",
            "full_name": "To Be Deleted"
        }
        user = User(
            email=user_data["email"],
            hashed_password=user_data["password"],
            full_name=user_data["full_name"],
            is_active=True,
            is_superuser=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        response = client.delete(
            f"/api/v1/users/{user.id}",
            headers=superuser_token_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == user.email
        
        # Verify user was marked as inactive
        deleted_user = db.query(User).filter(User.id == user.id).first()
        assert deleted_user is not None
        assert deleted_user.is_active is False

    def test_register_user(self, client: TestClient, db: Session):
        """Test user registration."""
        user_data = {
            "email": "newuser@example.com",
            "password": "testpassword123",
            "full_name": "New User"
        }
        
        response = client.post(
            "/api/v1/auth/register",
            json=user_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        assert "hashed_password" not in data
        
        # Verify user was created in the database
        user = db.query(User).filter(User.email == user_data["email"]).first()
        assert user is not None
        assert user.verify_password(user_data["password"])
        assert user.is_active is True
        assert user.is_superuser is False

    def test_login_user(self, client: TestClient, normal_user: User):
        """Test user login."""
        login_data = {
            "username": normal_user.email,
            "password": "testpassword"  # From the fixture
        }
        
        response = client.post(
            "/api/v1/auth/login/access-token",
            data=login_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
