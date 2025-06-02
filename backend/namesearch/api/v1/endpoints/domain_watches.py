"""API endpoints for managing domain watches."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from namesearch.api.deps import get_current_active_user, get_db
from namesearch.models.user import User
from namesearch.schemas.domain_watch import (
    DomainWatch as DomainWatchSchema,
    DomainWatchCreate,
    DomainWatchUpdate,
)
from namesearch.services.domain_monitor_service import DomainMonitorService

router = APIRouter()


@router.post("/", response_model=DomainWatchSchema, status_code=status.HTTP_201_CREATED)
async def create_domain_watch(
    *,
    db: Session = Depends(get_db),
    domain_watch_in: DomainWatchCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new domain watch.
    
    Args:
        db: Database session
        domain_watch_in: Domain watch data
        current_user: Current authenticated user
        
    Returns:
        The created domain watch
    """
    monitor_service = DomainMonitorService()
    try:
        domain_watch = monitor_service.create_watch(
            db=db,
            user_id=current_user.id,
            domain=domain_watch_in.domain,
            check_frequency=domain_watch_in.check_frequency,
            is_active=domain_watch_in.is_active,
        )
        db.commit()
        return domain_watch
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create domain watch: {str(e)}",
        ) from e


@router.get("/", response_model=List[DomainWatchSchema])
async def read_domain_watches(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve domain watches for the current user.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated user
        
    Returns:
        List of domain watches
    """
    monitor_service = DomainMonitorService()
    try:
        return monitor_service.get_user_watches(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to retrieve domain watches: {str(e)}",
        ) from e


@router.get("/{watch_id}", response_model=DomainWatchSchema)
async def read_domain_watch(
    watch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific domain watch by ID.
    
    Args:
        watch_id: ID of the domain watch
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        The requested domain watch
    """
    monitor_service = DomainMonitorService()
    try:
        domain_watch = monitor_service.get_watch(
            db=db,
            watch_id=watch_id,
            user_id=current_user.id
        )
        
        if not domain_watch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain watch not found or access denied",
            )
            
        return domain_watch
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to retrieve domain watch: {str(e)}",
        ) from e


@router.put("/{watch_id}", response_model=DomainWatchSchema)
async def update_domain_watch(
    watch_id: int,
    domain_watch_in: DomainWatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a domain watch.
    
    Args:
        watch_id: ID of the domain watch to update
        domain_watch_in: Fields to update
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        The updated domain watch
    """
    monitor_service = DomainMonitorService()
    
    try:
        # Update the watch
        updated_watch = monitor_service.update_watch(
            db=db,
            watch_id=watch_id,
            user_id=current_user.id,
            update_data=domain_watch_in.dict(exclude_unset=True)
        )
        
        if not updated_watch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain watch not found or access denied",
            )
            
        db.commit()
        return updated_watch
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update domain watch: {str(e)}",
        ) from e


@router.delete("/{watch_id}", response_model=dict)
async def delete_domain_watch(
    watch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a domain watch.
    
    Args:
        watch_id: ID of the domain watch to delete
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    monitor_service = DomainMonitorService()
    
    try:
        success = monitor_service.delete_watch(
            db=db,
            watch_id=watch_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain watch not found or access denied",
            )
            
        db.commit()
        return {"message": "Domain watch deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete domain watch: {str(e)}",
        ) from e


@router.post("/{watch_id}/check-now", response_model=DomainWatchSchema)
async def check_domain_now(
    watch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Manually trigger a domain check for a specific watch.
    
    Args:
        watch_id: ID of the domain watch to check
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        The updated domain watch with fresh data
    """
    monitor_service = DomainMonitorService()
    
    try:
        # Get the watch first to verify ownership
        existing_watch = monitor_service.get_watch(
            db=db,
            watch_id=watch_id,
            user_id=current_user.id
        )
        
        if not existing_watch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain watch not found or access denied",
            )
        
        # Process the watch immediately
        await monitor_service._process_watch(db, existing_watch)
        db.refresh(existing_watch)
        return existing_watch
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to check domain: {str(e)}",
        ) from e
