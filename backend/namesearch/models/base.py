"""Base model class for SQLAlchemy models."""
from typing import Any, Dict
from datetime import datetime

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declared_attr as orm_declared_attr
from sqlalchemy import Column, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base

# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult.
# See: http://alembic.zzzcomputing.com/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Base:
    """Base class for all database models."""
    
    # This is a hack to make mypy happy
    __table__: Any
    __tablename__: str
    metadata: Any = metadata
    
    id: Any
    
    # Generate __tablename__ automatically if not specified
    @declared_attr
    @classmethod
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # Common columns
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary.
        
        This is a basic implementation that can be overridden by subclasses.
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


# Create the declarative base with our custom Base class
Base = declarative_base(metadata=metadata, cls=Base)
