"""Authentication endpoints."""
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .... import crud, models
from ....core import security
from ....core.config import settings
from ....db.session import get_db
from ....schemas.token import Token, TokenResponse, TokenData
from ....schemas.user import User, UserCreate, UserInDB, UserResponse
from ..deps import get_current_user, get_db as get_db_dep

router = APIRouter()


@router.post("/login/access-token", response_model=TokenResponse)
async def login_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token and refresh token for future requests
    """
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not crud.user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Inactive user"
        )
    
    # Update last login
    user.update_last_login()
    db.commit()
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    refresh_token = security.create_refresh_token(
        user.id, expires_delta=refresh_token_expires
    )
    
    # Store refresh token in database
    crud.token.create(db, obj_in={
        "user_id": user.id,
        "token": refresh_token,
        "expires_at": datetime.utcnow() + refresh_token_expires
    })
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds())
    }


@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a new access token using a refresh token
    """
    # Verify refresh token
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = security.verify_token(refresh_token)
        if payload is None:
            raise credentials_exception
            
        token_data = TokenData(**payload)
        if token_data.email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Check if refresh token exists in database
    db_token = crud.token.get_by_token(db, token=refresh_token)
    if not db_token or db_token.revoked or db_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    # Get user
    user = crud.user.get(db, id=token_data.sub)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds())
    }


@router.get("/test-token", response_model=UserResponse)
async def test_token(current_user: models.User = Depends(get_current_user)):
    """
    Test access token
    """
    return current_user


from fastapi import Response
from fastapi import status

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    *,
    db: Session = Depends(get_db_dep),
    user_in: UserCreate,
) -> Any:
    """
    Register a new user account.
    """
    # Check if user with this email already exists
    if crud.user.get_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    
    # Create user
    user = crud.user.create(db, obj_in=user_in)
    
    # Generate email verification token
    verification_token = security.create_email_verification_token(user.email)
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
    
    # Send verification email (in production, this would be async)
    if settings.EMAILS_ENABLED:
        try:
            await send_verification_email(
                email_to=user.email,
                username=user.full_name or user.email,
                verification_url=verification_url,
            )
        except Exception as e:
            logger.error(f"Error sending verification email: {e}")
            # Don't fail the request if email sending fails
    
    return user


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED, response_model=dict)
def forgot_password(
    user_in: dict = Body(...),
    db: Session = Depends(get_db_dep)
) -> Any:
    """
    Password Recovery: Always return 202 to prevent email enumeration.
    """
    email = user_in.get("email")
    user = crud.user.get_by_email(db, email=email)
    # TODO: Send password reset email if user exists
    return {"msg": "If the email exists, a password reset link will be sent"}


@router.post("/password-recovery/{email}", response_model=schemas.Msg)
async def recover_password(
    email: str, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Initiate password recovery process.
    """
    user = crud.user.get_by_email(db, email=email)
    
    # Always return 202 to prevent email enumeration
    if not user or not user.is_active:
        return {"msg": "If your email is registered, you will receive a password reset link."}
    
    # Generate password reset token
    password_reset_token = security.create_password_reset_token(email=email)
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={password_reset_token}"
    
    # Send password reset email (in production, this would be async)
    if settings.EMAILS_ENABLED:
        try:
            await send_password_reset_email(
                email_to=user.email,
                username=user.full_name or user.email,
                reset_url=reset_url,
            )
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
    
    return {"msg": "If your email is registered, you will receive a password reset link."}


@router.post("/reset-password/", response_model=dict)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db_dep),
) -> Any:
    """
    Reset password
    """
    from namesearch.core.security import decode_token
    from namesearch.core.password import get_password_hash
    from jose import JWTError

    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"msg": "Password updated successfully"}
