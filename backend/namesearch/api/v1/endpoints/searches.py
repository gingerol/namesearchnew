"""Search endpoints."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .... import crud, models
from ....core.security import get_current_active_user
from ....db.session import get_db
from ....schemas.domain import DomainSearchQuery, DomainBulkSearchResponse, DomainPublic
from ....schemas.search import Search, SearchResults

router = APIRouter()


@router.post("/domains", response_model=DomainBulkSearchResponse)
def search_domains(
    *,
    db: Session = Depends(get_db),
    search_in: DomainSearchQuery,
    current_user: models.User = Depends(get_current_active_user),
    save_search: bool = True,
) -> Any:
    """
    Search for domains with various filters.
    
    Args:
        search_in: The search query parameters
        save_search: Whether to save this search to the user's history
    """
    # Create a search record
    if save_search:
        search = crud.domain.create_search(
            db, query=search_in.query, user_id=current_user.id
        )
    else:
        search = None
    
    # TODO: Implement actual domain search with WHOIS lookup
    # For now, return a mock response
    results = []
    
    # If this was a saved search, create search results
    if search:
        # TODO: Create actual search results
        pass
    
    return {
        "results": results,
        "total": len(results),
        "available": 0,
        "taken": 0,
        "premium": 0
    }


@router.get("/history", response_model=List[Search])
def get_search_history(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get the current user's search history.
    """
    searches = crud.domain.get_search_history(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return searches


@router.get("/{search_id}", response_model=Search)
def get_search(
    search_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific search by ID.
    """
    search = crud.domain.get_search(db, search_id=search_id)
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )
    
    # Check if the search belongs to the current user
    if search.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this search"
        )
    
    return search


@router.get("/{search_id}/results", response_model=List[DomainPublic])
def get_search_results(
    search_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get the results of a specific search.
    """
    # Verify the search exists and belongs to the user
    search = crud.domain.get_search(db, search_id=search_id)
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )
    
    if search.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these search results"
        )
    
    # TODO: Implement actual search results retrieval
    # For now, return an empty list
    return []


@router.delete("/{search_id}", response_model=Search)
def delete_search(
    search_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a search and its results.
    """
    search = crud.domain.get_search(db, search_id=search_id)
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )
    
    # Only the search owner can delete it
    if search.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this search"
        )
    
    # TODO: Delete associated search results
    # For now, just delete the search
    db.delete(search)
    db.commit()
    
    return search
