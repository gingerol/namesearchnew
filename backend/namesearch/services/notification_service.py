"""Notification service for sending and managing notifications."""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from ..core.config import settings
from ..crud.crud_user import user as crud_user
from ..crud.crud_notification import notification as crud_notification
from ..models.notification import Notification, NotificationStatus, NotificationType
from ..schemas.notification import NotificationCreate, NotificationPreferences
from ..schemas.user import User

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling notifications."""
    
    def __init__(self, background_tasks: Optional[BackgroundTasks] = None):
        """Initialize the notification service."""
        self.background_tasks = background_tasks
    
    async def send_notification(
        self,
        db: Session,
        user_id: int,
        type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        send_immediately: bool = True
    ) -> Notification:
        """
        Create and send a notification.
        
        Args:
            db: Database session
            user_id: ID of the user to notify
            type: Type of notification
            title: Notification title
            message: Notification message
            data: Additional data for the notification
            send_immediately: Whether to send the notification immediately
            
        Returns:
            The created notification
        """
        try:
            # Create the notification in the database
            notification = crud_notification.create_notification(
                db=db,
                user_id=user_id,
                type=type,
                title=title,
                message=message,
                data=data or {}
            )
            
            # If background tasks are available, queue the notification for sending
            if send_immediately and self.background_tasks:
                self.background_tasks.add_task(
                    self._send_pending_notifications,
                    db
                )
            
            return notification
            
        except Exception as e:
            logger.error(f"Failed to create notification: {str(e)}")
            raise
    
    async def send_domain_notification(
        self,
        db: Session,
        user_id: int,
        domain: str,
        notification_type: NotificationType,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """
        Send a domain-related notification.
        
        Args:
            db: Database session
            user_id: ID of the user to notify
            domain: Domain related to the notification
            notification_type: Type of domain notification
            message: Notification message
            data: Additional data for the notification
            
        Returns:
            The created notification
        """
        # Create a title based on the notification type
        titles = {
            NotificationType.DOMAIN_AVAILABLE: f"Domain {domain} is available",
            NotificationType.DOMAIN_EXPIRING: f"Domain {domain} is expiring soon",
            NotificationType.DOMAIN_CHANGED: f"Changes detected for {domain}",
            NotificationType.DOMAIN_EXPIRED: f"Domain {domain} has expired",
            NotificationType.DOMAIN_TRANSFERRED: f"Domain {domain} has been transferred"
        }
        
        title = titles.get(notification_type, f"Domain Notification: {domain}")
        
        # Add domain to data
        if data is None:
            data = {}
        data["domain"] = domain
        
        return await self.send_notification(
            db=db,
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data
        )
    
    async def _send_pending_notifications(self, db: Session) -> None:
        """
        Send all pending notifications.
        
        Args:
            db: Database session
        """
        try:
            # Get pending notifications
            pending = crud_notification.get_pending_notifications(db)
            
            for note in pending:
                try:
                    # Get user preferences
                    user = crud_user.get(db, note.user_id)
                    prefs = self._get_user_notification_preferences(user)
                    
                    # Check if we should send this type of notification
                    if not self._should_send_notification(note, prefs):
                        crud_notification.update(
                            db, db_obj=note, 
                            obj_in={"status": NotificationStatus.READ}
                        )
                        continue
                    
                    # Send the notification based on user preferences
                    if prefs.email_enabled:
                        await self._send_email_notification(db, note, user, prefs)
                    
                    if prefs.in_app_enabled:
                        # In-app notifications are already stored in the database
                        pass
                    
                    # Mark as sent
                    crud_notification.mark_as_sent(db, db_obj=note)
                    
                except Exception as e:
                    logger.error(f"Failed to send notification {note.id}: {str(e)}")
                    crud_notification.mark_as_failed(db, db_obj=note, error=str(e))
                    
        except Exception as e:
            logger.error(f"Error in notification sender: {str(e)}")
    
    async def _send_email_notification(
        self, 
        db: Session, 
        notification: Notification, 
        user: User,
        prefs: NotificationPreferences
    ) -> bool:
        """
        Send an email notification.
        
        Args:
            db: Database session
            notification: Notification to send
            user: User to notify
            prefs: User notification preferences
            
        Returns:
            bool: True if the email was sent successfully
        """
        # In a real implementation, this would use an email service
        # For now, we'll just log the email that would be sent
        logger.info(
            f"Sending email to {user.email}: {notification.title}\n"
            f"{notification.message}"
        )
        return True
    
    def _get_user_notification_preferences(
        self, user: User
    ) -> NotificationPreferences:
        """
        Get notification preferences for a user.
        
        Args:
            user: User to get preferences for
            
        Returns:
            Notification preferences
        """
        # In a real implementation, this would get the user's preferences from the database
        # For now, we'll return default preferences
        return NotificationPreferences(
            email_enabled=True,
            in_app_enabled=True,
            email_frequency="immediate",
            notify_on_available=True,
            notify_on_expiring=True,
            notify_on_changed=True,
            notify_on_expired=True,
            notify_on_transferred=True,
            expiration_reminder_days=[30, 7, 1]
        )
    
    def _should_send_notification(
        self, 
        notification: Notification, 
        prefs: NotificationPreferences
    ) -> bool:
        """
        Check if a notification should be sent based on user preferences.
        
        Args:
            notification: Notification to check
            prefs: User notification preferences
            
        Returns:
            bool: True if the notification should be sent
        """
        # Check if this type of notification is enabled
        type_enabled = {
            NotificationType.DOMAIN_AVAILABLE: prefs.notify_on_available,
            NotificationType.DOMAIN_EXPIRING: prefs.notify_on_expiring,
            NotificationType.DOMAIN_CHANGED: prefs.notify_on_changed,
            NotificationType.DOMAIN_EXPIRED: prefs.notify_on_expired,
            NotificationType.DOMAIN_TRANSFERRED: prefs.notify_on_transferred
        }.get(notification.type, True)
        
        if not type_enabled:
            return False
            
        # Add additional checks here (e.g., rate limiting, time of day, etc.)
        
        return True
