"""CRUD operations for notifications."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from ..models.notification import Notification, NotificationStatus
from ..schemas.notification import NotificationCreate, NotificationUpdate, NotificationType
from .base import CRUDBase

class CRUDNotification(CRUDBase[Notification, NotificationCreate, NotificationUpdate]):
    """CRUD operations for notifications."""
    
    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Notification]:
        """Get notifications for a specific user."""
        return (
            db.query(self.model)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_unread_count(self, db: Session, user_id: int) -> int:
        """Get count of unread notifications for a user."""
        return (
            db.query(self.model)
            .filter(
                Notification.user_id == user_id,
                Notification.read_at.is_(None)
            )
            .count()
        )
    
    def mark_as_read(
        self, db: Session, *, db_obj: Notification
    ) -> Notification:
        """Mark a notification as read."""
        if not db_obj.read_at:
            db_obj.read_at = datetime.utcnow()
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def mark_as_sent(
        self, db: Session, *, db_obj: Notification
    ) -> Notification:
        """Mark a notification as sent."""
        db_obj.status = NotificationStatus.SENT
        db_obj.sent_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def mark_as_failed(
        self, db: Session, *, db_obj: Notification, error: str = None
    ) -> Notification:
        """Mark a notification as failed."""
        db_obj.status = NotificationStatus.FAILED
        if error:
            if not db_obj.data:
                db_obj.data = {}
            db_obj.data["error"] = str(error)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def create_notification(
        self, 
        db: Session, 
        *, 
        user_id: int,
        type: NotificationType,
        title: str,
        message: str,
        data: Dict[str, Any] = None
    ) -> Notification:
        """Create a new notification."""
        notification_in = {
            "user_id": user_id,
            "type": type,
            "title": title,
            "message": message,
            "data": data or {}
        }
        return self.create(db, obj_in=notification_in)
    
    def get_pending_notifications(
        self, db: Session, *, limit: int = 100
    ) -> List[Notification]:
        """Get pending notifications that need to be sent."""
        return (
            db.query(self.model)
            .filter(Notification.status == NotificationStatus.PENDING)
            .order_by(Notification.created_at.asc())
            .limit(limit)
            .all()
        )

# Create singleton instance
notification = CRUDNotification(Notification)
