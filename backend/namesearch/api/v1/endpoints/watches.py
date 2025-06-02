"""API endpoints for domain watching functionality."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .... import models, schemas
from ....core.security import get_current_active_user
from ....db.session import get_db
from ....services.domain_monitor_service import DomainMonitorService

router = APIRouter()

@router.post("/", response_model=schemas.DomainWatch, status_code=status.HTTP_201_CREATED)
async def create_domain_watch(
    *,
    db: Session = Depends(get_db),
    watch_in: schemas.DomainWatchCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new domain watch.
    
    This will start monitoring the specified domain for availability changes.
    """
    monitor_service = DomainMonitorService(db)
    try:
        # Create the watch
        domain_watch = monitor_service.create_watch(
            user_id=current_user.id,
            domain=watch_in.domain,
            check_frequency=watch_in.check_frequency,
            is_active=watch_in.is_active if hasattr(watch_in, 'is_active') else True,
        )
        db.commit()
        return domain_watch
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.get("/", response_model=List[schemas.DomainWatch])
def read_domain_watches(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve domain watches for the current user.
    """
    monitor_service = DomainMonitorService(db)
    return monitor_service.get_user_watches(
        user_id=current_user.id,
        skip=skip,
        limit=min(limit, 100),  # Enforce a reasonable limit
    )

@router.get("/{watch_id}", response_model=schemas.DomainWatch)
def read_domain_watch(
    *,
    db: Session = Depends(get_db),
    watch_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific domain watch by ID.
    """
    from ....crud import crud_domain_watch
    watch = crud_domain_watch.domain_watch.get(db, id=watch_id)
    if not watch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain watch not found"
        )
    if watch.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return watch

@router.patch("/{watch_id}", response_model=schemas.DomainWatch)
def update_domain_watch(
    *,
    db: Session = Depends(get_db),
    watch_id: int,
    watch_in: schemas.DomainWatchUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Update a domain watch.
    """
    from ....crud import crud_domain_watch
    
    # Verify the watch exists and belongs to the user
    domain_watch = crud_domain_watch.domain_watch.get(db, id=watch_id)
    if not domain_watch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain watch not found",
        )
    
    if domain_watch.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Update the watch using the service
    monitor_service = DomainMonitorService(db)
    updated_watch = monitor_service.update_watch(
        watch_id=watch_id,
        user_id=current_user.id,
        update_data=watch_in.dict(exclude_unset=True),
    )
    
    if not updated_watch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain watch not found",
        )
    
    db.commit()
    return updated_watch

@router.delete("/{watch_id}", response_model=dict)
def delete_domain_watch(
    *,
    db: Session = Depends(get_db),
    watch_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a domain watch.
    """
    from ....crud import crud_domain_watch
    
    # Verify the watch exists and belongs to the user
    domain_watch = crud_domain_watch.domain_watch.get(db, id=watch_id)
    if not domain_watch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain watch not found",
        )
    
    if domain_watch.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Delete the watch using the service
    monitor_service = DomainMonitorService(db)
    success = monitor_service.delete_watch(
        watch_id=watch_id,
        user_id=current_user.id,
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain watch not found",
        )
    
    db.commit()
    return {"message": "Domain watch deleted successfully"}

@router.post("/{watch_id}/check-now", response_model=schemas.DomainWatch)
async def check_domain_watch_now(
    *,
    db: Session = Depends(get_db),
    watch_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Manually trigger a domain check for a watch.
    """
    watch = crud.domain_watch.get(db, id=watch_id)
    if not watch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain watch not found"
        )
    if watch.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Force a check
    from ....utils.domain_checker import is_domain_available
    is_available, whois_data = is_domain_available(watch.domain)
    
    # Update watch status
    status = "available" if is_available else "taken"
    watch = crud.domain_watch.update_last_checked(
        db,
        db_obj=watch,
        status=status,
        whois_data=whois_data.to_dict() if whois_data and hasattr(whois_data, 'to_dict') else None
    )
    
    return watch
