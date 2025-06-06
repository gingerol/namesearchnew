"""
Domain availability checker using python-whois with caching.
"""
import re
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
    domain = domain.lower().strip()
    domain = domain.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]
    
    # Validate domain format
    if not re.match(r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$', domain):
        logger.warning(f"Invalid domain format: {domain}")
        return False, None
    
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
        # If we get here, the domain exists and is registered
        result = (False, None)
    except (socket.gaierror, socket.herror):
        # Domain doesn't resolve, proceed with WHOIS check
        try:
            # Set a timeout for the WHOIS lookup
            socket.setdefaulttimeout(10)
            
            # Initialize WHOIS with more detailed parameters
            w = whois.whois(
                domain,
                ignore_returncode=1,  # Don't raise exceptions on return codes
                timeout=10,
                cache_age=0,  # Don't use cache, we handle our own
                slow_down=1,  # Add delay between requests
                internationalized=True  # Handle IDNs
            )
            
            # Convert WHOIS data to dict if it's not already
            whois_data = dict(w) if w and not isinstance(w, dict) else (w or {})
            
            # Check if we got any meaningful data
            if not whois_data:
                logger.warning(f"No WHOIS data received for {domain}, assuming available")
                result = (True, None)
            else:
                # Check for common availability indicators in the response
                whois_str = str(whois_data).lower()
                availability_indicators = [
                    "no match", "no data found", "not found", 
                    "no entries found", "no object found",
                    "no such domain", "domain not found"
                ]
                
                if any(indicator in whois_str for indicator in availability_indicators):
                    result = (True, whois_data)
                else:
                    # Check if we have a domain name in the response
                    if whois_data.get('domain_name'):
                        # Check if domain is expired
                        exp_date = whois_data.get('expiration_date')
                        if exp_date:
                            if isinstance(exp_date, list):
                                exp_date = exp_date[0] if exp_date else None
                            if exp_date and isinstance(exp_date, datetime) and exp_date < datetime.now():
                                result = (True, whois_data)
                                return result  # Early return for expired domains
                        
                        # If we have name servers, domain is likely registered
                        if whois_data.get('name_servers'):
                            result = (False, whois_data)
                        else:
                            # If we have a creation date but no name servers, still consider it registered
                            if whois_data.get('creation_date'):
                                result = (False, whois_data)
                            else:
                                # If we can't determine, assume available
                                result = (True, whois_data)
                    else:
                        # No domain name in response, assume available
                        result = (True, whois_data)
                        
        except (whois.parser.PywhoisError, socket.timeout, Exception) as e:
            logger.warning(f"WHOIS lookup failed for {domain}: {str(e)}")
            # If we can't get WHOIS info, be conservative and assume registered
            result = (False, None)
    
    # Cache the result with a TTL based on the result
    # Shorter TTL for available domains to catch new registrations faster
    ttl_hours = 1 if result[0] else 24  # 1 hour for available, 24 hours for registered
    
    cache_domain(
        domain, 
        {
            'is_available': result[0],
            'whois_data': result[1],
            'expires_at': datetime.now() + timedelta(hours=ttl_hours)
        },
        ttl=ttl_hours * 3600  # Convert hours to seconds
    )
    
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
