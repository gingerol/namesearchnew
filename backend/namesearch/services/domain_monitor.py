"""Domain monitoring service for tracking domain availability changes."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple

from sqlalchemy.orm import Session

from namesearch import crud, schemas
from namesearch.models import domain_watch
from namesearch.core.config import settings
from namesearch.db.session import get_db
from namesearch.utils.domain_checker import is_domain_available
from namesearch.utils.cache import cache_domain, get_cached_domain

logger = logging.getLogger(__name__)

class DomainMonitor:
    """Service for monitoring domain availability changes."""
    
    def __init__(self, db: Session):
        self.db = db
        self.active_monitors: Dict[int, asyncio.Task] = {}
        self.running = False
    
    async def start(self):
        """Start the domain monitoring service."""
        if self.running:
            logger.warning("Domain monitor is already running")
            return
            
        self.running = True
        logger.info("Starting domain monitor")
        
        # Start monitoring all active watches
        watches = crud.domain_watch.get_active_watches(self.db)
        for watch in watches:
            self._start_watch(watch)
    
    async def stop(self):
        """Stop the domain monitoring service."""
        self.running = False
        for task in self.active_monitors.values():
            task.cancel()
        self.active_monitors.clear()
        logger.info("Domain monitor stopped")
    
    def add_watch(self, watch: domain_watch.DomainWatch):
        """Add a new domain to monitor."""
        if watch.id in self.active_monitors:
            logger.warning(f"Watch {watch.id} is already being monitored")
            return
            
        logger.info(f"Adding domain to monitor: {watch.domain}")
        self._start_watch(watch)
    
    def remove_watch(self, watch_id: int):
        """Stop monitoring a domain."""
        if watch_id in self.active_monitors:
            logger.info(f"Removing domain watch: {watch_id}")
            self.active_monitors[watch_id].cancel()
            del self.active_monitors[watch_id]
    
    def _start_watch(self, watch: domain_watch.DomainWatch):
        """Start monitoring a domain."""
        if watch.id in self.active_monitors:
            return
            
        task = asyncio.create_task(self._monitor_domain(watch))
        self.active_monitors[watch.id] = task
    
    async def _monitor_domain(self, watch: domain_watch.DomainWatch):
        """Monitor a single domain for changes."""
        logger.info(f"Starting monitoring for domain: {watch.domain}")
        
        check_interval = timedelta(minutes=settings.DOMAIN_CHECK_INTERVAL_MINUTES)
        last_status = watch.last_status
        
        while self.running:
            try:
                # Check domain availability
                is_available, whois_data = is_domain_available(watch.domain)
                current_status = "available" if is_available else "taken"
                
                # Check for status change
                if current_status != last_status:
                    logger.info(f"Domain status changed: {watch.domain} is now {current_status}")
                    
                    # Update watch in database
                    db_watch = crud.domain_watch.get(self.db, watch.id)
                    if db_watch:
                        update_data = {
                            "last_checked": datetime.utcnow(),
                            "last_status": current_status,
                            "whois_data": whois_data.to_dict() if whois_data and hasattr(whois_data, 'to_dict') else {}
                        }
                        crud.domain_watch.update(self.db, db_obj=db_watch, obj_in=update_data)
                        
                        # Create notification
                        notification = models.Notification(
                            user_id=watch.user_id,
                            title=f"Domain {watch.domain} is now {current_status}",
                            message=f"The domain {watch.domain} is now {current_status}.",
                            notification_type="domain_status_change",
                            data={
                                "domain": watch.domain,
                                "status": current_status,
                                "watch_id": watch.id
                            }
                        )
                        self.db.add(notification)
                        self.db.commit()
                        
                        # TODO: Send email notification if configured
                        
                        last_status = current_status
                
                # Wait for the next check interval
                await asyncio.sleep(check_interval.total_seconds())
                
            except asyncio.CancelledError:
                logger.info(f"Stopping monitoring for domain: {watch.domain}")
                raise
            except Exception as e:
                logger.error(f"Error monitoring domain {watch.domain}: {str(e)}", exc_info=True)
                await asyncio.sleep(60)  # Wait a minute before retrying on error

# Global instance
domain_monitor = None

def get_domain_monitor() -> DomainMonitor:
    """Get the global domain monitor instance."""
    global domain_monitor
    if domain_monitor is None:
        db = next(get_db())
        domain_monitor = DomainMonitor(db)
    return domain_monitor
