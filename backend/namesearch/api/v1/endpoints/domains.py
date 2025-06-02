"""Domain endpoints with rate limiting and enhanced search."""
from typing import Any, List, Dict, Tuple, Set
import asyncio
import logging
from datetime import datetime, timedelta
import re

from fastapi import APIRouter, Depends, HTTPException, status, Request
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
from ....utils.domain_generator import generate_domain_variations, is_valid_domain
from ....utils.rate_limiter import standard_limiter, strict_limiter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


async def check_domain_availability(domain_name: str) -> Dict[str, Any]:
    """
    Check domain availability and get detailed analysis.
    
    Args:
        domain_name: The domain name to check (e.g., 'example.com')
        
    Returns:
        Dictionary with domain details and analysis
    """
    try:
        # Validate domain format
        if not is_valid_domain(domain_name):
            logger.warning(f"Invalid domain format: {domain_name}")
            return {
                "domain": domain_name,
                "is_valid": False,
                "is_available": False,
                "error": "Invalid domain format"
            }
        
        # Get domain availability and pricing (with caching)
        is_available, whois_data = is_domain_available(domain_name)
        pricing = get_domain_pricing(domain_name) if is_available else {}
        
        # Extract base domain (without TLD) for analysis
        base_domain = domain_name.rsplit('.', 1)[0]
        
        # Perform linguistic and brand analysis in parallel
        linguistic_analysis, brand_analysis = await asyncio.gather(
            asyncio.to_thread(analyze_domain_name, base_domain),
            asyncio.to_thread(analyze_brand_archetype, base_domain)
        )
        
        # Calculate domain quality score
        quality_score = calculate_domain_quality_score(
            domain_name, 
            linguistic_analysis, 
            brand_analysis
        )
        
        # Create the result
        result = {
            "domain": domain_name,
            "tld": domain_name.rsplit('.', 1)[-1],
            "is_available": is_available,
            "is_valid": True,
            "quality_score": quality_score,
            "is_premium": pricing.get('is_premium', False) if is_available else False,
            "price": pricing.get('price') if is_available else None,
            "renewal_price": pricing.get('renewal_price') if is_available else None,
            "sale_price": pricing.get('sale_price') if is_available else None,
            "sale_ends": pricing.get('sale_ends') if is_available else None,
            "analysis": {
                "linguistic": {
                    "score": round(10 - linguistic_analysis.get('complexity_score', 5), 1),
                    "is_pronounceable": linguistic_analysis.get('is_pronounceable', False),
                    "syllable_count": linguistic_analysis.get('syllable_count', 0),
                    "word_count": linguistic_analysis.get('word_count', 0),
                    "language": linguistic_analysis.get('language', 'en')
                },
                "brand": {
                    "archetype": brand_analysis.get('archetype', 'Unknown'),
                    "confidence": brand_analysis.get('confidence', 0.0),
                    "keywords": brand_analysis.get('keywords', [])
                },
                "trademark_risk": "low",  # Placeholder for trademark check
                "seo_potential": calculate_seo_potential(domain_name, linguistic_analysis)
            },
            "whois": whois_data.to_dict() if whois_data and hasattr(whois_data, 'to_dict') else {}
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking domain {domain_name}: {str(e)}", exc_info=True)
        return {
            "domain": domain_name,
            "is_valid": False,
            "is_available": False,
            "error": str(e)
        }


def calculate_domain_quality_score(
    domain: str, 
    linguistic_analysis: Dict[str, Any], 
    brand_analysis: Dict[str, Any]
) -> float:
    """
    Calculate a quality score (0-100) for a domain based on various factors.
    
    Args:
        domain: The domain name
        linguistic_analysis: Linguistic analysis results
        brand_analysis: Brand analysis results
        
    Returns:
        float: Quality score between 0 and 100
    """
    score = 50.0  # Start with a neutral score
    
    try:
        # Length scoring (shorter is better)
        base_domain = domain.split('.')[0]
        if len(base_domain) <= 3:
            score += 20
        elif len(base_domain) <= 6:
            score += 15
        elif len(base_domain) <= 10:
            score += 10
        elif len(base_domain) <= 15:
            score += 5
        
        # Linguistic scoring
        if linguistic_analysis.get('is_pronounceable', False):
            score += 10
            
        # Brand scoring
        score += float(brand_analysis.get('confidence', 0)) * 10  # 0-10 points based on confidence
        
        # TLD scoring (.com is best)
        tld = domain.split('.')[-1]
        if tld == 'com':
            score += 10
        elif tld in ['io', 'ai', 'co']:
            score += 5
            
    except Exception as e:
        logger.warning(f"Error calculating quality score for {domain}: {str(e)}")
    
    # Ensure score is within bounds
    return max(0, min(100, round(score, 1)))


def calculate_seo_potential(domain: str, linguistic_analysis: Dict[str, Any]) -> float:
    """
    Calculate SEO potential score (0-1) for a domain.
    
    Args:
        domain: The domain name
        linguistic_analysis: Linguistic analysis results
        
    Returns:
        float: SEO potential score between 0 and 1
    """
    try:
        # Base score on word count and length
        word_count = int(linguistic_analysis.get('word_count', 1))
        base_domain = domain.split('.')[0]
        
        # More words are generally better for SEO, but not too many
        word_score = min(word_count / 3.0, 1.0)
        
        # Moderate length is best (3-15 chars)
        length = len(base_domain)
        if 3 <= length <= 15:
            length_score = 1.0
        else:
            length_score = max(0, 1.0 - (abs(length - 10) / 20.0))
        
        # Combine scores with weights
        return round((word_score * 0.7) + (length_score * 0.3), 2)
        
    except Exception as e:
        logger.warning(f"Error calculating SEO potential for {domain}: {str(e)}")
        return 0.5  # Default score if calculation fails


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
    request: Request,
    db: Session = Depends(get_db),
    search_in: DomainSearchQuery,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Search for domains with various filters and AI-powered analysis.
    
    This endpoint performs a domain search with linguistic and brand analysis
    to help users find the perfect domain name.
    
    Rate limited to 10 requests per minute per IP.
    """
    # Apply rate limiting
    await strict_limiter(request)
    
    # Clean and validate the search query
    query = (search_in.query or '').lower().strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty"
        )
    
    # Validate TLDs if provided
    tlds = search_in.tlds or []
    if tlds and not all(isinstance(tld, str) and tld.isalpha() for tld in tlds):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid TLD format. TLDs must contain only letters."
        )
    
    # Set limits
    max_results = min(search_in.limit or 20, 50)  # Max 50 results for performance
    
    try:
        # Generate domain variations
        logger.info(f"Generating domain variations for: {query}")
        domains_to_check = generate_domain_variations(query, max_results * 2)
        
        # Add custom TLDs if specified
        if tlds:
            base_domain = re.sub(r'[^a-z0-9]', '', query)
            for tld in tlds:
                if len(domains_to_check) >= max_results * 3:  # Don't check too many domains
                    break
                domains_to_check.append(f"{base_domain}.{tld}")
        
        # Remove duplicates and validate
        domains_to_check = list({d.lower() for d in domains_to_check if is_valid_domain(d)})
        
        # Limit the number of domains to check
        domains_to_check = domains_to_check[:max_results * 2]
        
        if not domains_to_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid domain names could be generated from the query"
            )
        
        # Check domain availability in parallel with semaphore to limit concurrency
        logger.info(f"Checking availability for {len(domains_to_check)} domains")
        
        # Use a semaphore to limit concurrent WHOIS/DNS lookups
        sem = asyncio.Semaphore(10)  # Limit to 10 concurrent checks
        
        async def check_with_semaphore(domain: str) -> Dict[str, Any]:
            async with sem:
                return await check_domain_availability(domain)
        
        tasks = [check_with_semaphore(domain) for domain in domains_to_check]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results, handling any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Error checking domain {domains_to_check[i]}: {str(result)}")
                continue
            if isinstance(result, dict):
                processed_results.append(result)
        
        # Filter and sort results
        available_results = [r for r in processed_results if r.get('is_available')]
        taken_results = [r for r in processed_results if not r.get('is_available')]
        
        # Sort available domains by price (non-premium first), then by domain length
        available_results.sort(key=lambda x: (
            x.get('price', 0) > 0,  # Non-premium first
            len(x.get('domain', '')),  # Shorter domains first
            -x.get('analysis', {}).get('linguistic', {}).get('score', 0)  # Higher score first
        ))
        
        # Sort taken domains by domain length
        taken_results.sort(key=lambda x: len(x.get('domain', '')))
        
        # Combine results (available first, then taken)
        sorted_results = available_results + taken_results
        
        # Limit to max results
        sorted_results = sorted_results[:max_results]
        
        # Count premium domains
        premium_count = sum(1 for r in available_results if r.get('is_premium'))
        
        # Log the search in the database
        search_data = {
            "query": query,
            "results_count": len(processed_results),
            "available_count": len(available_results),
            "user_id": current_user.id,
            "timestamp": datetime.utcnow()
        }
        
        try:
            search = Search(**search_data)
            db.add(search)
            db.commit()
        except Exception as e:
            logger.error(f"Error saving search to database: {str(e)}")
            db.rollback()
        
        return {
            "query": query,
            "results": sorted_results,
            "total_results": len(processed_results),
            "available_count": len(available_results),
            "premium_count": premium_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except asyncio.CancelledError:
        logger.warning("Domain search was cancelled")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search was cancelled due to server load. Please try again later."
        )
    except Exception as e:
        logger.error(f"Error in domain search: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again later."
        )
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
