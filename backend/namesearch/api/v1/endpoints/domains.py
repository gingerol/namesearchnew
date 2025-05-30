"""Domain endpoints."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .... import crud, models
from ....core.security import get_current_active_user
from ....db.session import get_db
from ....schemas.domain import (
    DomainPublic, DomainBulkSearchResponse, DomainBase, 
    DomainSearchQuery, DomainSearchResult, DomainCreate, DomainStatus
)
from ....schemas.search import Search

router = APIRouter()


@router.get("/", response_model=List[DomainPublic])
def read_domains(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve domains with pagination.
    """
    domains = crud.domain.get_multi(db, skip=skip, limit=limit)
    return domains


@router.post("/search", response_model=DomainBulkSearchResponse)
def search_domains(
    *,
    db: Session = Depends(get_db),
    search_in: DomainSearchQuery,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Search for domains with various filters.
    """
    # TODO: Implement actual domain search logic with WHOIS lookup
    # For now, return a mock response
    return {
        "results": [],
        "total": 0,
        "available": 0,
        "taken": 0,
        "premium": 0
    }


@router.get("/{domain_id}", response_model=DomainPublic)
def read_domain(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific domain by ID.
    """
    domain = crud.domain.get(db, id=domain_id)
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )
    return domain


@router.post("/check", response_model=DomainPublic)
def check_domain(
    *,
    db: Session = Depends(get_db),
    domain_in: DomainBase,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Check domain availability and get details.
    """
    # Check if domain exists in our database
    domain = crud.domain.get_by_name(db, name=f"{domain_in.name}.{domain_in.tld}")
    
    if not domain:
        # TODO: Perform WHOIS lookup and create domain record
        # For now, create a mock domain
        domain = crud.domain.create(
            db,
            obj_in=DomainCreate(
                name=domain_in.name,
                tld=domain_in.tld,
                status=DomainStatus.UNKNOWN
            )
        )
    
    return domain


@router.get("/{domain_id}/whois", response_model=dict)
def get_domain_whois(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get WHOIS information for a domain.
    """
    domain = crud.domain.get(db, id=domain_id)
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )
    
    # TODO: Implement actual WHOIS lookup if not in database or expired
    # For now, return the stored WHOIS data or empty dict
    return domain.whois_data or {}


@router.get("/search/history", response_model=List[Search])
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
