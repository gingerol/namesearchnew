"""Tests for domain search functionality."""
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import patch, MagicMock

from ...main import app
from ...core.security import create_access_token
from ...models.user import User

client = TestClient(app)

def create_test_user():
    """Create a test user and return access token."""
    user_data = {
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    # This is a mock - in a real test, you'd use a test database
    test_user = User(
        email=user_data["email"],
        hashed_password="hashed_testpass123",
        full_name=user_data["full_name"],
        is_active=True
    )
    access_token = create_access_token(data={"sub": test_user.email})
    return test_user, access_token

@pytest.fixture
def auth_headers():
    """Return headers with a valid access token."""
    _, token = create_test_user()
    return {"Authorization": f"Bearer {token}"}

@patch('app.utils.domain_checker.is_domain_available')
@patch('app.services.ai.analyze_domain_name')
@patch('app.services.ai.analyze_brand_archetype')
async def test_search_domains(
    mock_brand_analysis, 
    mock_linguistic_analysis,
    mock_domain_available,
    auth_headers
):
    """Test domain search with valid input."""
    # Setup mocks
    mock_domain_available.return_value = (True, None)  # Domain is available
    
    mock_linguistic_analysis.return_value = {
        'complexity_score': 3.5,
        'is_pronounceable': True,
        'syllable_count': 2,
        'word_count': 1,
        'language': 'en'
    }
    
    mock_brand_analysis.return_value = {
        'archetype': 'Creator',
        'confidence': 0.85,
        'keywords': ['create', 'build', 'make']
    }
    
    # Test data
    search_data = {
        "query": "testapp",
        "tlds": ["com", "io"],
        "limit": 5
    }
    
    # Make request
    response = client.post(
        "/api/v1/domains/search",
        json=search_data,
        headers=auth_headers
    )
    
    # Assertions
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["query"] == "testapp"
    assert len(data["results"]) > 0
    assert all("testapp" in result["domain"] for result in data["results"])
    assert all("analysis" in result for result in data["results"])

async def test_search_domains_rate_limiting(auth_headers):
    """Test rate limiting on domain search."""
    search_data = {"query": "test"}
    
    # Make multiple requests quickly to trigger rate limiting
    for _ in range(15):  # More than the 10 request limit
        response = client.post(
            "/api/v1/domains/search",
            json=search_data,
            headers=auth_headers
        )
    
    # The last request should be rate limited
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

async def test_invalid_domain_search(auth_headers):
    """Test domain search with invalid input."""
    # Empty query
    response = client.post(
        "/api/v1/domains/search",
        json={"query": ""},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Invalid TLDs
    response = client.post(
        "/api/v1/domains/search",
        json={"query": "test", "tlds": ["invalid"]},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
