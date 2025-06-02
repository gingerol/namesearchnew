"""Test script for domain monitoring functionality."""
import asyncio
import logging
import sys
from datetime import datetime

# Add project root to path
sys.path.append('..')

from sqlalchemy.orm import Session

from namesearch.db.session import get_db
from namesearch.models.domain_watch import DomainWatch
from namesearch.models.user import User
from namesearch.services.domain_monitor import DomainMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_domain_monitor():
    """Test the domain monitoring functionality."""
    db = next(get_db())
    
    # Create a test user if not exists
    test_email = "test@example.com"
    user = db.query(User).filter(User.email == test_email).first()
    
    if not user:
        logger.info("Creating test user...")
        user = User(
            email=test_email,
            hashed_password="hashed_test_password",
            full_name="Test User",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create a test domain watch
    test_domain = "example-test-domain123.com"
    watch = db.query(DomainWatch).filter(
        DomainWatch.domain == test_domain,
        DomainWatch.user_id == user.id
    ).first()
    
    if not watch:
        logger.info(f"Creating test watch for domain: {test_domain}")
        watch = DomainWatch(
            domain=test_domain,
            user_id=user.id,
            is_active=True,
            check_frequency=1,  # 1 minute for testing
            last_checked=datetime.utcnow(),
            last_status="unknown"
        )
        db.add(watch)
        db.commit()
        db.refresh(watch)
    
    # Initialize and start the monitor
    logger.info("Starting domain monitor...")
    monitor = DomainMonitor(db)
    monitor_task = asyncio.create_task(monitor.start())
    
    try:
        # Let it run for a few minutes
        logger.info("Monitoring domains for 5 minutes (press Ctrl+C to stop)...")
        await asyncio.sleep(300)  # 5 minutes
    except asyncio.CancelledError:
        logger.info("Test completed")
    finally:
        # Clean up
        logger.info("Stopping domain monitor...")
        await monitor.stop()
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        
        # Clean up test data
        db.delete(watch)
        db.delete(user)
        db.commit()
        logger.info("Test data cleaned up")

if __name__ == "__main__":
    asyncio.run(test_domain_monitor())
