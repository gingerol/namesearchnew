"""Tests for the search CRUD operations."""
import pytest
from sqlalchemy.orm import Session

from namesearch import crud, models, schemas
from namesearch.models.domain import Search, SearchResult, SearchStatus
from tests.test_utils import random_lower_string, create_test_user


def test_create_search(db: Session, normal_user: models.User) -> None:
    """Test creating a new search."""
    search_data = {
        "query": "example",
        "status": SearchStatus.COMPLETED.value,
        "results_count": 5,
        "available_count": 3,
        "taken_count": 2,
        "premium_count": 0,
        "tlds": ["com", "net", "org"],
        "filters": {"min_length": 3, "max_length": 15}
    }
    
    search = crud.domain.create_search(
        db, 
        query=search_data["query"],
        user_id=normal_user.id,
        status=search_data["status"],
        results_count=search_data["results_count"],
        available_count=search_data["available_count"],
        taken_count=search_data["taken_count"],
        premium_count=search_data["premium_count"],
        tlds=search_data["tlds"],
        filters=search_data["filters"]
    )
    
    assert search.query == search_data["query"]
    assert search.status == search_data["status"]
    assert search.results_count == search_data["results_count"]
    assert search.available_count == search_data["available_count"]
    assert search.taken_count == search_data["taken_count"]
    assert search.premium_count == search_data["premium_count"]
    assert search.tlds == search_data["tlds"]
    assert search.filters == search_data["filters"]
    assert search.user_id == normal_user.id


def test_get_search(db: Session, normal_user: models.User) -> None:
    """Test getting a search by ID."""
    # Create a test search
    search = crud.domain.create_search(
        db, 
        query="example",
        user_id=normal_user.id,
        status=SearchStatus.COMPLETED.value
    )
    
    # Test getting the search by ID
    search_by_id = crud.domain.get_search(db, search_id=search.id)
    assert search_by_id
    assert search_by_id.id == search.id
    assert search_by_id.query == search.query
    
    # Test getting a non-existent search
    non_existent_search = crud.domain.get_search(db, search_id=999999)
    assert non_existent_search is None


def test_get_search_history(db: Session, normal_user: models.User) -> None:
    """Test getting search history for a user."""
    # Create some test searches
    for i in range(5):
        crud.domain.create_search(
            db, 
            query=f"example{i}",
            user_id=normal_user.id,
            status=SearchStatus.COMPLETED.value
        )
    
    # Test getting search history with pagination
    searches = crud.domain.get_search_history(
        db, 
        user_id=normal_user.id,
        skip=1,
        limit=3
    )
    
    assert len(searches) == 3
    assert all(s.user_id == normal_user.id for s in searches)


def test_add_search_result(db: Session, normal_user: models.User) -> None:
    """Test adding a search result."""
    # Create a test search
    search = crud.domain.create_search(
        db, 
        query="example",
        user_id=normal_user.id,
        status=SearchStatus.COMPLETED.value
    )
    
    # Create a test domain
    domain = crud.domain.create(
        db, 
        obj_in=schemas.DomainCreate(
            name="example",
            tld="com",
            status="available",
            whois_data={}
        )
    )
    
    # Add search result
    result_data = {
        "search_id": search.id,
        "domain_id": domain.id,
        "is_available": True,
        "is_premium": False,
        "price": None,
        "score": 85,
        "highlights": ["example"]
    }
    
    result = crud.domain.add_search_result(
        db,
        obj_in=schemas.SearchResultCreate(**result_data)
    )
    
    assert result.search_id == search.id
    assert result.domain_id == domain.id
    assert result.is_available == result_data["is_available"]
    assert result.is_premium == result_data["is_premium"]
    assert result.price == result_data["price"]
    assert result.score == result_data["score"]
    assert result.highlights == result_data["highlights"]


def test_get_search_results(db: Session, normal_user: models.User) -> None:
    """Test getting search results for a search."""
    # Create a test search
    search = crud.domain.create_search(
        db, 
        query="example",
        user_id=normal_user.id,
        status=SearchStatus.COMPLETED.value
    )
    
    # Create some test domains and search results
    for i in range(5):
        domain = crud.domain.create(
            db, 
            obj_in=schemas.DomainCreate(
                name=f"example{i}",
                tld="com",
                status="available",
                whois_data={}
            )
        )
        
        crud.domain.add_search_result(
            db,
            obj_in=schemas.SearchResultCreate(
                search_id=search.id,
                domain_id=domain.id,
                is_available=True,
                is_premium=False,
                score=80 + i
            )
        )
    
    # Test getting search results with pagination
    results = crud.domain.get_search_results(
        db,
        search_id=search.id,
        skip=1,
        limit=3
    )
    
    assert len(results) == 3
    assert all(r.search_id == search.id for r in results)
    # Results should be ordered by score (descending)
    assert all(
        results[i].score >= results[i+1].score 
        for i in range(len(results)-1)
    )


def test_delete_search(db: Session, normal_user: models.User) -> None:
    """Test deleting a search and its results."""
    # Create a test search
    search = crud.domain.create_search(
        db, 
        query="example",
        user_id=normal_user.id,
        status=SearchStatus.COMPLETED.value
    )
    
    # Create a test domain and search result
    domain = crud.domain.create(
        db, 
        obj_in=schemas.DomainCreate(
            name="example",
            tld="com",
            status="available",
            whois_data={}
        )
    )
    
    crud.domain.add_search_result(
        db,
        obj_in=schemas.SearchResultCreate(
            search_id=search.id,
            domain_id=domain.id,
            is_available=True
        )
    )
    
    # Delete the search
    deleted = crud.domain.delete_search(db, search_id=search.id)
    
    assert deleted is True
    
    # Verify the search was deleted
    assert crud.domain.get_search(db, search_id=search.id) is None
    
    # Verify the search results were also deleted
    results = crud.domain.get_search_results(db, search_id=search.id)
    assert len(results) == 0
