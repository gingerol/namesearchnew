"""Tests for domain monitoring functionality."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from namesearch.models.domain_watch import DomainWatch
from namesearch.models.user import User
from namesearch.schemas.domain_watch import DomainWatchCreate, DomainWatchUpdate
from namesearch.services.domain_monitor_service import DomainMonitorService
from namesearch.services.whois_service import WHOISService

# Test data
TEST_DOMAIN = "example-test-domain.com"
TEST_USER_ID = 1

# Mock WHOIS data
MOCK_WHOIS_DATA = {
    "domain_name": "EXAMPLE-TEST-DOMAIN.COM",
    "registrar": "Example Registrar, Inc.",
    "whois_server": "whois.example-registrar.com",
    "updated_date": [datetime.utcnow() - timedelta(days=30)],
    "creation_date": [datetime.utcnow() - timedelta(days=365)],
    "expiration_date": [datetime.utcnow() + timedelta(days=335)],
    "name_servers": ["ns1.example.com", "ns2.example.com"],
    "status": "clientDeleteProhibited",
    "emails": ["contact@example-registrar.com"],
    "dnssec": "unsigned",
    "org": "Example Organization",
    "address": "123 Example St",
    "city": "Example City",
    "state": "CA",
    "zipcode": "12345",
    "country": "US",
}

@pytest.fixture
def mock_whois_lookup():
    """Mock the WHOIS lookup to return test data."""
    with patch('namesearch.services.whois_service.whois.whois') as mock_whois:
        mock_whois.return_value = MOCK_WHOIS_DATA
        yield mock_whois

@pytest.fixture
def domain_monitor_service(db: Session) -> DomainMonitorService:
    """Create a DomainMonitorService instance for testing."""
    return DomainMonitorService(db)

def test_create_domain_watch(db: Session, domain_monitor_service: DomainMonitorService):
    """Test creating a new domain watch."""
    # Create a test user
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
    )
    db.add(user)
    db.commit()
    
    # Create a domain watch
    domain_watch = domain_monitor_service.create_watch(
        user_id=user.id,
        domain=TEST_DOMAIN,
        check_frequency=60,
    )
    
    # Verify the domain watch was created
    assert domain_watch.id is not None
    assert domain_watch.domain == TEST_DOMAIN.lower()
    assert domain_watch.user_id == user.id
    assert domain_watch.check_frequency == 60
    assert domain_watch.is_active is True
    assert domain_watch.last_checked is None
    assert domain_watch.last_status is None

@patch('namesearch.services.domain_monitor_service.WHOISService.lookup_domain')
def test_process_watch(mock_lookup, db: Session, domain_monitor_service: DomainMonitorService):
    """Test processing a domain watch."""
    # Create a test user
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
    )
    db.add(user)
    db.commit()
    
    # Create a domain watch
    domain_watch = domain_monitor_service.create_watch(
        user_id=user.id,
        domain=TEST_DOMAIN,
        check_frequency=60,
    )
    
    # Mock the WHOIS lookup
    mock_lookup.return_value = {
        **MOCK_WHOIS_DATA,
        "status": "active",
    }
    
    # Process the watch
    import asyncio
    asyncio.run(domain_monitor_service._process_watch(domain_watch))
    
    # Verify the watch was updated
    db.refresh(domain_watch)
    assert domain_watch.last_checked is not None
    assert domain_watch.last_status == "active"
    assert domain_watch.whois_data is not None

def test_get_user_watches(db: Session, domain_monitor_service: DomainMonitorService):
    """Test retrieving domain watches for a user."""
    # Create a test user
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
    )
    db.add(user)
    db.commit()
    
    # Create some test watches
    for i in range(5):
        domain_monitor_service.create_watch(
            user_id=user.id,
            domain=f"test{i}.com",
            check_frequency=60,
        )
    
    # Get watches for the user
    watches = domain_monitor_service.get_user_watches(user_id=user.id)
    
    # Verify the correct number of watches were returned
    assert len(watches) == 5
    assert all(watch.user_id == user.id for watch in watches)

def test_update_watch(db: Session, domain_monitor_service: DomainMonitorService):
    """Test updating a domain watch."""
    # Create a test user
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
    )
    db.add(user)
    db.commit()
    
    # Create a domain watch
    domain_watch = domain_monitor_service.create_watch(
        user_id=user.id,
        domain=TEST_DOMAIN,
        check_frequency=60,
    )
    
    # Update the watch
    updated_watch = domain_monitor_service.update_watch(
        watch_id=domain_watch.id,
        user_id=user.id,
        update_data={"check_frequency": 120, "is_active": False}
    )
    
    # Verify the watch was updated
    assert updated_watch.check_frequency == 120
    assert updated_watch.is_active is False

def test_delete_watch(db: Session, domain_monitor_service: DomainMonitorService):
    """Test deleting a domain watch."""
    # Create a test user
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
    )
    db.add(user)
    db.commit()
    
    # Create a domain watch
    domain_watch = domain_monitor_service.create_watch(
        user_id=user.id,
        domain=TEST_DOMAIN,
        check_frequency=60,
    )
    
    # Delete the watch
    success = domain_monitor_service.delete_watch(
        watch_id=domain_watch.id,
        user_id=user.id,
    )
    
    # Verify the watch was deleted
    assert success is True
    
    # Try to get the watch (should not exist)
    from namesearch.crud import crud_domain_watch
    deleted_watch = crud_domain_watch.domain_watch.get(db, id=domain_watch.id)
    assert deleted_watch is None
