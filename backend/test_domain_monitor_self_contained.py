"""Self-contained test for DomainMonitorService with all dependencies included."""
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass, field
from unittest.mock import MagicMock, patch, AsyncMock
import pytest

# Domain Models
@dataclass
class DomainWatch:
    id: int
    domain: str
    user_id: int
    check_frequency: int = 60
    is_active: bool = True
    last_checked: Optional[datetime] = None
    last_status: Optional[str] = None
    whois_data: Dict[str, Any] = field(default_factory=dict)

# Mock Database
class MockDB:
    def __init__(self):
        self.watches: List[DomainWatch] = []
        self.committed = False
        self.refreshed = False
    
    def add(self, obj):
        self.watches.append(obj)
    
    def commit(self):
        self.committed = True
    
    def refresh(self, obj):
        self.refreshed = True
    
    def query(self, model):
        return MockQuery(self.watches)

class MockQuery:
    def __init__(self, items):
        self.items = items
    
    def filter(self, *args, **kwargs):
        return self
    
    def first(self):
        return self.items[0] if self.items else None
    
    def all(self):
        return self.items

# DomainMonitorService Implementation
class DomainMonitorService:
    def __init__(self):
        self._monitoring = False
    
    def create_watch(self, db: MockDB, user_id: int, domain: str, 
                    check_frequency: int = 60, is_active: bool = True) -> DomainWatch:
        """Create a new domain watch."""
        watch = DomainWatch(
            id=len(db.watches) + 1,
            domain=domain.lower(),
            user_id=user_id,
            check_frequency=check_frequency,
            is_active=is_active
        )
        db.add(watch)
        db.commit()
        return watch
    
    def get_user_watches(self, db: MockDB, user_id: int) -> List[DomainWatch]:
        """Get all watches for a user."""
        return [w for w in db.watches if w.user_id == user_id]
    
    def get_watch(self, db: MockDB, watch_id: int, user_id: int) -> Optional[DomainWatch]:
        """Get a specific watch by ID."""
        for watch in db.watches:
            if watch.id == watch_id and watch.user_id == user_id:
                return watch
        return None
    
    def update_watch(self, db: MockDB, watch_id: int, user_id: int, 
                     update_data: Dict[str, Any]) -> Optional[DomainWatch]:
        """Update a watch."""
        watch = self.get_watch(db, watch_id, user_id)
        if not watch:
            return None
        
        for key, value in update_data.items():
            setattr(watch, key, value)
        
        db.commit()
        db.refresh(watch)
        return watch
    
    def delete_watch(self, db: MockDB, watch_id: int, user_id: int) -> bool:
        """Delete a watch."""
        watch = self.get_watch(db, watch_id, user_id)
        if not watch:
            return False
        
        db.watches = [w for w in db.watches if w.id != watch_id]
        db.commit()
        return True
    
    async def _process_watch(self, db: MockDB, watch: DomainWatch):
        """Process a single domain watch."""
        # Simulate WHOIS lookup
        whois_data = {
            "status": "active",
            "expiration_date": "2025-12-31T23:59:59Z"
        }
        
        # Update watch status
        watch.last_checked = datetime.utcnow()
        watch.last_status = whois_data.get("status")
        watch.whois_data = whois_data
        
        db.commit()
        db.refresh(watch)
    
    async def _monitor_loop(self, db: MockDB, check_interval: int = 300):
        """Monitor domains in the background."""
        self._monitoring = True
        while self._monitoring:
            # Get active watches
            active_watches = [w for w in db.watches if w.is_active]
            
            # Process each watch
            for watch in active_watches:
                await self._process_watch(db, watch)
            
            # Wait for the next check
            try:
                await asyncio.sleep(check_interval)
            except asyncio.CancelledError:
                self._monitoring = False
                raise
    
    def start_monitoring(self, db: MockDB, check_interval: int = 300):
        """Start the monitoring background task."""
        self._monitoring = True
        return asyncio.create_task(self._monitor_loop(db, check_interval))
    
    def stop_monitoring(self):
        """Stop the monitoring background task."""
        self._monitoring = False

# Test Fixtures
@pytest.fixture
def domain_monitor_service():
    return DomainMonitorService()

@pytest.fixture
def mock_db():
    return MockDB()

@pytest.fixture
def test_user():
    return MagicMock(id=1, email="test@example.com")

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
    assert len(mock_db.watches) == 1
    assert mock_db.committed is True

@pytest.mark.asyncio
async def test_get_user_watches(mock_db, test_user, domain_monitor_service):
    """Test getting watches for a user."""
    # Add test watches
    domain_monitor_service.create_watch(mock_db, test_user.id, "example1.com")
    domain_monitor_service.create_watch(mock_db, test_user.id, "example2.com")
    
    watches = domain_monitor_service.get_user_watches(mock_db, test_user.id)
    assert len(watches) == 2
    assert all(w.user_id == test_user.id for w in watches)

@pytest.mark.asyncio
async def test_process_watch(mock_db, test_user, domain_monitor_service):
    """Test processing a watch."""
    watch = domain_monitor_service.create_watch(
        db=mock_db,
        user_id=test_user.id,
        domain="example.com"
    )
    
    await domain_monitor_service._process_watch(mock_db, watch)
    
    assert watch.last_status == "active"
    assert watch.last_checked is not None
    assert "expiration_date" in watch.whois_data

@pytest.mark.asyncio
async def test_monitor_loop(mock_db, test_user, domain_monitor_service):
    """Test the monitoring loop."""
    # Add a test watch
    domain_monitor_service.create_watch(mock_db, test_user.id, "example.com")
    
    # Start monitoring with a short interval
    monitor_task = domain_monitor_service.start_monitoring(mock_db, check_interval=0.1)
    
    # Let it run for a short time
    await asyncio.sleep(0.2)
    
    # Stop monitoring
    domain_monitor_service.stop_monitoring()
    monitor_task.cancel()
    
    # Verify the watch was processed
    watch = mock_db.watches[0]
    assert watch.last_status == "active"
    assert watch.last_checked is not None

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
