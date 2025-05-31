"""
Domain availability checker using python-whois.
"""
import whois
import socket
from typing import Dict, Any, Optional, Tuple
from datetime import datetime


def is_domain_available(domain: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Check if a domain is available by querying WHOIS information.
    
    Args:
        domain: The domain name to check (e.g., 'example.com')
        
    Returns:
        Tuple of (is_available, whois_data)
        - is_available: Boolean indicating if the domain is available
        - whois_data: Dictionary containing WHOIS information if domain is registered
    """
    if not domain:
        return False, None
        
    # First, try a DNS lookup as it's faster than WHOIS
    try:
        # Try to resolve the domain
        socket.gethostbyname(domain)
        # If we get here, the domain exists
        return False, None
    except (socket.gaierror, socket.herror):
        # Domain doesn't resolve, but we should still check WHOIS
        pass
    
    # If DNS lookup didn't resolve, check WHOIS
    try:
        w = whois.whois(domain)
        
        # Check if domain is registered
        if not w.domain_name:
            return True, None
            
        # Check expiration date if available
        if hasattr(w, 'expiration_date'):
            if isinstance(w.expiration_date, list):
                exp_date = w.expiration_date[0]
            else:
                exp_date = w.expiration_date
                
            if exp_date and exp_date < datetime.now():
                return True, w
                
        # If we have a domain name but no expiration date, assume it's registered
        return False, w
        
    except (whois.parser.PywhoisError, Exception) as e:
        # If we can't get WHOIS info, assume the domain is available
        # This is a simplification and might not be accurate in all cases
        return True, None


def get_domain_pricing(domain: str) -> Dict[str, Any]:
    """
    Get pricing information for a domain.
    
    Args:
        domain: The domain name to check pricing for
        
    Returns:
        Dictionary containing pricing information
    """
    # This is a placeholder implementation
    # In a real application, you would integrate with a domain registrar's API
    # like Namecheap, GoDaddy, etc.
    
    # For now, we'll use a simple heuristic to determine if a domain is premium
    # based on TLD and domain length
    tld = domain.split('.')[-1].lower()
    name = domain.split('.')[0]
    
    # Common premium TLDs
    premium_tlds = ['io', 'ai', 'co', 'app', 'dev']
    
    is_premium = (
        len(name) <= 5 or  # Short domains are premium
        tld in premium_tlds or  # Premium TLDs
        any(word in name for word in ['app', 'hq', 'inc', 'tech'])  # Common premium keywords
    )
    
    if is_premium:
        price = 99.99
    else:
        price = 12.99
    
    return {
        'is_premium': is_premium,
        'price': price,
        'currency': 'USD',
        'renewal_price': price * 1.2  # Renewal is typically more expensive
    }
