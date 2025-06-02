"""API endpoints for managing notifications."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from namesearch.api.deps import get_current_user as get_current_active_user, get_db
from namesearch.models.user import User
from namesearch.schemas.notification import (
    Notification as NotificationSchema,
    NotificationPreferences,
    NotificationPreferencesUpdate,
    NotificationUpdate,
    NotificationType
)
from namesearch.services.notification_service import NotificationService
from namesearch.crud.crud_notification import notification as crud_notification

router = APIRouter()

@router.get("/", response_model=List[NotificationSchema])
async def get_notifications(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve notifications for the current user.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        unread_only: Only return unread notifications
        current_user: Current authenticated user
        
    Returns:
        List of notifications
    """
    if unread_only:
        # Get unread notifications
        notifications = (
            db.query(crud_notification.model)
            .filter(
                crud_notification.model.user_id == current_user.id,
                crud_notification.model.read_at.is_(None)
            )
            .order_by(crud_notification.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    else:
        # Get all notifications
        notifications = crud_notification.get_multi_by_user(
            db, user_id=current_user.id, skip=skip, limit=limit
        )
    
    return notifications

@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get the count of unread notifications for the current user.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Dictionary with unread count
    """
    count = crud_notification.get_unread_count(db, user_id=current_user.id)
    return {"unread_count": count}

@router.get("/{notification_id}", response_model=NotificationSchema)
async def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific notification by ID.
    
    Args:
        notification_id: ID of the notification
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        The requested notification
    """
    notification = crud_notification.get(db, id=notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Ensure the notification belongs to the current user
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this notification"
        )
    
    return notification

@router.patch("/{notification_id}", response_model=NotificationSchema)
async def update_notification(
    notification_id: int,
    notification_in: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a notification.
    
    Args:
        notification_id: ID of the notification to update
        notification_in: Fields to update
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        The updated notification
    """
    notification = crud_notification.get(db, id=notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Ensure the notification belongs to the current user
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this notification"
        )
    
    # Handle marking as read
    update_data = notification_in.dict(exclude_unset=True)
    if "read" in update_data:
        if update_data["read"] and not notification.read_at:
            crud_notification.mark_as_read(db, db_obj=notification)
        del update_data["read"]
    
    # Update other fields if any
    if update_data:
        notification = crud_notification.update(
            db, db_obj=notification, obj_in=update_data
        )
    
    return notification

@router.delete("/{notification_id}", response_model=dict)
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a notification.
    
    Args:
        notification_id: ID of the notification to delete
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    notification = crud_notification.get(db, id=notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Ensure the notification belongs to the current user
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this notification"
        )
    
    crud_notification.remove(db, id=notification_id)
    return {"message": "Notification deleted successfully"}

@router.get("/preferences/", response_model=NotificationPreferences)
async def get_notification_preferences(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get the current user's notification preferences.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        The user's notification preferences
    """
    # In a real implementation, this would get the preferences from the database
    # For now, we'll return default preferences
    return NotificationPreferences()

@router.put("/preferences/", response_model=NotificationPreferences)
async def update_notification_preferences(
    preferences_in: NotificationPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update the current user's notification preferences.
    
    Args:
        preferences_in: New notification preferences
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        The updated notification preferences
    """
    # In a real implementation, this would update the preferences in the database
    # For now, we'll just return the input
    return preferences_in

@router.post("/test/{notification_type}", status_code=status.HTTP_201_CREATED)
async def send_test_notification(
    notification_type: NotificationType,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Send a test notification of the specified type.
    
    Args:
        notification_type: Type of notification to send
        background_tasks: Background tasks
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    notification_service = NotificationService(background_tasks=background_tasks)
    
    test_messages = {
        NotificationType.DOMAIN_AVAILABLE: "This domain is now available for registration!",
        NotificationType.DOMAIN_EXPIRING: "Your domain will expire in 7 days. Renew now to avoid losing it.",
        NotificationType.DOMAIN_CHANGED: "Changes have been detected for your domain.",
        NotificationType.DOMAIN_EXPIRED: "Your domain has expired. Renew it now to avoid losing it.",
        NotificationType.DOMAIN_TRANSFERRED: "Your domain has been successfully transferred to another registrar.",
    }
    
    message = test_messages.get(
        notification_type, 
        f"This is a test {notification_type.value} notification."
    )
    
    await notification_service.send_notification(
        db=db,
        user_id=current_user.id,
        type=notification_type,
        title=f"Test {notification_type.value.replace('_', ' ').title()}",
        message=message,
        data={"test": True},
        send_immediately=True
    )
    
    return {"message": f"Test {notification_type.value} notification sent successfully"}
