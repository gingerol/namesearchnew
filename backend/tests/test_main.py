"""Tests for the main FastAPI application."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from namesearch.main import app


class TestMain:
    """Test the main FastAPI application."""
    
    def test_read_root(self, client: TestClient):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_health_check(self, client: TestClient):
        """Test the health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_nonexistent_endpoint(self, client: TestClient):
        """Test a non-existent endpoint."""
        response = client.get("/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Not Found"
    
    def test_docs_redirect(self, client: TestClient):
        """Test the docs redirect."""
        response = client.get("/docs", allow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/api/docs"
    
    def test_redoc_redirect(self, client: TestClient):
        """Test the ReDoc redirect."""
        response = client.get("/redoc", allow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/api/redoc"
    
    def test_openapi_json(self, client: TestClient):
        """Test the OpenAPI JSON endpoint."""
        response = client.get("/api/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "openapi" in data
        assert data["info"]["title"] == "Namesearch.io API"
        assert data["info"]["version"] == "0.1.0"
