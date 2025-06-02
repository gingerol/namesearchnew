"""Test script for domain monitoring service."""
import asyncio
import logging
import os
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules after setting up logging
from namesearch.db.base import Base
from namesearch.models import *  # Import all models to ensure tables are created
from namesearch.services.domain_monitor_service import DomainMonitorService
from namesearch.services.whois_service import WHOISService

# Test database URL (in-memory SQLite for testing)
TEST_DB_PATH = "./test.db"
if os.path.exists(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

# Create test database and tables
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database with all tables."""
    # Import all models to ensure tables are created
    from namesearch.models.user import User
    from namesearch.models.domain import Domain, Search, SearchResult
    from namesearch.models.project import Project, ProjectMember
    from namesearch.models.domain_watch import DomainWatch
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

# Removed create_test_user function as it's now inlined in test_domain_monitoring

async def test_domain_monitoring():
    """Test the domain monitoring service."""
    # Initialize the database
    init_db()
    
    # Create a new database session
    db = TestingSessionLocal()
    
    try:
        # Create a test user
        user = User(
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created test user with ID: {user.id}")
        
        # Create the domain monitor service
        monitor_service = DomainMonitorService()
        
        # Create a domain watch
        logger.info("Testing domain watch creation...")
        try:
            domain_watch = monitor_service.create_watch(
                db=db,
                user_id=user.id,
                domain="example-test-domain.com",
                check_frequency=60,
            )
            db.commit()
            logger.info(f"Created domain watch: {domain_watch}")
        except Exception as e:
            logger.error(f"Error creating domain watch: {str(e)}")
            raise
        
        # Test getting user's watches
        logger.info("Testing getting user's watches...")
        try:
            watches = monitor_service.get_user_watches(db=db, user_id=user.id)
            logger.info(f"Found {len(watches)} watches for user")
            domain_watch = watches[0] if watches else None
        except Exception as e:
            logger.error(f"Error getting user's watches: {str(e)}")
            raise
        
        # Test getting user's watches
        logger.info("Testing getting user's watches...")
        try:
            watches = monitor_service.get_user_watches(db=db, user_id=user.id)
            logger.info(f"Found {len(watches)} watches for user")
        except Exception as e:
            logger.error(f"Error getting user's watches: {str(e)}")
            raise
        
        # Test processing a watch
        if domain_watch:
            logger.info("Testing watch processing...")
            try:
                await monitor_service._process_watch(db, domain_watch)
                db.refresh(domain_watch)
                logger.info(f"Updated watch after processing: {domain_watch}")
            except Exception as e:
                logger.error(f"Error processing watch: {str(e)}")
                raise
        
        # Test updating a watch
        logger.info("Testing watch update...")
        try:
            updated_watch = monitor_service.update_watch(
                db=db,
                watch_id=domain_watch.id,
                user_id=user.id,
                update_data={"check_frequency": 120, "is_active": False}
            )
            db.commit()
            logger.info(f"Updated watch: {updated_watch}")
        except Exception as e:
            logger.error(f"Error updating watch: {str(e)}")
            raise
        
        # Test deleting a watch
        logger.info("Testing watch deletion...")
        try:
            success = monitor_service.delete_watch(
                db=db,
                watch_id=domain_watch.id,
                user_id=user.id,
            )
            logger.info(f"Watch deletion {'succeeded' if success else 'failed'}")
        except Exception as e:
            logger.error(f"Error deleting watch: {str(e)}")
            raise
        
        # Start and stop the monitor service
        logger.info("Testing monitor service start/stop...")
        try:
            await monitor_service.start(db=db, check_interval=5)
            await asyncio.sleep(2)  # Let it run for a bit
            await monitor_service.stop()
            logger.info("Monitor service stopped")
        except Exception as e:
            logger.error(f"Error in monitor service: {str(e)}")
            await monitor_service.stop()  # Ensure service is stopped
            raise
        
        logger.info("All tests completed successfully!")
        
        # Clean up test database
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
            logger.info("Test database cleaned up")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        raise
    finally:
        # Clean up
        db.close()

if __name__ == "__main__":
    asyncio.run(test_domain_monitoring())
