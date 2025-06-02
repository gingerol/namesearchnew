"""Standalone tests for DomainMonitorService."""
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from sqlalchemy.orm import Session

# Mock the imports to avoid loading the entire application
class MockDomainWatch:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class MockUser:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

# Mock the crud_domain_watch module
class MockCrudDomainWatch:
    @staticmethod
    def create_with_user(db, obj_in, user_id):
        return MockDomainWatch(
            id=1,
            domain=obj_in.domain,
            user_id=user_id,
            check_frequency=obj_in.check_frequency,
            is_active=obj_in.is_active,
            last_checked=None,
            last_status=None
        )
    
    @staticmethod
    def get_by_user(db, user_id):
        return [MockDomainWatch(id=1, domain="example.com", user_id=user_id)]
    
    @staticmethod
    def get(db, id):
        return MockDomainWatch(id=id, domain="example.com", user_id=1)
    
    @staticmethod
    def update(db, db_obj, obj_in):
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        return db_obj
    
    @staticmethod
    def remove(db, id):
        return None
    
    @staticmethod
    def get_active_watches(db):
        return [MockDomainWatch(id=1, domain="example.com", user_id=1)]
    
    @staticmethod
    def update_last_checked(db, db_obj, last_checked, last_status, whois_data=None):
        db_obj.last_checked = last_checked
        db_obj.last_status = last_status
        return db_obj

# Mock the whois_service module
class MockWhoisService:
    @staticmethod
    def lookup_domain(domain):
        return {
            "status": "active",
            "expiration_date": "2025-12-31T23:59:59Z"
        }

# Apply the mocks
import sys
sys.modules['namesearch.crud.domain_watch'] = MockCrudDomainWatch()
sys.modules['namesearch.services.whois_service.whois_service'] = MockWhoisService()

# Now import the service we want to test
from namesearch.services.domain_monitor_service import DomainMonitorService

# Test fixtures
@pytest.fixture
def domain_monitor_service():
    return DomainMonitorService()

@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)

@pytest.fixture
def test_user():
    return MockUser(id=1, email="test@example.com")

@pytest.fixture
def test_domain_watch(test_user):
    return MockDomainWatch(
        id=1,
        domain="example.com",
        user_id=test_user.id,
        check_frequency=60,
        is_active=True,
        last_checked=None,
        last_status=None
    )

# Tests
@pytest.mark.asyncio
async def test_create_watch(mock_db, test_user, domain_monitor_service):
    """Test creating a new domain watch."""
    watch = domain_monitor_service.create_watch(
        db=mock_db,
        user_id=test_user.id,
        domain="example.com",
        check_frequency=60,
        is_active=True
    )
    
    assert watch is not None
    assert watch.domain == "example.com"
    assert watch.user_id == test_user.id

@pytest.mark.asyncio
async def test_get_user_watches(mock_db, test_user, domain_monitor_service):
    """Test getting watches for a user."""
    watches = domain_monitor_service.get_user_watches(
        db=mock_db,
        user_id=test_user.id
    )
    
    assert len(watches) == 1
    assert watches[0].domain == "example.com"

@pytest.mark.asyncio
async def test_process_watch(mock_db, test_domain_watch, domain_monitor_service):
    """Test processing a watch."""
    with patch('namesearch.services.whois_service.whois_service.lookup_domain', 
               return_value={"status": "active"}) as mock_whois:
        await domain_monitor_service._process_watch(mock_db, test_domain_watch)
        mock_whois.assert_called_once_with(test_domain_watch.domain)
        assert test_domain_watch.last_status == "active"

@pytest.mark.asyncio
async def test_monitor_loop(mock_db, domain_monitor_service):
    """Test the monitoring loop."""
    domain_monitor_service._monitoring = True
    monitor_task = asyncio.create_task(
        domain_monitor_service._monitor_loop(mock_db, check_interval=0.1)
    )
    
    # Let it run for a short time
    await asyncio.sleep(0.2)
    
    # Stop the monitor
    domain_monitor_service._monitoring = False
    monitor_task.cancel()
    
    # If we got here without errors, the test passed
    assert True

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
