"""Domain endpoints."""
from typing import Any, List, Dict, Tuple
import random
import asyncio
from datetime import datetime

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
from ....services.ai import analyze_domain_name, analyze_brand_archetype
from ....utils.domain_checker import is_domain_available, get_domain_pricing

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


async def check_domain_availability(domain_name: str) -> Dict[str, Any]:
    """Check domain availability and get details."""
    base_domain = domain_name.split('.')[0]
    
    # Get domain availability and pricing
    is_available, whois_data = is_domain_available(domain_name)
    pricing = get_domain_pricing(domain_name) if is_available else {}
    
    # Analyze the domain name (without TLD)
    linguistic_analysis = analyze_domain_name(base_domain)
    brand_analysis = analyze_brand_archetype(base_domain)
    
    # Create the result
    result = {
        "domain": domain_name,
        "tld": domain_name.split('.')[-1],
        "is_available": is_available,
        "is_premium": pricing.get('is_premium', False) if is_available else False,
        "price": pricing.get('price') if is_available else None,
        "analysis": {
            "linguistic": {
                "score": round(10 - linguistic_analysis['complexity_score'], 1),
                "is_pronounceable": linguistic_analysis['is_pronounceable'],
                "syllable_count": linguistic_analysis['syllable_count'],
                "word_count": linguistic_analysis['word_count']
            },
            "brand_archetype": brand_analysis['archetype'],
            "brand_confidence": brand_analysis['confidence'],
            "trademark_risk": "low"  # This would come from a trademark check service
        }
    }
    
    return result


@router.post("/search", response_model=DomainBulkSearchResponse)
async def search_domains(
    *,
    db: Session = Depends(get_db),
    search_in: DomainSearchQuery,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Search for domains with various filters and AI-powered analysis.
    
    This endpoint performs a domain search with linguistic and brand analysis
    to help users find the perfect domain name.
    """
    # Clean the search query
    query = search_in.query.lower().strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty"
        )
    
    # Generate domain variations with different TLDs
    tlds = search_in.tlds or ["com", "io", "ai", "app", "dev", "net", "org"]
    limit = min(search_in.limit or 10, 20)  # Max 20 results for performance
    
    # Generate domain variations
    domains_to_check = []
    base_domain = query.replace(' ', '').lower()
    
    # Add base domain with different TLDs
    for tld in tlds[:limit]:
        domains_to_check.append(f"{base_domain}.{tld}")
    
    # Add some common variations if we have room
    variations = [
        f"{base_dimain}{suffix}" for suffix in 
        ['app', 'hq', 'inc', 'ai', 'io', 'co', 'get', 'try', 'go']
    ]
    
    for var in variations:
        if len(domains_to_check) >= limit * 2:  # Don't check too many domains
            break
        for tld in tlds:
            domains_to_check.append(f"{var}.{tld}")
            if len(domains_to_check) >= limit * 2:
                break
    
    # Check domain availability in parallel
    tasks = [check_domain_availability(domain) for domain in domains_to_check[:limit]]
    results = await asyncio.gather(*tasks)
    
    # Filter and sort results
    available_results = [r for r in results if r['is_available']]
    taken_results = [r for r in results if not r['is_available']]
    
    # Sort available domains by price (non-premium first), then by domain length
    available_results.sort(key=lambda x: (x.get('price', 0) > 0, len(x['domain'])))
    
    # Combine results (available first, then taken)
    sorted_results = available_results + taken_results
    
    # Count premium domains
    premium_count = sum(1 for r in available_results if r.get('is_premium'))
    
    # Log the search in the database
    search_data = {
        "query": query,
        "results_count": len(results),
        "available_count": len(available_results),
        "user_id": current_user.id if current_user else None,
        "timestamp": datetime.utcnow()
    }
    
    try:
        search = Search(**search_data)
        db.add(search)
        db.commit()
    except Exception as e:
        db.rollback()
        # Don't fail the request if search logging fails
        pass
    
    return {
        "results": sorted_results[:limit],
        "total": len(sorted_results),
        "available": len(available_results),
        "taken": len(taken_results),
        "premium": premium_count,
        "query": query
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
