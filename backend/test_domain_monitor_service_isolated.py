"""Isolated tests for DomainMonitorService with all external dependencies mocked."""
import asyncio
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, AsyncMock
import pytest

# Mock classes
class MockDomainWatch:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.domain = kwargs.get('domain')
        self.user_id = kwargs.get('user_id')
        self.check_frequency = kwargs.get('check_frequency', 60)
        self.is_active = kwargs.get('is_active', True)
        self.last_checked = kwargs.get('last_checked')
        self.last_status = kwargs.get('last_status')
        self.whois_data = kwargs.get('whois_data', {})
        self.__dict__.update(kwargs)

class MockDB:
    def __init__(self):
        self.committed = False
        self.refreshed = False
    
    def commit(self):
        self.committed = True
    
    def refresh(self, obj):
        self.refreshed = True

# Mock CRUD operations
class MockCRUDDomainWatch:
    @staticmethod
    def create_with_user(db, obj_in, user_id):
        return MockDomainWatch(
            id=1,
            domain=obj_in.domain,
            user_id=user_id,
            check_frequency=obj_in.check_frequency,
            is_active=obj_in.is_active
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
        return True
    
    @staticmethod
    def get_active_watches(db):
        return [MockDomainWatch(id=1, domain="example.com", user_id=1)]
    
    @staticmethod
    def update_last_checked(db, db_obj, last_checked, last_status, whois_data=None):
        db_obj.last_checked = last_checked
        db_obj.last_status = last_status
        if whois_data:
            db_obj.whois_data = whois_data
        return db_obj

# Mock WHOIS service
class MockWhoisService:
    @staticmethod
    def lookup_domain(domain):
        return {
            "status": "active",
            "expiration_date": "2025-12-31T23:59:59Z",
            "creation_date": "2020-01-01T00:00:00Z",
            "updated_date": "2024-01-01T00:00:00Z"
        }

# Apply mocks
import sys
sys.modules['namesearch.crud.domain_watch'] = MockCRUDDomainWatch()
sys.modules['namesearch.services.whois_service.whois_service'] = MockWhoisService()

# Import the service after setting up mocks
from namesearch.services.domain_monitor_service import DomainMonitorService

# Test fixtures
@pytest.fixture
def domain_monitor_service():
    return DomainMonitorService()

@pytest.fixture
def mock_db():
    return MockDB()

@pytest.fixture
def test_user():
    return MagicMock(id=1, email="test@example.com")

@pytest.fixture
def test_domain_watch():
    return MockDomainWatch(
        id=1,
        domain="example.com",
        user_id=1,
        check_frequency=60,
        is_active=True
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
    with patch('namesearch.services.whois_service.whois_service.lookup_domain') as mock_whois:
        mock_whois.return_value = {"status": "active"}
        
        await domain_monitor_service._process_watch(mock_db, test_domain_watch)
        
        mock_whois.assert_called_once_with(test_domain_watch.domain)
        assert test_domain_watch.last_status == "active"
        assert mock_db.committed is True
        assert mock_db.refreshed is True

@pytest.mark.asyncio
async def test_monitor_loop(mock_db, domain_monitor_service):
    """Test the monitoring loop."""
    domain_monitor_service._monitoring = True
    
    with patch('namesearch.services.domain_monitor_service.crud_domain_watch.get_active_watches', 
               return_value=[MockDomainWatch(id=1, domain="example.com", user_id=1)]) as mock_get_active, \
         patch('namesearch.services.domain_monitor_service.DomainMonitorService._process_watch',
               new_callable=AsyncMock) as mock_process:
        
        monitor_task = asyncio.create_task(
            domain_monitor_service._monitor_loop(mock_db, check_interval=0.1)
        )
        
        await asyncio.sleep(0.2)
        domain_monitor_service._monitoring = False
        monitor_task.cancel()
        
        mock_get_active.assert_called()
        mock_process.assert_called_once()

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
