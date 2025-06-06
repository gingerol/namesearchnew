"""Caching utilities for domain availability checks."""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import hashlib

# In-memory cache (replace with Redis in production)
_cache: Dict[str, Dict] = {}

def get_cache_key(domain: str) -> str:
    """Generate a cache key for a domain."""
    return hashlib.md5(domain.lower().encode()).hexdigest()

def get_cached_domain(domain: str) -> Optional[Dict]:
    """
    Get a domain from cache if it exists and is not expired.
    
    Args:
        domain: The domain name to retrieve from cache
        
    Returns:
        Cached data if found and not expired, None otherwise
    """
    key = get_cache_key(domain)
    if key in _cache:
        cached = _cache[key]
        
        # Check if cache entry has an explicit expiration
        if 'expires_at' in cached and cached['expires_at'] is not None:
            if datetime.now() < cached['expires_at']:
                return cached['data']
        # Fall back to default TTL (1 hour)
        elif datetime.now() - cached['timestamp'] < timedelta(hours=1):
            return cached['data']
            
        # Entry is expired, remove it
        del _cache[key]
    return None

def cache_domain(domain: str, data: Dict, ttl: Optional[int] = None) -> None:
    """
    Cache domain availability data.
    
    Args:
        domain: The domain name to cache
        data: The data to cache
        ttl: Time to live in seconds (optional, defaults to 1 hour)
    """
    key = get_cache_key(domain)
    _cache[key] = {
        'data': data,
        'timestamp': datetime.now(),
        'expires_at': datetime.now() + timedelta(seconds=ttl) if ttl else None
    }

def clear_cache() -> None:
    """Clear the entire cache."""
    _cache.clear()
