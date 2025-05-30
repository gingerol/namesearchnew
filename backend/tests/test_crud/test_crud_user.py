"""Tests for the user CRUD operations."""
import pytest
from sqlalchemy.orm import Session

from namesearch import crud, models, schemas
from namesearch.core.security import get_password_hash, verify_password
from tests.test_utils import random_email, random_lower_string


def test_create_user(db: Session) -> None:
    """Test creating a new user."""
    email = random_email()
    password = random_lower_string()
    full_name = "Test User"
    user_in = schemas.UserCreate(
        email=email, 
        password=password, 
        full_name=full_name
    )
    
    user = crud.user.create(db, obj_in=user_in)
    
    assert user.email == email
    assert hasattr(user, "hashed_password")
    assert not hasattr(user, "password")  # Password should be hashed
    assert verify_password(password, user.hashed_password)
    assert user.full_name == full_name
    assert user.is_active is True
    assert user.is_superuser is False


def test_authenticate_user(db: Session) -> None:
    """Test authenticating a user."""
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserCreate(
        email=email, 
        password=password, 
        full_name="Test User"
    )
    
    user = crud.user.create(db, obj_in=user_in)
    
    # Test successful authentication
    authenticated_user = crud.user.authenticate(
        db, 
        email=email, 
        password=password
    )
    assert authenticated_user
    assert authenticated_user.email == user.email
    
    # Test wrong password
    wrong_password_user = crud.user.authenticate(
        db, 
        email=email, 
        password="wrongpassword"
    )
    assert wrong_password_user is None
    
    # Test wrong email
    wrong_email_user = crud.user.authenticate(
        db, 
        email="wrong@example.com", 
        password=password
    )
    assert wrong_email_user is None
    
    # Test inactive user
    user.is_active = False
    db.add(user)
    db.commit()
    db.refresh(user)
    
    inactive_user = crud.user.authenticate(
        db, 
        email=email, 
        password=password
    )
    assert inactive_user is None


def test_get_user(db: Session) -> None:
    """Test getting a user by ID."""
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserCreate(
        email=email, 
        password=password, 
        full_name="Test User"
    )
    
    user = crud.user.create(db, obj_in=user_in)
    
    # Test getting the user by ID
    user_by_id = crud.user.get(db, id=user.id)
    assert user_by_id
    assert user_by_id.email == user.email
    assert user_by_id.id == user.id
    
    # Test getting a non-existent user
    non_existent_user = crud.user.get(db, id=999999)
    assert non_existent_user is None


def test_get_user_by_email(db: Session) -> None:
    """Test getting a user by email."""
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserCreate(
        email=email, 
        password=password, 
        full_name="Test User"
    )
    
    user = crud.user.create(db, obj_in=user_in)
    
    # Test getting the user by email
    user_by_email = crud.user.get_by_email(db, email=email)
    assert user_by_email
    assert user_by_email.email == user.email
    assert user_by_email.id == user.id
    
    # Test getting a non-existent user
    non_existent_user = crud.user.get_by_email(db, email="nonexistent@example.com")
    assert non_existent_user is None


def test_update_user(db: Session) -> None:
    """Test updating a user."""
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserCreate(
        email=email, 
        password=password, 
        full_name="Test User"
    )
    
    user = crud.user.create(db, obj_in=user_in)
    
    # Update the user
    new_email = random_email()
    new_full_name = "Updated User"
    user_update = schemas.UserUpdate(
        email=new_email,
        full_name=new_full_name,
        is_superuser=True
    )
    
    updated_user = crud.user.update(db, db_obj=user, obj_in=user_update)
    
    assert updated_user.email == new_email
    assert updated_user.full_name == new_full_name
    assert updated_user.is_superuser is True
    
    # Test updating with a new password
    new_password = random_lower_string()
    user_update = schemas.UserUpdate(password=new_password)
    updated_user = crud.user.update(db, db_obj=user, obj_in=user_update)
    
    assert verify_password(new_password, updated_user.hashed_password)


def test_remove_user(db: Session) -> None:
    """Test removing a user."""
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserCreate(
        email=email, 
        password=password, 
        full_name="Test User"
    )
    
    user = crud.user.create(db, obj_in=user_in)
    
    # Remove the user
    removed_user = crud.user.remove(db, id=user.id)
    
    assert removed_user.id == user.id
    assert removed_user.email == user.email
    
    # Verify the user was removed
    assert crud.user.get(db, id=user.id) is None


def test_get_multi_users(db: Session) -> None:
    """Test getting multiple users with pagination."""
    # Create some test users
    users = []
    for i in range(10):
        user_in = schemas.UserCreate(
            email=f"user{i}@example.com",
            password=random_lower_string(),
            full_name=f"User {i}"
        )
        user = crud.user.create(db, obj_in=user_in)
        users.append(user)
    
    # Test getting first page (5 users)
    users_page_1 = crud.user.get_multi(db, skip=0, limit=5)
    assert len(users_page_1) == 5
    
    # Test getting second page (5 users)
    users_page_2 = crud.user.get_multi(db, skip=5, limit=5)
    assert len(users_page_2) == 5
    
    # Test getting with skip beyond the number of users
    users_empty = crud.user.get_multi(db, skip=20, limit=5)
    assert len(users_empty) == 0
