"""Session management utilities for user authentication."""
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from . import models, schemas
from .config import settings
from .db.session import get_db
from .jwt import oauth2_scheme

# Configure logging
logger = logging.getLogger(__name__)

# Redis client for session storage
_redis_client: Optional[redis.Redis] = None

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token"
)

# Token types
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

# Session key prefixes
SESSION_PREFIX = "session:"
USER_SESSIONS_PREFIX = "user_sessions:"
TOKEN_BLACKLIST_PREFIX = "token_blacklist:"


def get_redis() -> redis.Redis:
    """
    Get a Redis client instance.
    
    Returns:
        redis.Redis: A Redis client instance.
        
    Raises:
        RuntimeError: If Redis is not configured.
    """
    global _redis_client
    if _redis_client is None:
        if not settings.REDIS_URL:
            raise RuntimeError("Redis URL is not configured")
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=False)
    return _redis_client


def create_session(
    db: Session,
    user_id: int,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> schemas.Session:
    """
    Create a new user session.
    
    Args:
        db: Database session.
        user_id: ID of the user.
        user_agent: User agent string from the request.
        ip_address: IP address of the client.
        metadata: Additional session metadata.
        
    Returns:
        Session: The created session object.
    """
    # Generate session ID and tokens
    session_id = str(uuid4())
    
    # Create access and refresh tokens
    access_token = create_access_token(
        subject=user_id,
        additional_claims={"session_id": session_id}
    )
    
    refresh_token = create_refresh_token(
        subject=user_id,
    )
    
    # Calculate token expiration times
    now = datetime.utcnow()
    access_token_expires = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Create session data
    session_data = {
        "id": session_id,
        "user_id": user_id,
        "user_agent": user_agent,
        "ip_address": ip_address,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "access_token_expires": access_token_expires.isoformat(),
        "refresh_token_expires": refresh_token_expires.isoformat(),
        "created_at": now.isoformat(),
        "last_used_at": now.isoformat(),
        "is_active": True,
        "metadata": metadata or {},
    }
    
    # Store session in Redis
    redis_client = get_redis()
    session_key = f"{SESSION_PREFIX}{session_id}"
    
    # Set session data with expiration (slightly longer than refresh token)
    redis_client.set(
        name=session_key,
        value=json.dumps(session_data, default=str),
        ex=int(settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600 * 1.1)  # 10% longer
    )
    
    # Add to user's session set
    user_sessions_key = f"{USER_SESSIONS_PREFIX}{user_id}"
    redis_client.sadd(user_sessions_key, session_id)
    
    # Set expiration on the user's session set
    redis_client.expire(
        user_sessions_key,
        int(settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600 * 1.1)
    )
    
    # Convert to Pydantic model
    return schemas.Session(**session_data)


def get_session(session_id: str) -> Optional[schemas.Session]:
    """
    Get a session by ID.
    
    Args:
        session_id: The session ID.
        
    Returns:
        Optional[Session]: The session if found, None otherwise.
    """
    redis_client = get_redis()
    session_key = f"{SESSION_PREFIX}{session_id}"
    session_data = redis_client.get(session_key)
    
    if not session_data:
        return None
    
    try:
        session_dict = json.loads(session_data)
        return schemas.Session(**session_dict)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Error decoding session data: {str(e)}")
        return None


def get_user_sessions(user_id: int) -> List[schemas.Session]:
    """
    Get all active sessions for a user.
    
    Args:
        user_id: The user ID.
        
    Returns:
        List[Session]: List of active sessions.
    """
    redis_client = get_redis()
    user_sessions_key = f"{USER_SESSIONS_PREFIX}{user_id}"
    session_ids = redis_client.smembers(user_sessions_key)
    
    sessions = []
    for session_id in session_ids:
        session = get_session(session_id.decode())
        if session and session.is_active:
            sessions.append(session)
    
    return sessions


def revoke_session(session_id: str, user_id: Optional[int] = None) -> bool:
    """
    Revoke a session.
    
    Args:
        session_id: The session ID to revoke.
        user_id: Optional user ID for additional validation.
        
    Returns:
        bool: True if the session was revoked, False otherwise.
    """
    session = get_session(session_id)
    if not session or not session.is_active:
        return False
    
    # Additional validation if user_id is provided
    if user_id is not None and session.user_id != user_id:
        return False
    
    # Add tokens to blacklist
    redis_client = get_redis()
    
    # Blacklist access token with remaining TTL
    if session.access_token:
        access_token_key = f"{TOKEN_BLACKLIST_PREFIX}{session.access_token}"
        ttl = (datetime.fromisoformat(session.access_token_expires) - datetime.utcnow()).total_seconds()
        if ttl > 0:
            redis_client.set(access_token_key, "revoked", ex=int(ttl))
    
    # Blacklist refresh token with remaining TTL
    if session.refresh_token:
        refresh_token_key = f"{TOKEN_BLACKLIST_PREFIX}{session.refresh_token}"
        ttl = (datetime.fromisoformat(session.refresh_token_expires) - datetime.utcnow()).total_seconds()
        if ttl > 0:
            redis_client.set(refresh_token_key, "revoked", ex=int(ttl))
    
    # Mark session as inactive
    session.is_active = False
    session_key = f"{SESSION_PREFIX}{session_id}"
    redis_client.set(
        name=session_key,
        value=session.json(),
        ex=int(settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600 * 1.1)
    )
    
    # Remove from user's active sessions set
    user_sessions_key = f"{USER_SESSIONS_PREFIX}{session.user_id}"
    redis_client.srem(user_sessions_key, session_id)
    
    return True


def revoke_all_sessions(user_id: int, exclude_session_id: Optional[str] = None) -> int:
    """
    Revoke all sessions for a user, optionally excluding one.
    
    Args:
        user_id: The user ID.
        exclude_session_id: Optional session ID to exclude from revocation.
        
    Returns:
        int: Number of sessions revoked.
    """
    sessions = get_user_sessions(user_id)
    revoked_count = 0
    
    for session in sessions:
        if exclude_session_id and session.id == exclude_session_id:
            continue
        if revoke_session(session.id, user_id):
            revoked_count += 1
    
    return revoked_count


def is_token_revoked(token: str) -> bool:
    """
    Check if a token has been revoked.
    
    Args:
        token: The JWT token to check.
        
    Returns:
        bool: True if the token is revoked, False otherwise.
    """
    redis_client = get_redis()
    token_key = f"{TOKEN_BLACKLIST_PREFIX}{token}"
    return redis_client.exists(token_key) > 0


# Dependencies for FastAPI
def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """
    Get the current user from the JWT token.
    
    Args:
        security_scopes: Security scopes required for the endpoint.
        token: The JWT token from the Authorization header.
        db: Database session.
        
    Returns:
        User: The authenticated user.
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't have the required scopes.
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope=\"{}\"'.format(" ".join(security_scopes.scopes))
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        # Check if token is blacklisted
        if is_token_revoked(token):
            raise credentials_exception
        
        # Verify the token
        payload = verify_token(token, token_type=TOKEN_TYPE_ACCESS)
        user_id: str = payload.get("sub")
        session_id: str = payload.get("session_id")
        
        if user_id is None or session_id is None:
            raise credentials_exception
            
        # Verify the session
        session = get_session(session_id)
        if not session or not session.is_active or session.user_id != int(user_id):
            raise credentials_exception
            
        # Get the user from the database
        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        if user is None:
            raise credentials_exception
            
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Check scopes if required
        if security_scopes.scopes:
            token_scopes = payload.get("scopes", [])
            for scope in security_scopes.scopes:
                if scope not in token_scopes:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Not enough permissions",
                        headers={"WWW-Authenticate": authenticate_value},
                    )
        
        # Update session last used time
        session.last_used_at = datetime.utcnow().isoformat()
        session_key = f"{SESSION_PREFIX}{session_id}"
        redis_client = get_redis()
        redis_client.set(
            name=session_key,
            value=session.json(),
            ex=int(settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600 * 1.1)
        )
        
        return user
        
    except (JWTError, ValidationError) as e:
        logger.error(f"Token validation error: {str(e)}")
        raise credentials_exception from e
