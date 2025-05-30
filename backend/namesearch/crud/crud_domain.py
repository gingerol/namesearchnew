"""CRUD operations for domains."""
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from ..models.domain import Domain, Search, SearchResult
from .base import CRUDBase
from ..schemas.domain import DomainCreate, DomainUpdate, DomainSearchQuery


class CRUDDomain(CRUDBase[Domain, DomainCreate, DomainUpdate]):
    """CRUD operations for domains with additional domain-specific methods."""
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Domain]:
        """Get a domain by its full name."""
        return db.query(Domain).filter(Domain.name == name).first()
    
    def get_by_tld(self, db: Session, *, tld: str, skip: int = 0, limit: int = 100) -> List[Domain]:
        """Get domains by TLD."""
        return db.query(Domain).filter(Domain.tld == tld).offset(skip).limit(limit).all()
    
    def search(
        self, 
        db: Session, 
        *, 
        query: DomainSearchQuery,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Domain]:
        """Search domains with filters."""
        q = db.query(Domain)
        
        # Apply filters based on query parameters
        if query.query:
            q = q.filter(Domain.name.contains(query.query))
        if query.tlds:
            q = q.filter(Domain.tld.in_(query.tlds))
        if query.check_availability is not None:
            q = q.filter(Domain.is_available == query.check_availability)
        # Apply pagination
        return q.offset(skip).limit(limit).all()
    
    def create_search(self, db: Session, *, query: str, user_id: Optional[int] = None) -> Search:
        """Create a new search record."""
        search = Search(query=query, user_id=user_id, search_type="domain")
        db.add(search)
        db.commit()
        db.refresh(search)
        return search
    
    def add_search_result(
        self, 
        db: Session, 
        *, 
        search_id: int, 
        domain_id: int, 
        user_id: int,
        is_available: bool,
        is_premium: bool = False
    ) -> SearchResult:
        """Add a search result to a search."""
        search_result = SearchResult(
            search_id=search_id,
            domain_id=domain_id,
            user_id=user_id,
            is_available=is_available,
            is_premium=is_premium
        )
        db.add(search_result)
        db.commit()
        db.refresh(search_result)
        return search_result
    
    def get_search_history(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Search]:
        """Get search history for a user."""
        return (
            db.query(Search)
            .filter(Search.user_id == user_id)
            .order_by(Search.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


# Create a singleton instance
domain = CRUDDomain(Domain)
