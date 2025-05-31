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
from ....schemas.user import User, UserCreate, UserInDB
from ..deps import get_current_user, get_db as get_db_dep

router = APIRouter()


@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    
    # Update last login
    user.update_last_login()
    db.commit()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/test-token", response_model=User)
async def test_token(current_user: models.User = Depends(get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


from fastapi import Response
from fastapi import status

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(get_db_dep),
    user_in: UserCreate = Body(...),
    response: Response
) -> Any:
    """
    Create new user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    user = crud.user.create(db, obj_in=user_in)
    # TODO: Send email verification
    response.status_code = status.HTTP_201_CREATED
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
