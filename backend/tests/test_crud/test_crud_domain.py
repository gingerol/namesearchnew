"""Tests for the domain CRUD operations."""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from namesearch import crud, models, schemas
from namesearch.models.domain import DomainStatus, TLDType
from namesearch.schemas.domain import DomainSearchQuery
from tests.test_utils import random_lower_string


def test_create_domain(db: Session) -> None:
    """Test creating a new domain."""
    domain_data = {
        "name": f"testdomain{int(datetime.now().timestamp())}",
        "tld": "com",
        "tld_type": TLDType.GTLD.value,
        "status": DomainStatus.AVAILABLE.value,
        "whois_data": {"registrar": "Test Registrar"},
        "is_premium": False
    }
    
    domain = crud.domain.create(db, obj_in=schemas.DomainCreate(**domain_data))
    
    assert domain.name == domain_data["name"]
    assert domain.tld == domain_data["tld"]
    assert domain.tld_type == domain_data["tld_type"]
    assert domain.status == domain_data["status"]
    assert domain.is_premium == domain_data["is_premium"]


def test_get_domain(db: Session) -> None:
    """Test getting a domain by ID."""
    # Create a test domain with a unique name
    domain_name = f"testdomain{datetime.now().timestamp()}"
    domain_data = {
        "name": domain_name,
        "tld": "com",
        "tld_type": TLDType.GTLD.value,
        "status": DomainStatus.AVAILABLE.value,
        "whois_data": {}
    }
    domain = crud.domain.create(db, obj_in=schemas.DomainCreate(**domain_data))
    
    # Test getting the domain by ID
    domain_by_id = crud.domain.get(db, id=domain.id)
    assert domain_by_id
    assert domain_by_id.name == domain.name
    assert domain_by_id.id == domain.id
    assert domain_by_id.tld_type == TLDType.GTLD.value
    
    # Test getting a non-existent domain
    non_existent_domain = crud.domain.get(db, id=999999)
    assert non_existent_domain is None


def test_get_domain_by_name(db: Session) -> None:
    """Test getting a domain by name."""
    # Create a test domain with a unique name
    domain_name = f"testdomain{datetime.now().timestamp()}"
    domain_data = {
        "name": domain_name,
        "tld": "com",
        "tld_type": TLDType.GTLD.value,
        "status": DomainStatus.AVAILABLE.value,
        "whois_data": {}
    }
    domain = crud.domain.create(db, obj_in=schemas.DomainCreate(**domain_data))
    
    # Test getting the domain by name (without TLD)
    domain_by_name = crud.domain.get_by_name(db, name=domain_name)
    assert domain_by_name
    assert domain_by_name.name == domain.name
    assert domain_by_name.tld == domain.tld
    assert domain_by_name.tld_type == TLDType.GTLD.value
    
    # Test getting a non-existent domain
    non_existent_domain = crud.domain.get_by_name(db, name="nonexistent.com")
    assert non_existent_domain is None


def test_get_multi_domains(db: Session) -> None:
    """Test getting multiple domains with pagination."""
    # Create some test domains
    domains = []
    for i in range(10):
        domain_data = {
            "name": f"testdomain{datetime.now().timestamp()}{i}",
            "tld": "com",
            "tld_type": TLDType.GTLD.value,
            "status": DomainStatus.AVAILABLE.value,
            "whois_data": {}
        }
        domain = crud.domain.create(db, obj_in=schemas.DomainCreate(**domain_data))
        domains.append(domain)
    
    # Test getting first page (5 domains)
    domains_page_1 = crud.domain.get_multi(db, skip=0, limit=5)
    assert len(domains_page_1) == 5
    assert all(d.tld_type == TLDType.GTLD.value for d in domains_page_1)
    
    # Test getting second page (5 domains)
    domains_page_2 = crud.domain.get_multi(db, skip=5, limit=5)
    assert len(domains_page_2) == 5
    assert all(d.tld_type == TLDType.GTLD.value for d in domains_page_2)
    
    # Test getting with skip beyond the number of domains
    domains_empty = crud.domain.get_multi(db, skip=20, limit=5)
    assert len(domains_empty) == 0


def test_update_domain(db: Session) -> None:
    """Test updating a domain."""
    # Create a test domain with a unique name
    domain_name = f"testdomain{datetime.now().timestamp()}"
    domain_data = {
        "name": domain_name,
        "tld": "com",
        "tld_type": TLDType.GTLD.value,
        "status": DomainStatus.AVAILABLE.value,
        "whois_data": {}
    }
    domain = crud.domain.create(db, obj_in=schemas.DomainCreate(**domain_data))
    
    # Update the domain
    update_data = {
        "status": DomainStatus.REGISTERED.value,
        "whois_data": {"registrar": "Updated Registrar"},
        "is_premium": True
    }
    
    updated_domain = crud.domain.update(
        db, 
        db_obj=domain, 
        obj_in=schemas.DomainUpdate(**update_data)
    )
    
    assert updated_domain.status == update_data["status"]
    assert updated_domain.whois_data == update_data["whois_data"]
    assert updated_domain.is_premium == update_data["is_premium"]
    assert updated_domain.tld_type == TLDType.GTLD.value


def test_remove_domain(db: Session) -> None:
    """Test removing a domain."""
    # Create a test domain with a unique name
    domain_name = f"testdomain{datetime.now().timestamp()}"
    domain_data = {
        "name": domain_name,
        "tld": "com",
        "tld_type": TLDType.GTLD.value,
        "status": DomainStatus.AVAILABLE.value,
        "whois_data": {}
    }
    domain = crud.domain.create(db, obj_in=schemas.DomainCreate(**domain_data))
    
    # Remove the domain
    removed_domain = crud.domain.remove(db, id=domain.id)
    
    assert removed_domain.id == domain.id
    assert removed_domain.name == domain.name
    assert removed_domain.tld_type == TLDType.GTLD.value
    
    # Verify the domain was removed
    assert crud.domain.get(db, id=domain.id) is None


def test_search_domains(db: Session) -> None:
    """Test searching for domains."""
    # Create some test domains with unique names
    timestamp = int(datetime.now().timestamp())
    domains_data = [
        {"name": f"testdomain{timestamp}1", "tld": "com", "tld_type": TLDType.GTLD.value, "status": DomainStatus.AVAILABLE.value, "is_available": True},
        {"name": f"testdomain{timestamp}2", "tld": "com", "tld_type": TLDType.GTLD.value, "status": DomainStatus.REGISTERED.value, "is_available": False},
        {"name": f"testdomain{timestamp}3", "tld": "net", "tld_type": TLDType.GTLD.value, "status": DomainStatus.AVAILABLE.value, "is_available": True},
        {"name": f"testdomain{timestamp}4", "tld": "org", "tld_type": TLDType.GTLD.value, "status": DomainStatus.AVAILABLE.value, "is_available": True},
    ]
    
    for data in domains_data:
        crud.domain.create(db, obj_in=schemas.DomainCreate(**data))

    # Debug: Print all domains in the DB
    all_domains = crud.domain.get_multi(db)
    print('DEBUG: All domains in DB:')
    for d in all_domains:
        print(f"name={d.name}, tld={d.tld}, is_available={d.is_available}, status={d.status}")
    # Debug: Print TLDs in search query and in DB
    print('DEBUG: TLDs in search query:', [t for t in ["com", "net"]])
    print('DEBUG: TLDs in DB:', [d.tld for d in all_domains])

    # Search for available domains
    search_query = DomainSearchQuery(
        query=f"testdomain{timestamp}",
        tlds=["com", "net"],
        check_availability=True
    )
    available_domains = crud.domain.search(db, query=search_query, skip=0, limit=10)
    
    assert len(available_domains) == 2
    assert all(d.status == DomainStatus.AVAILABLE.value for d in available_domains)
    assert all(d.name.startswith(f"testdomain{timestamp}") for d in available_domains)
    assert all(d.tld_type == TLDType.GTLD.value for d in available_domains)
    assert set(d.tld for d in available_domains) == {"com", "net"}
    
    # Search with pagination
    pagination_query = DomainSearchQuery(query=f"testdomain{timestamp}")
    paginated_domains = crud.domain.search(
        db, 
        query=pagination_query,
        skip=1,
        limit=2
    )
    assert len(paginated_domains) == 2
