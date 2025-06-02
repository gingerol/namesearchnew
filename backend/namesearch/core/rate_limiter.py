"""Rate limiting utilities for API endpoints."""
import time
from typing import Callable, Optional, Dict, Any, Tuple
from functools import wraps
import redis
from fastapi import Request, HTTPException, status

from .config import settings

# Configure Redis connection
redis_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    """
    Get a Redis client instance.
    
    Returns:
        redis.Redis: A Redis client instance.
        
    Raises:
        RuntimeError: If Redis is not configured.
    """
    global redis_client
    if redis_client is None:
        if not settings.REDIS_URL:
            raise RuntimeError("Redis URL is not configured")
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client


def rate_limited(
    key_func: Callable[[Request], str],
    limit: int = 60,
    window: int = 60,
    block_duration: int = 300,
    scope: Optional[str] = None,
):
    """
    Decorator to rate limit API endpoints.
    
    Args:
        key_func: Function that extracts a key from the request (e.g., IP, user ID).
        limit: Maximum number of requests allowed in the time window.
        window: Time window in seconds.
        block_duration: How long to block the client after exceeding the limit (in seconds).
        scope: Optional scope for the rate limit (e.g., 'login', 'register').
        
    Returns:
        Decorator function.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Skip rate limiting in development if disabled
            if not settings.RATE_LIMIT:
                return await func(request, *args, **kwargs)
                
            try:
                client_key = key_func(request)
                if not client_key:
                    # If we can't identify the client, allow the request but log it
                    return await func(request, *args, **kwargs)
                    
                # Create a unique key for this rate limit
                prefix = f"rate_limit:{scope}:" if scope else "rate_limit:"
                key = f"{prefix}{client_key}"
                
                # Get Redis client
                r = get_redis()
                
                # Check if the client is blocked
                block_key = f"{key}:blocked"
                is_blocked = r.get(block_key)
                if is_blocked:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail={
                            "message": "Too many requests. Please try again later.",
                            "retry_after": int(float(is_blocked) - time.time()),
                            "code": "rate_limit_exceeded"
                        },
                        headers={"Retry-After": str(int(float(is_blocked) - time.time()))}
                    )
                
                # Use a pipeline for atomic operations
                with r.pipeline() as pipe:
                    pipe.multi()
                    
                    # Increment the request count
                    pipe.incr(key)
                    
                    # Set expiration if this is the first request in the window
                    pipe.ttl(key)
                    ttl = pipe.execute()[-1]
                    if ttl == -1:  # Key exists but has no TTL
                        pipe.expire(key, window)
                        pipe.execute()
                
                # Get the current count
                count = int(r.get(key) or 0)
                
                # Calculate remaining requests and reset time
                remaining = max(0, limit - count)
                reset_time = int(time.time() + (ttl if ttl > 0 else window))
                
                # Set headers
                request.scope["rate_limit"] = {
                    "limit": limit,
                    "remaining": remaining,
                    "reset": reset_time,
                }
                
                # Check if rate limit exceeded
                if remaining <= 0:
                    # Block the client
                    r.setex(block_key, block_duration, int(time.time() + block_duration))
                    
                    # Log the incident
                    logger.warning(
                        f"Rate limit exceeded for {client_key} on {request.url.path} "
                        f"({count} requests in {window}s)"
                    )
                    
                    # Raise 429 Too Many Requests
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail={
                            "message": "Too many requests. Please try again later.",
                            "retry_after": block_duration,
                            "code": "rate_limit_exceeded"
                        },
                        headers={
                            "X-RateLimit-Limit": str(limit),
                            "X-RateLimit-Remaining": "0",
                            "X-RateLimit-Reset": str(reset_time),
                            "Retry-After": str(block_duration)
                        }
                    )
                
                # Add rate limit headers to the response
                response = await func(request, *args, **kwargs)
                response.headers["X-RateLimit-Limit"] = str(limit)
                response.headers["X-RateLimit-Remaining"] = str(remaining - 1)
                response.headers["X-RateLimit-Reset"] = str(reset_time)
                
                return response
                
            except redis.RedisError as e:
                # If Redis is down, log the error but allow the request
                logger.error(f"Redis error in rate limiter: {str(e)}")
                return await func(request, *args, **kwargs)
                
        return wrapper
    return decorator


def get_client_ip(request: Request) -> str:
    """
    Get the client's IP address from the request.
    
    Args:
        request: The FastAPI request object.
        
    Returns:
        str: The client's IP address.
    """
    # Get the client's IP address, considering X-Forwarded-For header
    if "x-forwarded-for" in request.headers:
        # Get the first IP in the X-Forwarded-For header
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"
    
    return client_ip


def get_rate_limit_key(prefix: str = "") -> Callable[[Request], str]:
    """
    Get a function that generates a rate limit key based on client IP and path.
    
    Args:
        prefix: Optional prefix for the rate limit key.
        
    Returns:
        Callable: A function that takes a Request and returns a rate limit key.
    """
    def key_func(request: Request) -> str:
        client_ip = get_client_ip(request)
        path = request.url.path
        return f"{prefix}:{client_ip}:{path}"
    
    return key_func


# Common rate limiters
rate_limited_per_ip = rate_limited(
    key_func=get_client_ip,
    limit=settings.RATE_LIMIT_PER_MINUTE,
    window=60,  # 1 minute
    block_duration=300,  # 5 minutes
    scope="ip"
)

rate_limited_per_endpoint = rate_limited(
    key_func=get_rate_limit_key("endpoint"),
    limit=settings.RATE_LIMIT_PER_HOUR,
    window=3600,  # 1 hour
    block_duration=3600,  # 1 hour
    scope="endpoint"
)

# Special rate limiters for authentication endpoints
login_rate_limiter = rate_limited(
    key_func=lambda r: f"login:{get_client_ip(r)}",
    limit=5,  # 5 attempts
    window=300,  # 5 minutes
    block_duration=900,  # 15 minutes
    scope="login"
)

register_rate_limiter = rate_limited(
    key_func=lambda r: f"register:{get_client_ip(r)}",
    limit=3,  # 3 attempts
    window=86400,  # 24 hours
    block_duration=86400,  # 24 hours
    scope="register"
)

password_reset_rate_limiter = rate_limited(
    key_func=lambda r: f"password_reset:{get_client_ip(r)}",
    limit=3,  # 3 attempts
    window=3600,  # 1 hour
    block_duration=3600,  # 1 hour
    scope="password_reset"
)
