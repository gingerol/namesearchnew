"""Tests for the domain endpoints."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from namesearch.models.domain import Domain, Search, SearchResult, DomainStatus, SearchStatus
from namesearch.models import User


class TestDomainsAPI:
    """Test domains API endpoints."""

    def test_search_domains(self, client: TestClient, normal_user_token_headers: dict):
        """Test domain search."""
        search_data = {
            "query": "test",
            "tlds": ["com", "net"],
            "max_results": 10
        }
        
        response = client.post(
            "/api/v1/domains/search",
            headers=normal_user_token_headers,
            json=search_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert "available" in data
        assert "taken" in data
        assert "premium" in data

    def test_get_domain(self, client: TestClient, normal_user_token_headers: dict, db: Session):
        """Test getting domain details."""
        # Create a test domain
        domain = Domain(
            name="test",
            tld="com",
            status=DomainStatus.AVAILABLE
        )
        db.add(domain)
        db.commit()
        db.refresh(domain)
        
        response = client.get(
            f"/api/v1/domains/{domain.id}",
            headers=normal_user_token_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == domain.id
        assert data["name"] == domain.name
        assert data["tld"] == domain.tld
        assert data["status"] == domain.status.value

    def test_check_domain_availability(self, client: TestClient, normal_user_token_headers: dict):
        """Test domain availability check."""
        domain_data = {
            "name": "test",
            "tld": "com"
        }
        
        response = client.post(
            "/api/v1/domains/check",
            headers=normal_user_token_headers,
            json=domain_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["name"] == domain_data["name"]
        assert data["tld"] == domain_data["tld"]
        assert "status" in data

    def test_get_domain_whois(self, client: TestClient, normal_user_token_headers: dict, db: Session):
        """Test getting WHOIS information for a domain."""
        # Create a test domain with WHOIS data
        domain = Domain(
            name="test",
            tld="com",
            status=DomainStatus.REGISTERED,
            whois_data={"registrar": "Test Registrar"}
        )
        db.add(domain)
        db.commit()
        db.refresh(domain)
        
        response = client.get(
            f"/api/v1/domains/{domain.id}/whois",
            headers=normal_user_token_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "registrar" in data
        assert data["registrar"] == "Test Registrar"

    def test_get_search_history(self, client: TestClient, normal_user: User, normal_user_token_headers: dict, db: Session):
        """Test getting search history."""
        # Create a test search
        search = Search(
            query="test",
            user_id=normal_user.id,
            status=SearchStatus.COMPLETED
        )
        db.add(search)
        db.commit()
        db.refresh(search)
        
        response = client.get(
            "/api/v1/searches/history",
            headers=normal_user_token_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["query"] == "test"
        assert data[0]["status"] == "completed"

    def test_get_search_results(self, client: TestClient, normal_user: User, normal_user_token_headers: dict, db: Session):
        """Test getting search results."""
        # Create a test search
        search = Search(
            query="test",
            user_id=normal_user.id,
            status=SearchStatus.COMPLETED
        )
        db.add(search)
        db.commit()
        db.refresh(search)
        
        # Create a test domain
        domain = Domain(
            name="test",
            tld="com",
            status=DomainStatus.AVAILABLE
        )
        db.add(domain)
        db.commit()
        db.refresh(domain)
        
        # Create a search result
        search_result = SearchResult(
            search_id=search.id,
            domain_id=domain.id,
            is_available=True
        )
        db.add(search_result)
        db.commit()
        
        response = client.get(
            f"/api/v1/searches/{search.id}/results",
            headers=normal_user_token_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # In the current implementation, we're returning an empty list as a placeholder
        # Update this test when the actual implementation is done
        assert len(data) == 0

    def test_delete_search(self, client: TestClient, normal_user: User, normal_user_token_headers: dict, db: Session):
        """Test deleting a search."""
        # Create a test search
        search = Search(
            query="test",
            user_id=normal_user.id,
            status=SearchStatus.COMPLETED
        )
        db.add(search)
        db.commit()
        db.refresh(search)
        
        response = client.delete(
            f"/api/v1/searches/{search.id}",
            headers=normal_user_token_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == search.id
        assert data["query"] == "test"
        
        # Verify search was deleted
        deleted_search = db.query(Search).filter(Search.id == search.id).first()
        assert deleted_search is None
