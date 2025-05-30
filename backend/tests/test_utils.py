"""Test utilities for the backend application."""
import random
import string
from typing import Any, Dict, Optional

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from namesearch.core.security import get_password_hash
from namesearch.models.user import User


def random_lower_string(length: int = 8) -> str:
    """Generate a random string of lowercase letters and digits."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def random_email() -> str:
    """Generate a random email address."""
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_superuser_token_headers(client: TestClient) -> Dict[str, str]:
    """Get a valid token for a superuser."""
    login_data = {
        "username": "admin@example.com",
        "password": "adminpassword"
    }
    response = client.post("/api/v1/auth/login/access-token", data=login_data)
    tokens = response.json()
    access_token = tokens["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def create_test_user(db: Session, **kwargs) -> User:
    """Create a test user."""
    user_data = {
        "email": random_email(),
        "hashed_password": get_password_hash("testpassword"),
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False,
    }
    user_data.update(kwargs)
    
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_test_project(
    db: Session, 
    owner_id: int, 
    **kwargs
) -> Dict[str, Any]:
    """Create a test project."""
    from namesearch.models.project import Project
    
    project_data = {
        "name": f"Test Project {random_lower_string(4)}",
        "description": f"Test description {random_lower_string(12)}",
        "owner_id": owner_id,
        "is_public": False,
        "status": "active"
    }
    project_data.update(kwargs)
    
    project = Project(**project_data)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def create_test_domain(
    db: Session,
    **kwargs
) -> Dict[str, Any]:
    """Create a test domain."""
    from namesearch.models.domain import Domain, DomainStatus
    
    domain_data = {
        "name": random_lower_string(8),
        "tld": random.choice(["com", "net", "org", "io"]),
        "status": random.choice(list(DomainStatus)).value,
        "whois_data": {},
    }
    domain_data.update(kwargs)
    
    domain = Domain(**domain_data)
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return domain
