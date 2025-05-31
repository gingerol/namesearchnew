"""Pytest configuration and fixtures."""
import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from namesearch.core.config import settings
from namesearch.db.base import Base
from namesearch.db.session import get_db
from namesearch.main import app
from namesearch.models.user import User
from namesearch.core.security import get_password_hash

# Use an in-memory SQLite database for tests
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """Create database engine for tests."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield engine
    # Drop all tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db(db_engine):
    """Create a fresh database session with a rollback at the end of each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator:
    """Create a test client for the FastAPI application using the test DB session."""
    from namesearch.main import app

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def normal_user(db: Session) -> User:
    """Create a normal test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("Testpassword123"),
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def superuser(db: Session) -> User:
    """Create a superuser test user."""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("Adminpassword123"),
        full_name="Admin User",
        is_active=True,
        is_superuser=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def normal_user_token_headers(normal_user: User, client: TestClient) -> dict[str, str]:
    """Get a valid access token for a normal user."""
    from namesearch.core.security import create_access_token
    
    access_token = create_access_token(subject=normal_user.email)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
def superuser_token_headers(superuser: User, client: TestClient) -> dict[str, str]:
    """Get a valid access token for a superuser."""
    from namesearch.core.security import create_access_token
    
    access_token = create_access_token(subject=superuser.email)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
def inactive_user(db: Session) -> User:
    """Create an inactive test user."""
    user = User(
        email="inactive@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Inactive User",
        is_active=False,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def inactive_user_token_headers(inactive_user: User) -> dict[str, str]:
    """Get a token for an inactive user."""
    from namesearch.core.security import create_access_token
    
    access_token = create_access_token(subject=inactive_user.id)
    return {"Authorization": f"Bearer {access_token}"}
