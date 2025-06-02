"""Domain monitoring service for tracking domain availability changes."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, TYPE_CHECKING
from sqlalchemy.orm import Session

from fastapi import HTTPException, status, BackgroundTasks

from ..crud.domain_watch import domain_watch as crud_domain_watch
from ..models.domain_watch import DomainWatch
from ..schemas.domain_watch import DomainWatchCreate, DomainWatchUpdate
from .whois_service import whois_service
from .notification_service import NotificationService, NotificationType

if TYPE_CHECKING:
    from ..models.user import User
    from ..db.session import SessionLocal

logger = logging.getLogger(__name__)

class DomainMonitorService:
    """Service for managing domain monitoring."""
    
    def __init__(self, background_tasks: Optional[BackgroundTasks] = None):
        """
        Initialize the domain monitor service.
        
        Args:
            background_tasks: Optional FastAPI BackgroundTasks instance for sending notifications
        """
        self._monitoring = False
        self._monitor_task = None
        self.notification_service = NotificationService(background_tasks=background_tasks)
    
    async def start(self, db: Session, check_interval: int = 300):
        """Start the domain monitoring service.
        
        Args:
            db: Database session
            check_interval: How often to check for domains to monitor (in seconds)
        """
        if self._monitoring:
            logger.warning("Domain monitoring is already running")
            return
            
        self._monitoring = True
        logger.info(f"Started domain monitoring service with {check_interval}s check interval")
        
        # Run the monitor in a separate task
        self._monitor_task = asyncio.create_task(self._monitor_loop(db, check_interval))
    
    async def stop(self) -> None:
        """Stop the domain monitoring service."""
        if not self._monitoring:
            return
            
        logger.info("Stopping domain monitor")
        self._monitoring = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                logger.info("Domain monitor stopped")
    
    async def _monitor_loop(self, db: Session, check_interval: int = 300):
        """Background task to monitor domain watches.
        
        Args:
            db: Database session
            check_interval: Seconds between monitoring cycles
        """
        logger.info("Starting domain monitor loop")
        
        while self._monitoring:
            try:
                # Get all active watches
                watches = crud_domain_watch.get_active_watches(db)
                
                if not watches:
                    logger.debug("No active domain watches to monitor")
                    await asyncio.sleep(check_interval)
                    continue
                
                logger.info(f"Checking {len(watches)} active domain watches")
                
                # Process each watch
                for watch in watches:
                    try:
                        await self._process_watch(db, watch)
                    except Exception as e:
                        logger.error(f"Error processing watch {watch.id}: {str(e)}")
                
                # Wait for the next check interval
                await asyncio.sleep(check_interval)
                
            except asyncio.CancelledError:
                logger.info("Domain monitor loop cancelled")
                raise
            except Exception as e:
                logger.error(f"Error in domain monitor loop: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying after error
    
    async def _process_watch(self, db: Session, watch: DomainWatch) -> None:
        """Process a single domain watch.
        
        Args:
            db: Database session
            watch: Domain watch to process
        """
        try:
            # Get current WHOIS data
            whois_data = await whois_service.lookup_domain(watch.domain)
            
            # Store the previous status for change detection
            previous_status = watch.last_status
            
            # Update the watch with the latest data
            watch.last_checked = datetime.utcnow()
            watch.last_status = whois_data.get('status', 'unknown')
            watch.whois_data = whois_data
            
            db.add(watch)
            db.commit()
            db.refresh(watch)
            
            logger.info(f"Processed domain watch for {watch.domain}: {watch.last_status}")
            
            # Check for status changes and send notifications if needed
            await self._check_for_domain_changes(
                db=db,
                watch=watch,
                previous_status=previous_status,
                whois_data=whois_data
            )
            
        except Exception as e:
            logger.error(f"Error processing domain watch {watch.id}: {str(e)}")
            db.rollback()
    
    async def _check_for_domain_changes(
        self,
        db: Session,
        watch: DomainWatch,
        previous_status: Optional[str],
        whois_data: Dict[str, Any]
    ) -> None:
        """Check for domain changes and send notifications if needed.
        
        Args:
            db: Database session
            watch: Domain watch that was processed
            previous_status: Previous status of the domain
            whois_data: Current WHOIS data
        """
        current_status = whois_data.get('status', 'unknown')
        
        # Skip if this is the first check
        if previous_status is None:
            logger.info(f"Initial check for {watch.domain}, no previous status to compare")
            return
        
        # Check for status changes
        if current_status != previous_status:
            logger.info(f"Status changed for {watch.domain}: {previous_status} -> {current_status}")
            
            # Determine notification type based on status change
            notification_type = None
            message = f"Domain {watch.domain} status changed from {previous_status} to {current_status}"
            
            if current_status == 'available':
                notification_type = NotificationType.DOMAIN_AVAILABLE
                message = f"Domain {watch.domain} is now available for registration!"
            elif current_status == 'expired':
                notification_type = NotificationType.DOMAIN_EXPIRED
                message = f"Domain {watch.domain} has expired. Renew it now to avoid losing it."
            elif 'expir' in current_status.lower() and 'soon' in current_status.lower():
                notification_type = NotificationType.DOMAIN_EXPIRING
                message = f"Domain {watch.domain} is expiring soon. Renew it to keep your domain."
            else:
                notification_type = NotificationType.DOMAIN_CHANGED
            
            # Send notification if we have a type
            if notification_type:
                try:
                    await self.notification_service.send_domain_notification(
                        db=db,
                        user_id=watch.user_id,
                        domain=watch.domain,
                        notification_type=notification_type,
                        message=message,
                        data={
                            "previous_status": previous_status,
                            "current_status": current_status,
                            "whois_data": whois_data
                        }
                    )
                    logger.info(f"Sent {notification_type} notification for {watch.domain}")
                except Exception as e:
                    logger.error(f"Failed to send notification for {watch.domain}: {str(e)}")
        
        # Check for expiration date changes
        expiration_date = whois_data.get('expiration_date')
        if expiration_date and isinstance(expiration_date, str):
            try:
                # Parse the expiration date if it's a string
                if isinstance(expiration_date, str):
                    expiration_date = datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
                
                # Check if domain is expiring soon (within 30 days)
                days_until_expiry = (expiration_date - datetime.utcnow()).days
                
                if 0 < days_until_expiry <= 30:
                    # Send expiring notification if we haven't already
                    notification_type = NotificationType.DOMAIN_EXPIRING
                    message = (
                        f"Domain {watch.domain} will expire in {days_until_expiry} days. "
                        f"Expiration date: {expiration_date.strftime('%Y-%m-%d')}"
                    )
                    
                    try:
                        await self.notification_service.send_domain_notification(
                            db=db,
                            user_id=watch.user_id,
                            domain=watch.domain,
                            notification_type=notification_type,
                            message=message,
                            data={
                                "expiration_date": expiration_date.isoformat(),
                                "days_until_expiry": days_until_expiry
                            }
                        )
                        logger.info(f"Sent expiring notification for {watch.domain} ({days_until_expiry} days left)")
                    except Exception as e:
                        logger.error(f"Failed to send expiring notification for {watch.domain}: {str(e)}")
                        
            except (ValueError, TypeError) as e:
                logger.warning(f"Error parsing expiration date for {watch.domain}: {str(e)}")
            
        # No need to save updates here as they're already handled in _process_watch
    
    def create_watch(
        self, 
        db: Session,
        user_id: int, 
        domain: str, 
        check_frequency: int = 60,
        is_active: bool = True
    ) -> DomainWatch:
        """Create a new domain watch.
        
        Args:
            db: Database session
            user_id: ID of the user creating the watch
            domain: Domain name to watch
            check_frequency: Frequency in minutes to check the domain
            is_active: Whether the watch is active
            
        Returns:
            The created DomainWatch instance
            
        Raises:
            HTTPException: If there's an error creating the watch
        """
        try:
            # Create the schema object for the new watch
            watch_create = DomainWatchCreate(
                domain=domain.lower(),
                check_frequency=check_frequency,
                is_active=is_active,
                last_checked=None,
                last_status=None
            )
            
            # Create the watch using the CRUD operation
            return crud_domain_watch.create_with_user(
                db=db,
                obj_in=watch_create,
                user_id=user_id
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating domain watch: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create domain watch: {str(e)}"
            )
    
    def get_user_watches(
        self, 
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[DomainWatch]:
        """Get all domain watches for a user.
        
        Args:
            db: Database session
            user_id: ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of DomainWatch instances
        """
        return crud_domain_watch.get_by_user(
            db, 
            user_id=user_id, 
            skip=skip, 
            limit=limit
        )
    
    def update_watch(
        self, 
        db: Session, 
        watch_id: int, 
        user_id: int, 
        update_data: Dict[str, Any]
    ) -> Optional[DomainWatch]:
        """Update a domain watch.
        
        Args:
            db: Database session
            watch_id: ID of the watch to update
            user_id: ID of the user making the request
            update_data: Dictionary of fields to update
            
        Returns:
            Updated DomainWatch instance, or None if not found
        """
        db_watch = self.get_watch(db, watch_id, user_id)
        if not db_watch:
            return None
            
        return crud_domain_watch.update(
            db, 
            db_obj=db_watch, 
            obj_in=update_data
        )
    
    def delete_watch(self, db: Session, watch_id: int, user_id: int) -> bool:
        """Delete a domain watch if it belongs to the user.
        
        Args:
            db: Database session
            watch_id: ID of the watch to delete
            user_id: ID of the user making the request
            
        Returns:
            True if the watch was deleted, False if not found or not authorized
        """
        db_watch = self.get_watch(db, watch_id, user_id)
        if not db_watch:
            return False
            
        crud_domain_watch.remove(db, id=watch_id)
        return True

    def get_watch(self, db: Session, watch_id: int, user_id: int) -> Optional[DomainWatch]:
        """Get a domain watch if it belongs to the user.
        
        Args:
            db: Database session
            watch_id: ID of the watch to get
            user_id: ID of the user making the request
            
        Returns:
            DomainWatch instance if found and authorized, None otherwise
        """
        watch = crud_domain_watch.get(db, watch_id)
        if not watch or watch.user_id != user_id:
            return None
        return watch
