"""Script to create the domain_watches table with proper foreign key relationship."""
import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_domain_watches_table(db_uri):
    """Create the domain_watches table with proper foreign key relationship."""
    try:
        # Create engine and reflect existing database
        engine = create_engine(db_uri)
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        # Check if domain_watches table already exists
        if 'domain_watches' in metadata.tables:
            logger.info("domain_watches table already exists")
            return True
            
        # Get the users table to reference
        users_table = Table('users', metadata, autoload_with=engine)
        
        # Define the domain_watches table
        domain_watches = Table(
            'domain_watches',
            metadata,
            Column('id', Integer, primary_key=True, index=True),
            Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
            Column('domain', String(255), nullable=False, index=True),
            Column('is_active', Boolean, default=True, nullable=False),
            Column('check_frequency', Integer, default=60, nullable=False),  # in minutes
            Column('last_checked', DateTime, nullable=True),
            Column('last_status', String(20), nullable=True),  # 'available', 'taken', 'unknown'
            Column('whois_data', JSON, nullable=True),
            Column('created_at', DateTime, default='now()', nullable=False),
            Column('updated_at', DateTime, default='now()', onupdate='now()', nullable=False),
        )
        
        # Create the table
        logger.info("Creating domain_watches table...")
        domain_watches.create(engine)
        logger.info("Successfully created domain_watches table")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Error creating domain_watches table: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    # Import settings here to avoid circular imports
    from namesearch.core.config import settings
    
    # Get database URI
    db_uri = settings.DATABASE_URI or settings.assemble_db_connection(None, settings.dict())
    
    # Run the migration
    success = create_domain_watches_table(db_uri)
    exit(0 if success else 1)
