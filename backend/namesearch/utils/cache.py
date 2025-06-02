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
    """Get a domain from cache if it exists and is not expired."""
    key = get_cache_key(domain)
    if key in _cache:
        cached = _cache[key]
        # Check if cache entry is still valid (1 hour TTL)
        if datetime.now() - cached['timestamp'] < timedelta(hours=1):
            return cached['data']
        del _cache[key]  # Remove expired entry
    return None

def cache_domain(domain: str, data: Dict) -> None:
    """Cache domain availability data."""
    key = get_cache_key(domain)
    _cache[key] = {
        'data': data,
        'timestamp': datetime.now()
    }

def clear_cache() -> None:
    """Clear the entire cache."""
    _cache.clear()
