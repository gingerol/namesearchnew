"""Rate limiting utilities for API endpoints."""
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable, Any
from fastapi import HTTPException, status
from fastapi import Request
import time

class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests: int, window: int):
        """
        Initialize rate limiter.
        
        Args:
            requests: Number of requests allowed per window
            window: Time window in seconds
        """
        self.requests = requests
        self.window = window
        self.requests_log: Dict[str, list] = {}
    
    async def __call__(self, request: Request, key: Optional[str] = None) -> None:
        """
        Check if request is allowed.
        
        Args:
            request: FastAPI request object
            key: Optional custom key for rate limiting (defaults to client IP)
            
        Raises:
            HTTPException: If rate limit is exceeded
        """
        # Use client IP as default key if not provided
        client = key or request.client.host
        
        # Get current timestamp
        current_time = time.time()
        
        # Initialize request log for this client if it doesn't exist
        if client not in self.requests_log:
            self.requests_log[client] = []
        
        # Remove timestamps older than the current window
        self.requests_log[client] = [
            t for t in self.requests_log[client] 
            if current_time - t < self.window
        ]
        
        # Check if we've exceeded the rate limit
        if len(self.requests_log[client]) >= self.requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Rate limit exceeded",
                    "retry_after": int(self.requests_log[client][0] + self.window - current_time)
                }
            )
        
        # Add current request timestamp
        self.requests_log[client].append(current_time)
        
        # Clean up old entries (optional, to prevent memory leaks)
        if len(self.requests_log) > 1000:  # Keep only the 1000 most recent clients
            # Convert to list to avoid 'dictionary changed size during iteration'
            clients = list(self.requests_log.keys())
            for old_client in clients[500:]:  # Remove oldest 500 clients
                del self.requests_log[old_client]


# Create rate limiter instances
# 100 requests per minute per IP for regular endpoints
standard_limiter = RateLimiter(requests=100, window=60)

# 10 requests per minute per IP for expensive operations
strict_limiter = RateLimiter(requests=10, window=60)

# 1000 requests per day per IP for public endpoints
public_limiter = RateLimiter(requests=1000, window=60*60*24)
