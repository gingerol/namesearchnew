"""
Domain availability checker using python-whois with caching.
"""
import whois
import socket
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta

from .cache import get_cached_domain, cache_domain

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_domain_available(domain: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Check if a domain is available by querying WHOIS information with caching.
    
    Args:
        domain: The domain name to check (e.g., 'example.com')
        
    Returns:
        Tuple of (is_available, whois_data)
        - is_available: Boolean indicating if the domain is available
        - whois_data: Dictionary containing WHOIS information if domain is registered
    """
    if not domain:
        return False, None
    
    # Normalize domain (remove www. and convert to lowercase)
    domain = domain.lower().replace('www.', '')
    
    # Check cache first
    cached = get_cached_domain(domain)
    if cached is not None:
        logger.debug(f"Cache hit for domain: {domain}")
        return cached['is_available'], cached.get('whois_data')
    
    logger.info(f"Cache miss for domain: {domain}, performing WHOIS lookup")
    
    # First, try a DNS lookup as it's faster than WHOIS
    try:
        # Try to resolve the domain
        socket.gethostbyname(domain)
        # If we get here, the domain exists
        result = (False, None)
    except (socket.gaierror, socket.herror):
        # Domain doesn't resolve, proceed with WHOIS check
        try:
            w = whois.whois(domain)
            
            # Check if domain is registered
            if not w.domain_name:
                result = (True, None)
            # Check if domain is expired
            elif hasattr(w, 'expiration_date'):
                exp_date = w.expiration_date[0] if isinstance(w.expiration_date, list) else w.expiration_date
                result = (exp_date and exp_date < datetime.now(), w if w.domain_name else None)
            else:
                # If we have a domain name but no expiration date, assume it's registered
                result = (False, w if w.domain_name else None)
                
        except (whois.parser.PywhoisError, Exception) as e:
            logger.warning(f"WHOIS lookup failed for {domain}: {str(e)}")
            # If we can't get WHOIS info, assume the domain is available
            result = (True, None)
    
    # Cache the result
    cache_domain(domain, {
        'is_available': result[0],
        'whois_data': result[1]
    })
    
    return result


def get_domain_pricing(domain: str) -> Dict[str, Any]:
    """
    Get pricing information for a domain with caching.
    
    Args:
        domain: The domain name to check pricing for
        
    Returns:
        Dictionary containing pricing information
    """
    # Check cache first
    cached = get_cached_domain(f"pricing_{domain}")
    if cached is not None and 'pricing' in cached:
        return cached['pricing']
    
    # This is a placeholder implementation
    # In a real application, you would integrate with a domain registrar's API
    # like Namecheap, GoDaddy, etc.
    
    # For now, we'll use a more sophisticated heuristic to determine pricing
    tld = domain.split('.')[-1].lower()
    name = domain.split('.')[0]
    name_length = len(name)
    
    # Define pricing tiers
    premium_tlds = {
        'io': 60.0, 'ai': 80.0, 'co': 30.0, 
        'app': 20.0, 'dev': 20.0, 'tech': 50.0,
        'cloud': 40.0, 'io': 60.0, 'ai': 80.0
    }
    
    # Base price based on TLD
    base_price = premium_tlds.get(tld, 12.99)
    
    # Adjust price based on name length (shorter = more expensive)
    length_multiplier = max(0.5, 2 - (name_length * 0.1))  # 1.9x for 1 char, 1.0x for 10 chars, 0.5x for 15+ chars
    
    # Premium keywords increase price
    premium_keywords = {
        'app': 1.5, 'hq': 1.8, 'inc': 1.3, 'tech': 1.4,
        'cloud': 1.6, 'ai': 2.0, 'io': 1.7, 'co': 1.2
    }
    
    keyword_multiplier = 1.0
    for keyword, multiplier in premium_keywords.items():
        if keyword in name:
            keyword_multiplier = max(keyword_multiplier, multiplier)
    
    # Calculate final price
    price = round(base_price * length_multiplier * keyword_multiplier, 2)
    is_premium = price > 30.0  # Consider domains over $30 as premium
    
    # Add some randomness to make it look more realistic
    if is_premium:
        price = round(price * (0.9 + (0.2 * (hash(domain) % 10) / 10)), 2)
    
    pricing = {
        'is_premium': is_premium,
        'price': price,
        'currency': 'USD',
        'renewal_price': round(price * 1.2, 2),  # Renewal is typically more expensive
        'sale_price': round(price * 0.9, 2) if is_premium else None,  # Discount for premium domains
        'sale_ends': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d') if is_premium else None
    }
    
    # Cache the pricing
    cache_domain(f"pricing_{domain}", {'pricing': pricing})
    
    return pricing
