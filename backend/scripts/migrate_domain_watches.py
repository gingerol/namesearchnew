"""Database migration script for domain watches."""
import sys
import logging
from datetime import datetime

# Add project root to path
sys.path.append('..')

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import sessionmaker

from namesearch.core.config import settings
from namesearch.db.base import Base
from namesearch.models.domain_watch import DomainWatch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_tables(engine):
    """Create all tables."""
    logger.info("Creating tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created successfully")

def drop_tables(engine):
    """Drop all tables."""
    logger.warning("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("All tables dropped")

def migrate_domain_watches():
    """Migrate the database to add domain_watches table."""
    # Create engine and session
    db_uri = settings.DATABASE_URI or settings.assemble_db_connection(None, settings.dict())
    engine = create_engine(db_uri)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Reflect existing tables
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        # Create domain_watches table if it doesn't exist
        if 'domain_watches' not in metadata.tables:
            logger.info("Creating domain_watches table...")
            DomainWatch.__table__.create(bind=engine)
            logger.info("domain_watches table created successfully")
            return True
        else:
            logger.info("domain_watches table already exists")
            return True
            
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}", exc_info=True)
        return False
            
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}", exc_info=True)
        return False
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration tool')
    parser.add_argument('--drop', action='store_true', help='Drop all tables before creating')
    parser.add_argument('--migrate', action='store_true', help='Run database migrations')
    
    args = parser.parse_args()
    
    try:
        # Get database URI from settings
        db_uri = settings.DATABASE_URI or settings.assemble_db_connection(None, settings.dict())
        engine = create_engine(db_uri)
        
        if args.drop:
            drop_tables(engine)
        
        if args.migrate:
            success = migrate_domain_watches()
            if success:
                logger.info("Migration completed successfully")
            else:
                logger.error("Migration failed")
                sys.exit(1)
        else:
            # Default: just create all tables
            create_tables(engine)
            
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        sys.exit(1)
