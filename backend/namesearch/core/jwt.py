"""JWT token utilities for authentication."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from . import models, schemas
from .config import settings
from .security import verify_password
from .db.session import get_db

# Configure logging
logger = logging.getLogger(__name__)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token"
)


def create_access_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a new access token.
    
    Args:
        subject: The subject of the token (usually user ID).
        expires_delta: Optional timedelta for token expiration.
        additional_claims: Additional claims to include in the token.
        
    Returns:
        str: The encoded JWT access token.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return _create_token(
        subject=subject,
        expires_delta=expires_delta,
        token_type="access",
        additional_claims=additional_claims,
    )


def create_refresh_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a new refresh token.
    
    Args:
        subject: The subject of the token (usually user ID).
        expires_delta: Optional timedelta for token expiration.
        
    Returns:
        str: The encoded JWT refresh token.
    """
    if expires_delta is None:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    return _create_token(
        subject=subject,
        expires_delta=expires_delta,
        token_type="refresh",
    )


def _create_token(
    subject: Union[str, int],
    expires_delta: timedelta,
    token_type: str,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a JWT token with the given parameters.
    
    Args:
        subject: The subject of the token.
        expires_delta: Time until the token expires.
        token_type: Type of token (e.g., 'access', 'refresh').
        additional_claims: Additional claims to include in the token.
        
    Returns:
        str: The encoded JWT token.
    """
    now = datetime.utcnow()
    expire = now + expires_delta
    
    # Standard claims
    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": token_type,
    }
    
    # Add additional claims if provided
    if additional_claims:
        to_encode.update(additional_claims)
    
    # Encode the token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    return encoded_jwt


def verify_token(
    token: str,
    token_type: Optional[str] = None,
    leeway: int = 0,
) -> Dict[str, Any]:
    """
    Verify a JWT token.
    
    Args:
        token: The JWT token to verify.
        token_type: Expected token type (e.g., 'access', 'refresh').
        leeway: Leeway in seconds for expiration time.
        
    Returns:
        Dict[str, Any]: The decoded token payload.
        
    Raises:
        JWTError: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"leeway": leeway},
        )
        
        # Check token type if specified
        if token_type and payload.get("type") != token_type:
            raise JWTError(f"Invalid token type: {payload.get('type')}")
            
        return payload
    except JWTError as e:
        logger.error(f"JWT Error: {str(e)}")
        raise


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> models.User:
    """
    Get the current user from the token.
    
    Args:
        db: Database session.
        token: JWT token from the Authorization header.
        
    Returns:
        User: The authenticated user.
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token, token_type="access")
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        logger.error(f"Token validation error: {str(e)}")
        raise credentials_exception from e
    
    # Get user from database
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
        
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Get the current active user.
    
    Args:
        current_user: The authenticated user.
        
    Returns:
        User: The active user.
        
    Raises:
        HTTPException: If the user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Get the current active superuser.
    
    Args:
        current_user: The authenticated user.
        
    Returns:
        User: The active superuser.
        
    Raises:
        HTTPException: If the user is not a superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user


def authenticate_user(
    db: Session, email: str, password: str
) -> Optional[models.User]:
    """
    Authenticate a user with email and password.
    
    Args:
        db: Database session.
        email: User's email.
        password: Plain text password.
        
    Returns:
        Optional[User]: The authenticated user if successful, None otherwise.
    """
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        # Hash a dummy password to prevent timing attacks
        verify_password("dummy-password", "dummy-hash")
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
