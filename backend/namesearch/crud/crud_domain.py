"""CRUD operations for domains."""
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from sqlalchemy import func, or_, and_, not_
from datetime import datetime, timedelta

from ..models.domain import Domain, Search, SearchResult, DomainStatus, TLDType # Assuming DomainStatus and TLDType might be useful for filters
from .base import CRUDBase
from ..schemas.domain import (
    DomainCreate, DomainUpdate, DomainSearchQuery, 
    AdvancedDomainSearchRequest, SortOrderEnum, KeywordMatchType,
    TLDType as SchemaTLDType # Alias if TLDType from models is also used
)


class CRUDDomain(CRUDBase[Domain, DomainCreate, DomainUpdate]):
    """CRUD operations for domains with additional domain-specific methods."""

    def create(self, db: Session, *, obj_in: DomainCreate) -> Domain:
        """
        Create a new domain, deriving name_part_length and domain_name_full if not provided.
        """
        db_obj_data = obj_in.model_dump(exclude_unset=True)

        if not db_obj_data.get('name_part_length') and db_obj_data.get('name_part'):
            db_obj_data['name_part_length'] = len(db_obj_data['name_part'])
        
        if not db_obj_data.get('domain_name_full') and db_obj_data.get('name_part') and db_obj_data.get('tld_part'):
            db_obj_data['domain_name_full'] = f"{db_obj_data['name_part']}.{db_obj_data['tld_part']}"
        
        # Ensure required fields that were made optional in Pydantic for derivation now have values
        if 'name_part_length' not in db_obj_data or db_obj_data['name_part_length'] is None:
            # This case should ideally not happen if name_part is always present in DomainCreate
            # Or we raise an error if name_part is missing and length cannot be derived.
            # For now, assuming name_part is present.
            if obj_in.name_part:
                 db_obj_data['name_part_length'] = len(obj_in.name_part)
            else:
                raise ValueError("Cannot create domain: name_part is missing and name_part_length cannot be derived.")

        if 'domain_name_full' not in db_obj_data or db_obj_data['domain_name_full'] is None:
            if obj_in.name_part and obj_in.tld_part:
                db_obj_data['domain_name_full'] = f"{obj_in.name_part}.{obj_in.tld_part}"
            else:
                raise ValueError("Cannot create domain: name_part or tld_part is missing and domain_name_full cannot be derived.")

        db_obj = Domain(**db_obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_name(self, db: Session, *, domain_name_full: str) -> Optional[Domain]:
        """Get a domain by its full name."""
        return db.query(Domain).filter(Domain.domain_name_full == domain_name_full).first()
    
    def get_by_tld(self, db: Session, *, tld_part: str, skip: int = 0, limit: int = 100) -> List[Domain]:
        """Get domains by TLD part."""
        return db.query(Domain).filter(Domain.tld_part == tld_part).offset(skip).limit(limit).all()
    
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
        if query.query: # This query field from DomainSearchQuery typically means a general keyword search
            # Search in name_part or domain_name_full. Using ilike for case-insensitivity.
            search_term = f"%{query.query}%"
            q = q.filter(or_(Domain.name_part.ilike(search_term), Domain.domain_name_full.ilike(search_term)))
        if query.tlds:
            # Ensure TLDs in the query don't have a leading dot, as tld_part in DB doesn't.
            cleaned_tlds = [tld.lstrip('.') for tld in query.tlds]
            q = q.filter(Domain.tld_part.in_(cleaned_tlds))
        if query.check_availability is not None:
            q = q.filter(Domain.is_available == query.check_availability)
        # Apply pagination
        return q.offset(skip).limit(limit).all()

    def advanced_search_filtered(self, db: Session, *, filters: AdvancedDomainSearchRequest) -> tuple[list[Domain], int]:
        """Perform an advanced search for domains with multiple filter criteria."""
        query = db.query(Domain)

        # Keyword search (name_part and domain_name_full)
        if filters.keywords:
            keyword_conditions = []
            for keyword in filters.keywords:
                term = f"%{keyword}%"
                condition = or_(Domain.name_part.ilike(term), Domain.domain_name_full.ilike(term))
                if filters.match_type == KeywordMatchType.EXACT:
                    condition = or_(Domain.name_part == keyword, Domain.domain_name_full == keyword)
                keyword_conditions.append(condition)
            
            if keyword_conditions:
                if filters.match_type == KeywordMatchType.ALL and len(keyword_conditions) > 1:
                    query = query.filter(and_(*keyword_conditions))
                else: # ANY or EXACT (applied per keyword, then ORed)
                    query = query.filter(or_(*keyword_conditions))

        # Exclude keywords
        if filters.exclude_keywords:
            for keyword in filters.exclude_keywords:
                term = f"%{keyword}%"
                query = query.filter(not_(or_(Domain.name_part.ilike(term), Domain.domain_name_full.ilike(term))))

        # TLD list
        if filters.tlds:
            cleaned_tlds = [tld.lstrip('.') for tld in filters.tlds]
            query = query.filter(Domain.tld_part.in_(cleaned_tlds))

        # TLD types
        if filters.tld_types:
            query = query.filter(Domain.tld_type.in_(filters.tld_types))

        # Price range
        if filters.min_price is not None:
            query = query.filter(Domain.price >= filters.min_price)
        if filters.max_price is not None:
            query = query.filter(Domain.price <= filters.max_price)

        # Name part length range
        if filters.min_length is not None:
            query = query.filter(Domain.name_part_length >= filters.min_length)
        if filters.max_length is not None:
            query = query.filter(Domain.name_part_length <= filters.max_length)

        # Availability and Premium status
        if filters.only_available is True:
            query = query.filter(Domain.is_available == True)
        if filters.only_premium is True:
            query = query.filter(Domain.is_premium == True)

        # Starts with / Ends with (for name_part)
        if filters.starts_with:
            query = query.filter(Domain.name_part.startswith(filters.starts_with))
        if filters.ends_with:
            query = query.filter(Domain.name_part.endswith(filters.ends_with))
        
        # Allow numbers/hyphens in name_part
        if filters.allow_numbers is False:
            query = query.filter(not_(Domain.name_part.op('~')('[0-9]'))) # PostgreSQL specific regex
        if filters.allow_hyphens is False:
            query = query.filter(not_(Domain.name_part.contains('-')))

        # Quality and SEO scores
        if filters.min_quality_score is not None:
            query = query.filter(Domain.quality_score >= filters.min_quality_score)
        if filters.max_quality_score is not None:
            query = query.filter(Domain.quality_score <= filters.max_quality_score)
        if filters.min_seo_score is not None:
            query = query.filter(Domain.seo_score >= filters.min_seo_score)
        if filters.max_seo_score is not None:
            query = query.filter(Domain.seo_score <= filters.max_seo_score)

        # Registration date range
        if filters.registered_after:
            query = query.filter(Domain.registered_date >= filters.registered_after)
        if filters.registered_before:
            query = query.filter(Domain.registered_date <= filters.registered_before)

        # Domain age (in years)
        current_time = datetime.utcnow()
        if filters.min_age_years is not None:
            # Domain must be registered at least min_age_years ago
            # So, registered_date must be older than (current_time - min_age_years)
            cutoff_date = current_time - timedelta(days=filters.min_age_years * 365.25)
            query = query.filter(Domain.registered_date <= cutoff_date)
        if filters.max_age_years is not None:
            # Domain must be registered at most max_age_years ago
            # So, registered_date must be younger than (current_time - max_age_years)
            cutoff_date = current_time - timedelta(days=filters.max_age_years * 365.25)
            query = query.filter(Domain.registered_date >= cutoff_date)

        # Search volume and CPC
        if filters.min_search_volume is not None:
            query = query.filter(Domain.search_volume >= filters.min_search_volume)
        if filters.max_search_volume is not None:
            query = query.filter(Domain.search_volume <= filters.max_search_volume)
        if filters.min_cpc is not None:
            query = query.filter(Domain.cpc >= filters.min_cpc)
        if filters.max_cpc is not None:
            query = query.filter(Domain.cpc <= filters.max_cpc)

        # Language codes
        if filters.language_codes:
            query = query.filter(Domain.language.in_(filters.language_codes))

        # Count total items matching filters before sorting and pagination
        total_items = query.count()

        # Apply Sorting
        sort_column_map = {
            "domain_name_full": Domain.domain_name_full,
            "name_part_length": Domain.name_part_length,
            "price": Domain.price,
            "registered_date": Domain.registered_date,
            "quality_score": Domain.quality_score,
            "seo_score": Domain.seo_score,
            "search_volume": Domain.search_volume,
            "cpc": Domain.cpc,
            # Add other sortable fields as needed
        }
        sort_column = sort_column_map.get(filters.sort_by, Domain.domain_name_full) # Default sort

        if filters.sort_order == SortOrderEnum.DESC:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Add secondary sort for consistent pagination if primary sort values are not unique
        if sort_column != Domain.id: # Avoid redundant sort if already sorting by id
             query = query.order_by(Domain.id.asc()) # Ensures stable sort

        # Apply Pagination
        query = query.offset((filters.page - 1) * filters.page_size).limit(filters.page_size)
        
        results = query.all()
        return results, total_items
    
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
