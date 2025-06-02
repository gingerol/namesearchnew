"""Unit tests for DomainMonitorService."""
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from sqlalchemy.orm import Session

from namesearch.models.domain_watch import DomainWatch
from namesearch.models.user import User
from namesearch.schemas.domain_watch import DomainWatchCreate, DomainWatchUpdate
from namesearch.services.domain_monitor_service import DomainMonitorService

# Enable async test support
pytestmark = pytest.mark.asyncio

@pytest.fixture
def domain_monitor_service():
    """Fixture for the domain monitor service."""
    return DomainMonitorService()

@pytest.fixture
def mock_db():
    """Fixture for a mock database session."""
    db = MagicMock(spec=Session)
    return db

@pytest.fixture
def test_user():
    """Fixture for a test user."""
    user = User(
        id=1,
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
    )
    return user

@pytest.fixture
def test_domain_watch(test_user):
    """Fixture for a test domain watch."""
    return DomainWatch(
        id=1,
        domain="example.com",
        user_id=test_user.id,
        check_frequency=60,
        is_active=True,
        last_checked=None,
        last_status=None,
    )

async def test_create_watch(mock_db, test_user, domain_monitor_service):
    """Test creating a new domain watch."""
    # Mock the CRUD method
    mock_watch = DomainWatch(
        id=1,
        domain="example.com",
        user_id=test_user.id,
        check_frequency=60,
        is_active=True,
    )
    
    with patch('namesearch.services.domain_monitor_service.crud_domain_watch.create_with_user', 
               return_value=mock_watch) as mock_create:
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
        mock_create.assert_called_once()

async def test_get_user_watches(mock_db, test_user, test_domain_watch, domain_monitor_service):
    """Test getting watches for a user."""
    with patch('namesearch.services.domain_monitor_service.crud_domain_watch.get_by_user', 
               return_value=[test_domain_watch]) as mock_get:
        watches = domain_monitor_service.get_user_watches(
            db=mock_db,
            user_id=test_user.id
        )
        
        assert len(watches) == 1
        assert watches[0].id == test_domain_watch.id
        mock_get.assert_called_once_with(mock_db, user_id=test_user.id)

async def test_get_watch(mock_db, test_user, test_domain_watch, domain_monitor_service):
    """Test getting a specific watch."""
    with patch('namesearch.services.domain_monitor_service.crud_domain_watch.get', 
               return_value=test_domain_watch) as mock_get:
        watch = domain_monitor_service.get_watch(
            db=mock_db,
            watch_id=test_domain_watch.id,
            user_id=test_user.id
        )
        
        assert watch is not None
        assert watch.id == test_domain_watch.id
        mock_get.assert_called_once_with(mock_db, id=test_domain_watch.id)

async def test_update_watch(mock_db, test_user, test_domain_watch, domain_monitor_service):
    """Test updating a watch."""
    update_data = {"check_frequency": 120, "is_active": False}
    updated_watch = DomainWatch(
        **{**test_domain_watch.__dict__, **update_data}
    )
    
    with patch('namesearch.services.domain_monitor_service.crud_domain_watch.get', 
               return_value=test_domain_watch) as mock_get, \
         patch('namesearch.services.domain_monitor_service.crud_domain_watch.update', 
               return_value=updated_watch) as mock_update:
        
        result = domain_monitor_service.update_watch(
            db=mock_db,
            watch_id=test_domain_watch.id,
            user_id=test_user.id,
            update_data=update_data
        )
        
        assert result is not None
        assert result.check_frequency == 120
        assert result.is_active is False
        mock_get.assert_called_once_with(mock_db, id=test_domain_watch.id)
        mock_update.assert_called_once()

async def test_delete_watch(mock_db, test_user, test_domain_watch, domain_monitor_service):
    """Test deleting a watch."""
    with patch('namesearch.services.domain_monitor_service.crud_domain_watch.get', 
               return_value=test_domain_watch) as mock_get, \
         patch('namesearch.services.domain_monitor_service.crud_domain_watch.remove', 
               return_value=None) as mock_remove:
        
        result = domain_monitor_service.delete_watch(
            db=mock_db,
            watch_id=test_domain_watch.id,
            user_id=test_user.id
        )
        
        assert result is True
        mock_get.assert_called_once_with(mock_db, id=test_domain_watch.id)
        mock_remove.assert_called_once_with(mock_db, id=test_domain_watch.id)

async def test_process_watch(mock_db, test_domain_watch, domain_monitor_service):
    """Test processing a watch."""
    with patch('namesearch.services.whois_service.whois_service.lookup_domain', 
               return_value={
                   "status": "active",
                   "expiration_date": "2025-12-31T23:59:59Z"
               }) as mock_whois, \
         patch('namesearch.services.domain_monitor_service.crud_domain_watch.update_last_checked',
               return_value=test_domain_watch) as mock_update:
        
        await domain_monitor_service._process_watch(mock_db, test_domain_watch)
        
        mock_whois.assert_called_once_with(test_domain_watch.domain)
        mock_update.assert_called_once()

async def test_monitor_loop(mock_db, test_domain_watch, domain_monitor_service):
    """Test the monitoring loop."""
    # Mock the active watches
    with patch('namesearch.services.domain_monitor_service.crud_domain_watch.get_active_watches',
               return_value=[test_domain_watch]) as mock_get_active, \
         patch('namesearch.services.domain_monitor_service.DomainMonitorService._process_watch',
               new_callable=AsyncMock) as mock_process:
        
        # Set up the monitor to run for a short time
        domain_monitor_service._monitoring = True
        monitor_task = asyncio.create_task(
            domain_monitor_service._monitor_loop(mock_db, check_interval=0.1)
        )
        
        # Let it run for a short time
        await asyncio.sleep(0.2)
        
        # Stop the monitor
        domain_monitor_service._monitoring = False
        monitor_task.cancel()
        
        # Verify the watch was processed
        mock_get_active.assert_called()
        mock_process.assert_called_once()
