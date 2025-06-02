"""CRUD operations for DomainWatch model."""
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session

from .. import models, schemas
from .base import CRUDBase

class CRUDDomainWatch(CRUDBase[models.DomainWatch, schemas.DomainWatchCreate, schemas.DomainWatchUpdate]):
    """CRUD operations for DomainWatch model."""
    
    def get_by_domain_and_user(
        self, db: Session, *, domain: str, user_id: int
    ) -> Optional[models.DomainWatch]:
        """Get a domain watch by domain and user ID."""
        return db.query(self.model).filter(
            self.model.domain == domain,
            self.model.user_id == user_id
        ).first()
    
    def get_active_watches(self, db: Session) -> List[models.DomainWatch]:
        """Get all active domain watches."""
        return db.query(self.model).filter(
            self.model.is_active == True  # noqa: E712
        ).all()
    
    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[models.DomainWatch]:
        """Get all domain watches for a user."""
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_with_user(
        self, db: Session, *, obj_in: schemas.DomainWatchCreate, user_id: int
    ) -> models.DomainWatch:
        """Create a new domain watch for a user."""
        # Check if watch already exists
        db_obj = self.get_by_domain_and_user(db, domain=obj_in.domain, user_id=user_id)
        if db_obj:
            # Update existing watch
            return self.update(db, db_obj=db_obj, obj_in=obj_in)
            
        # Create new watch
        db_obj = models.DomainWatch(
            **obj_in.dict(),
            user_id=user_id,
            last_checked=datetime.utcnow(),
            last_status="unknown"
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_last_checked(
        self, db: Session, *, db_obj: models.DomainWatch, status: str, whois_data: Optional[Dict[str, Any]] = None
    ) -> models.DomainWatch:
        """Update the last checked timestamp for a domain watch."""
        update_data = {
            "last_checked": datetime.utcnow(),
            "last_status": status
        }
        if whois_data:
            update_data["whois_data"] = whois_data
            
        return self.update(db, db_obj=db_obj, obj_in=update_data)

# Create instance
domain_watch = CRUDDomainWatch(models.DomainWatch)
