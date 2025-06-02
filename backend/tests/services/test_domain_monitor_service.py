"""Tests for the DomainMonitorService."""
import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

# Enable async test support
pytestmark = pytest.mark.asyncio

from namesearch.models.domain_watch import DomainWatch
from namesearch.models.user import User
from namesearch.schemas.domain_watch import DomainWatchCreate, DomainWatchUpdate
from namesearch.services.domain_monitor_service import DomainMonitorService

@pytest.fixture
def domain_monitor_service():
    """Fixture for the domain monitor service."""
    return DomainMonitorService()

def test_create_watch(db: Session, test_user: User, domain_monitor_service: DomainMonitorService):
    """Test creating a new domain watch."""
    watch_data = DomainWatchCreate(
        domain="example.com",
        check_frequency=60,
        is_active=True
    )
    
    watch = domain_monitor_service.create_watch(
        db=db,
        user_id=test_user.id,
        domain=watch_data.domain,
        check_frequency=watch_data.check_frequency,
        is_active=watch_data.is_active
    )
    
    assert watch is not None
    assert watch.domain == "example.com"
    assert watch.user_id == test_user.id
    assert watch.check_frequency == 60
    assert watch.is_active is True

def test_get_user_watches(db: Session, test_user: User, test_domain_watch: DomainWatch, domain_monitor_service: DomainMonitorService):
    """Test getting watches for a user."""
    watches = domain_monitor_service.get_user_watches(
        db=db,
        user_id=test_user.id
    )
    
    assert len(watches) > 0
    assert any(w.domain == test_domain_watch.domain for w in watches)

def test_get_watch(db: Session, test_user: User, test_domain_watch: DomainWatch, domain_monitor_service: DomainMonitorService):
    """Test getting a specific watch."""
    watch = domain_monitor_service.get_watch(
        db=db,
        watch_id=test_domain_watch.id,
        user_id=test_user.id
    )
    
    assert watch is not None
    assert watch.id == test_domain_watch.id
    assert watch.domain == test_domain_watch.domain

def test_update_watch(db: Session, test_user: User, test_domain_watch: DomainWatch, domain_monitor_service: DomainMonitorService):
    """Test updating a watch."""
    update_data = {"check_frequency": 120, "is_active": False}
    
    updated_watch = domain_monitor_service.update_watch(
        db=db,
        watch_id=test_domain_watch.id,
        user_id=test_user.id,
        update_data=update_data
    )
    
    assert updated_watch is not None
    assert updated_watch.check_frequency == 120
    assert updated_watch.is_active is False

def test_delete_watch(db: Session, test_user: User, test_domain_watch: DomainWatch, domain_monitor_service: DomainMonitorService):
    """Test deleting a watch."""
    result = domain_monitor_service.delete_watch(
        db=db,
        watch_id=test_domain_watch.id,
        user_id=test_user.id
    )
    
    assert result is True
    
    # Verify the watch was deleted
    watch = domain_monitor_service.get_watch(
        db=db,
        watch_id=test_domain_watch.id,
        user_id=test_user.id
    )
    assert watch is None

async def test_process_watch(db: Session, test_domain_watch: DomainWatch, domain_monitor_service: DomainMonitorService):
    """Test processing a watch."""
    with patch('namesearch.services.whois_service.whois_service.lookup_domain') as mock_whois:
        mock_whois.return_value = {
            "status": "active",
            "expiration_date": "2025-12-31T23:59:59Z",
            "creation_date": "2020-01-01T00:00:00Z",
            "updated_date": "2024-01-01T00:00:00Z",
            "registrar": "Example Registrar"
        }
        
        await domain_monitor_service._process_watch(db, test_domain_watch)
        
        # Verify the watch was updated
        db.refresh(test_domain_watch)
        assert test_domain_watch.last_status == "active"
        assert test_domain_watch.last_checked is not None

async def test_monitor_loop(db: Session, test_domain_watch: DomainWatch, domain_monitor_service: DomainMonitorService):
    """Test the monitoring loop."""
    # Set up mocks
    with patch('namesearch.services.whois_service.whois_service.lookup_domain') as mock_whois:
        mock_whois.return_value = {
            "status": "active",
            "expiration_date": "2025-12-31T23:59:59Z"
        }
        
        # Start the monitor with a short interval
        domain_monitor_service._monitoring = True
        monitor_task = asyncio.create_task(
            domain_monitor_service._monitor_loop(db, check_interval=0.1)
        )
        
        # Let it run for a short time
        await asyncio.sleep(0.2)
        
        # Stop the monitor
        domain_monitor_service._monitoring = False
        monitor_task.cancel()
        
        # Verify the watch was processed
        db.refresh(test_domain_watch)
        assert test_domain_watch.last_status == "active"
        assert test_domain_watch.last_checked is not None
