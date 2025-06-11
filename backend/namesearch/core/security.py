"""Security utilities for authentication and authorization."""
import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional, Union, Dict

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import ValidationError, EmailStr
from sqlalchemy.orm import Session
from jose.constants import ALGORITHMS

from .. import models, schemas
from ..db.session import get_db
from .config import settings
from .password import pwd_context, verify_password, get_password_hash

# Configure logging
logger = logging.getLogger(__name__)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")

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
        payload = decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    # Get user from database
    db_user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if db_user is None:
        raise credentials_exception
    return db_user

def get_current_user_optional(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> Optional[models.User]:
    """
    Get the current user from the token if available, otherwise return None.
    
    Args:
        db: Database session.
        token: Optional JWT token from the Authorization header.
        
    Returns:
        Optional[User]: The authenticated user if token is valid, None otherwise.
    """
    if not token:
        return None
        
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            return None
            
        user = db.query(models.User).filter(models.User.email == email).first()
        if user is None:
            return None
            
        return user
    except (JWTError, ValidationError):
        return None

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

def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: The subject to be stored in the token (usually user ID).
        expires_delta: Optional timedelta for token expiration.
        
    Returns:
        str: Encoded JWT token.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm="HS256"
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: The plain text password.
        hashed_password: The hashed password.
        
    Returns:
        bool: True if the password is valid, False otherwise.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """
    Generate a password hash.
    
    Args:
        password: The plain text password.
        
    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)

def validate_password_strength(password: str) -> bool:
    """
    Validate password strength.
    
    Args:
        password: The password to validate.
        
    Returns:
        bool: True if the password meets strength requirements.
        
    Raises:
        ValueError: If the password doesn't meet strength requirements.
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not any(c.islower() for c in password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one number")
    return True

def generate_password_reset_token(email: str) -> str:
    """
    Generate a password reset token.
    
    Args:
        email: The email to generate the token for.
        
    Returns:
        str: The generated token.
    """
    return create_token(
        subject=email,
        token_type="reset_password",
        expires_delta=timedelta(hours=1),
    )

def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and return the email if valid.
    
    Args:
        token: The password reset token.
        
    Returns:
        Optional[str]: The email if the token is valid, None otherwise.
    """
    try:
        payload = verify_token(token, token_type="reset_password")
        return payload.get("sub")
    except JWTError:
        return None

def decode_token(token: str) -> dict:
    """
    Decode a JWT token.
    
    Args:
        token: The JWT token to decode.
        
    Returns:
        dict: The decoded token payload.
        
    Raises:
        JWTError: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
        return payload
    except JWTError as e:
        raise e
