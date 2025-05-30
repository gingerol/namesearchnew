"""User endpoints."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .... import crud, models
from ....core.security import get_current_active_superuser, get_current_user
from ....db.session import get_db
from ....schemas.user import User, UserCreate, UserUpdate, UserInDB

router = APIRouter()


@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Retrieve users (admin only).
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=User)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create new user (admin only).
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.get("/me", response_model=User)
def read_user_me(
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update own user.
    """
    # Handle password update separately if provided
    if user_in.new_password:
        if not user_in.current_password:
            raise HTTPException(
                status_code=400,
                detail="Current password is required to set a new password",
            )
        if not crud.user.authenticate(
            db, email=current_user.email, password=user_in.current_password
        ):
            raise HTTPException(status_code=400, detail="Incorrect password")
        
        # Update password
        current_user.hashed_password = crud.user.get_password_hash(user_in.new_password)
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        
        # Remove password from update data
        user_in = user_in.dict(exclude_unset=True)
        user_in.pop("current_password", None)
        user_in.pop("new_password", None)
        user_in = UserUpdate(**user_in)
    
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/{user_id}", response_model=User)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a user (admin only).
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=User)
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Delete a user (admin only).
    """
    # Don't allow deleting yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete yourself. Please ask another admin to do this."
        )
    
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    
    # Instead of deleting, mark as inactive
    user.is_active = False
    db.add(user)
    db.commit()
    return user
