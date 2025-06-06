"""Search endpoints."""
from typing import Any, List

import math
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .... import crud, models
from ....core.security import get_current_active_user
from ....db.session import get_db
from ....schemas.domain import (
    DomainSearchQuery, DomainBulkSearchResponse, DomainPublic,
    AdvancedDomainSearchRequest, PaginatedFilteredDomainsResponse, FilteredDomainInfo,
    SortOrderEnum # Ensure SortOrderEnum is imported if it's used directly in type hints here, though it's part of AdvancedDomainSearchRequest
)
from ....core.logging_config import logger # Import your configured logger
from ....schemas.search import Search, SearchResults

router = APIRouter()


@router.post("/domains/old-bulk-whois", response_model=DomainBulkSearchResponse, tags=["domains-legacy"], summary="Legacy bulk WHOIS lookup", description="This is the older endpoint for performing direct WHOIS lookups based on a query and TLD list. Consider using the new /domains/search for broader searches.")
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
    
    # Perform WHOIS lookups for each domain combination
    results = []
    available_count = 0
    taken_count = 0
    premium_count = 0
    
    # Generate domain combinations
    base_query = search_in.query.lower()
    for tld in search_in.tlds:
        full_domain = f"{base_query}.{tld}"
        try:
            whois_result = whois_service.lookup_domain(full_domain)
            domain_status = whois_result.get("status")
            
            # Update counts
            if domain_status == DomainStatus.AVAILABLE:
                available_count += 1
            elif domain_status == DomainStatus.REGISTERED:
                taken_count += 1
            
            # Add result
            results.append({
                "domain": full_domain,
                "status": domain_status,
                "registrar": whois_result.get("registrar"),
                "creation_date": whois_result.get("creation_date"),
                "expiration_date": whois_result.get("expiration_date"),
                "name_servers": whois_result.get("name_servers"),
                "is_available": domain_status == DomainStatus.AVAILABLE
            })
        except Exception as e:
            logger.error(f"Error looking up domain {full_domain}: {str(e)}")
            continue
    
    # If this was a saved search, create search results
    if search:
        crud.domain.create_search_results(
            db,
            search_id=search.id,
            results=results
        )
    
    return {
        "results": results,
        "total": len(results),
        "available": available_count,
        "taken": taken_count,
        "premium": premium_count
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


@router.post("/domains/search", response_model=PaginatedFilteredDomainsResponse, tags=["domains"])
async def advanced_domain_search(
    *, 
    db: Session = Depends(get_db),
    search_request: AdvancedDomainSearchRequest,
    current_user: models.User = Depends(get_current_active_user) # Add if auth is needed
) -> Any:
    """
    Perform an advanced search for domains with various filters like keywords, TLDs,
    price range, and domain length. Supports pagination.
    """
    logger.info(f"Received advanced_domain_search request with the following parameters:")
    logger.info(f"  Keywords: {search_request.keywords}")
    logger.info(f"  TLDs: {search_request.tlds}")
    logger.info(f"  Min Price: {search_request.min_price}")
    logger.info(f"  Max Price: {search_request.max_price}")
    logger.info(f"  Min Length: {search_request.min_length}")
    logger.info(f"  Max Length: {search_request.max_length}")
    logger.info(f"  Only Available: {search_request.only_available}")
    logger.info(f"  Only Premium: {search_request.only_premium}")
    logger.info(f"  Starts With: {search_request.starts_with}")
    logger.info(f"  Ends With: {search_request.ends_with}")
    logger.info(f"  Exclude Pattern: {search_request.exclude_pattern}")
    logger.info(f"  Allow Numbers: {search_request.allow_numbers}")
    logger.info(f"  Allow Hyphens: {search_request.allow_hyphens}")
    logger.info(f"  Allow Special Chars: {search_request.allow_special_chars}")
    logger.info(f"  Min Quality Score: {search_request.min_quality_score}")
    logger.info(f"  Min SEO Score: {search_request.min_seo_score}")
    logger.info(f"  Registered After: {search_request.registered_after}")
    logger.info(f"  Registered Before: {search_request.registered_before}")
    logger.info(f"  Min Age Years: {search_request.min_age_years}")
    logger.info(f"  Max Age Years: {search_request.max_age_years}")
    logger.info(f"  Min Search Volume: {search_request.min_search_volume}")
    logger.info(f"  Min CPC: {search_request.min_cpc}")
    logger.info(f"  Language Code: {search_request.language_code}")
    logger.info(f"  Sort By: {search_request.sort_by}")
    logger.info(f"  Sort Order: {search_request.sort_order}")
    logger.info(f"  Page: {search_request.page}")
    logger.info(f"  Page Size: {search_request.page_size}")

    # Call the CRUD function to get filtered domains and total count
    try:
        domains, total_items = crud.domain.advanced_search_filtered(db=db, filters=search_request)
    except ValueError as e:
        logger.error(f"ValueError during advanced search: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during advanced search: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during search.")

    # Calculate total pages
    total_pages = 0
    if search_request.page_size > 0: # page_size should be > 0 based on Pydantic model (e.g. gt=0)
        total_pages = math.ceil(total_items / search_request.page_size)
    elif total_items > 0 : # page_size is 0 or less, but there are items
        total_pages = 1 
    # else total_pages remains 0 if total_items is 0

    # The `domains` are ORM objects. Pydantic's `from_attributes=True` in FilteredDomainInfo
    # will handle the conversion when creating PaginatedFilteredDomainsResponse.
    return PaginatedFilteredDomainsResponse(
        items=domains, # Pydantic will convert List[Domain] to List[FilteredDomainInfo]
        total_items=total_items,
        page=search_request.page,
        page_size=search_request.page_size,
        total_pages=total_pages
    )


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
