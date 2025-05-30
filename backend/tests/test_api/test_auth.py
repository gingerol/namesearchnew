"""Tests for the authentication endpoints."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from namesearch.models.user import User


class TestAuth:
    """Test authentication endpoints."""

    def test_login_success(self, client: TestClient, normal_user: User):
        """Test successful login."""
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

    def test_login_incorrect_password(self, client: TestClient, normal_user: User):
        """Test login with incorrect password."""
        login_data = {
            "username": normal_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post(
            "/api/v1/auth/login/access-token",
            data=login_data
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Incorrect email or password" in response.text

    def test_login_inactive_user(self, client: TestClient, inactive_user: User):
        """Test login with inactive user."""
        login_data = {
            "username": inactive_user.email,
            "password": "testpassword"  # From the fixture
        }
        
        response = client.post(
            "/api/v1/auth/login/access-token",
            data=login_data
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Inactive user" in response.text

    def test_register_success(self, client: TestClient, db: Session):
        """Test successful user registration."""
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

    def test_register_duplicate_email(self, client: TestClient, normal_user: User):
        """Test registration with duplicate email."""
        user_data = {
            "email": normal_user.email,  # Already exists
            "password": "testpassword123",
            "full_name": "Duplicate User"
        }
        
        response = client.post(
            "/api/v1/auth/register",
            json=user_data
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.text

    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email."""
        user_data = {
            "email": "not-an-email",
            "password": "testpassword123",
            "full_name": "Invalid Email"
        }
        
        response = client.post(
            "/api/v1/auth/register",
            json=user_data
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "value is not a valid email address" in response.text

    def test_register_short_password(self, client: TestClient):
        """Test registration with short password."""
        user_data = {
            "email": "shortpass@example.com",
            "password": "123",
            "full_name": "Short Password"
        }
        
        response = client.post(
            "/api/v1/auth/register",
            json=user_data
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "ensure this value has at least 8 characters" in response.text

    def test_refresh_token(self, client: TestClient, normal_user_token_headers: dict):
        """Test token refresh."""
        response = client.post(
            "/api/v1/auth/login/test-token",
            headers=normal_user_token_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "email" in data
        assert "id" in data
        assert data["is_active"] is True

    def test_refresh_token_invalid(self, client: TestClient):
        """Test token refresh with invalid token."""
        response = client.post(
            "/api/v1/auth/login/test-token",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in response.text

    def test_recover_password(self, client: TestClient, normal_user: User):
        """Test password recovery request."""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": normal_user.email}
        )
        
        # Even if the email doesn't exist, we return 202 to prevent email enumeration
        assert response.status_code == status.HTTP_202_ACCEPTED
        
        # TODO: Test email sending in a test environment

    def test_reset_password(self, client: TestClient, normal_user: User, db: Session):
        """Test password reset."""
        from namesearch.core.security import create_access_token
        
        # Generate a reset token
        token = create_access_token(subject=normal_user.email, expires_minutes=10)
        
        new_password = "newpassword123"
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": new_password
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the password was updated
        db.refresh(normal_user)
        assert normal_user.verify_password(new_password)

    def test_reset_password_invalid_token(self, client: TestClient):
        """Test password reset with invalid token."""
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "invalid-token",
                "new_password": "newpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid token" in response.text
