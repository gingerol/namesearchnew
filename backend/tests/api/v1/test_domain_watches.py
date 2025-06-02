"""Tests for domain watches API endpoints."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from namesearch.main import app
from namesearch.models.user import User
from namesearch.models.domain_watch import DomainWatch
from namesearch.schemas.domain_watch import DomainWatchCreate, DomainWatchUpdate
from namesearch.core.security import create_access_token

# Enable async test support
pytestmark = pytest.mark.asyncio

# Use async test client
@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

async def test_create_domain_watch(
    db: Session, test_user: User, test_user_token_headers: dict, client: TestClient
):
    """Test creating a new domain watch."""
    watch_data = {
        "domain": "example.com",
        "check_frequency": 60,
        "is_active": True
    }
    
    response = client.post(
        "/api/v1/watches/",
        headers=test_user_token_headers,
        json=watch_data,
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["domain"] == "example.com"
    assert data["user_id"] == test_user.id
    assert "id" in data

async def test_get_domain_watch(
    db: Session, test_user: User, test_user_token_headers: dict, test_domain_watch: DomainWatch, client: TestClient
):
    """Test retrieving a domain watch."""
    response = client.get(
        f"/api/v1/watches/{test_domain_watch.id}",
        headers=test_user_token_headers,
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_domain_watch.id
    assert data["domain"] == test_domain_watch.domain

async def test_list_domain_watches(
    db: Session, test_user: User, test_user_token_headers: dict, test_domain_watch: DomainWatch, client: TestClient
):
    """Test listing domain watches."""
    response = client.get(
        "/api/v1/watches/",
        headers=test_user_token_headers,
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert any(watch["id"] == test_domain_watch.id for watch in data)

async def test_update_domain_watch(
    db: Session, test_user: User, test_user_token_headers: dict, test_domain_watch: DomainWatch, client: TestClient
):
    """Test updating a domain watch."""
    update_data = {
        "check_frequency": 120,
        "is_active": False
    }
    
    response = client.put(
        f"/api/v1/watches/{test_domain_watch.id}",
        headers=test_user_token_headers,
        json=update_data,
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["check_frequency"] == 120
    assert data["is_active"] is False

async def test_delete_domain_watch(
    db: Session, test_user: User, test_user_token_headers: dict, test_domain_watch: DomainWatch, client: TestClient
):
    """Test deleting a domain watch."""
    response = client.delete(
        f"/api/v1/watches/{test_domain_watch.id}",
        headers=test_user_token_headers,
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Domain watch deleted successfully"}
    
    # Verify the watch was deleted
    response = client.get(
        f"/api/v1/watches/{test_domain_watch.id}",
        headers=test_user_token_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

async def test_check_domain_now(
    db: Session, test_user: User, test_user_token_headers: dict, test_domain_watch: DomainWatch, mocker, client: TestClient
):
    """Test manually triggering a domain check."""
    # Mock the WHOIS service to avoid actual network calls
    mock_whois = mocker.patch("namesearch.services.whois_service.whois_service.lookup_domain")
    mock_whois.return_value = {
        "status": "active",
        "expiration_date": "2025-12-31T23:59:59Z",
        "creation_date": "2020-01-01T00:00:00Z",
        "updated_date": "2024-01-01T00:00:00Z",
        "registrar": "Example Registrar"
    }
    
    response = client.post(
        f"/api/v1/watches/{test_domain_watch.id}/check-now",
        headers=test_user_token_headers,
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["last_status"] == "active"
    assert data["last_checked"] is not None
