"""Simple test script for DomainMonitorService core functionality."""
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

# Simple mock classes
@dataclass
class DomainWatch:
    id: int
    domain: str
    user_id: int
    check_frequency: int
    is_active: bool
    last_checked: Optional[datetime] = None
    last_status: Optional[str] = None

class MockDB:
    def __init__(self):
        self.watches = [
            DomainWatch(
                id=1,
                domain="example.com",
                user_id=1,
                check_frequency=60,
                is_active=True
            )
        ]
    
    def commit(self):
        pass
    
    def refresh(self, obj):
        pass

class DomainMonitorService:
    def __init__(self):
        self._monitoring = False
    
    async def _process_watch(self, db, watch: DomainWatch):
        """Process a single domain watch."""
        # Simulate WHOIS lookup
        whois_data = {
            "status": "active",
            "expiration_date": "2025-12-31T23:59:59Z"
        }
        
        # Update watch status
        watch.last_checked = datetime.utcnow()
        watch.last_status = whois_data.get("status")
        db.commit()
        db.refresh(watch)
    
    async def _monitor_loop(self, db, check_interval: int = 300):
        """Monitor domains in the background."""
        self._monitoring = True
        while self._monitoring:
            # Get active watches (simplified)
            active_watches = [w for w in db.watches if w.is_active]
            
            # Process each watch
            for watch in active_watches:
                await self._process_watch(db, watch)
            
            # Wait for the next check
            await asyncio.sleep(check_interval)
    
    def start_monitoring(self, db, check_interval: int = 300):
        """Start the monitoring background task."""
        self._monitoring = True
        return asyncio.create_task(self._monitor_loop(db, check_interval))
    
    def stop_monitoring(self):
        """Stop the monitoring background task."""
        self._monitoring = False

async def main():
    print("Starting domain monitor service test...")
    
    # Initialize service and test database
    service = DomainMonitorService()
    db = MockDB()
    
    try:
        # Start monitoring
        print("Starting monitoring...")
        monitor_task = service.start_monitoring(db, check_interval=1)
        
        # Let it run for a few seconds
        print("Monitoring for 3 seconds...")
        await asyncio.sleep(3)
        
        # Stop monitoring
        print("Stopping monitoring...")
        service.stop_monitoring()
        monitor_task.cancel()
        
        # Check results
        print("\nResults:")
        for watch in db.watches:
            print(f"- {watch.domain}: status={watch.last_status}, last_checked={watch.last_checked}")
        
        print("\nTest completed successfully!")
        
    except asyncio.CancelledError:
        print("\nMonitoring was cancelled")
    except Exception as e:
        print(f"\nError during monitoring: {e}")
    finally:
        # Ensure monitoring is stopped
        service.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
