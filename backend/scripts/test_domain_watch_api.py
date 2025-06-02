"""Test script for domain watch API endpoints."""
import os
import sys
import time
import asyncio
import logging
from typing import Dict, Any

# Add project root to path
sys.path.append('..')

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER = {
    "email": "test@example.com",
    "password": "testpass123"
}

class TestDomainWatchAPI:
    """Test class for domain watch API endpoints."""
    
    def __init__(self):
        """Initialize test client and auth token."""
        self.client = httpx.AsyncClient()
        self.token = None
        self.watch_id = None
    
    async def login(self):
        """Login and get auth token."""
        logger.info("Logging in...")
        try:
            # First try to register
            response = await self.client.post(
                f"{BASE_URL}/auth/register",
                json={
                    "email": TEST_USER["email"],
                    "password": TEST_USER["password"],
                    "full_name": "Test User"
                }
            )
            
            # Then login
            response = await self.client.post(
                f"{BASE_URL}/auth/login",
                data={
                    "username": TEST_USER["email"],
                    "password": TEST_USER["password"]
                }
            )
            
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.client.headers.update({"Authorization": f"Bearer {self.token}"})
                logger.info("Login successful")
                return True
            else:
                logger.error(f"Login failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return False
    
    async def test_create_watch(self) -> bool:
        """Test creating a domain watch."""
        logger.info("Testing create domain watch...")
        test_domain = f"test-domain-{int(time.time())}.com"
        
        response = await self.client.post(
            f"{BASE_URL}/watches/",
            json={
                "domain": test_domain,
                "is_active": True,
                "check_frequency": 5
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.watch_id = data["id"]
            logger.info(f"Created watch with ID: {self.watch_id}")
            return True
        else:
            logger.error(f"Failed to create watch: {response.text}")
            return False
    
    async def test_get_watch(self) -> bool:
        """Test getting a domain watch."""
        if not self.watch_id:
            logger.error("No watch ID available")
            return False
            
        logger.info(f"Testing get watch {self.watch_id}...")
        response = await self.client.get(f"{BASE_URL}/watches/{self.watch_id}")
        
        if response.status_code == 200:
            logger.info(f"Watch details: {response.json()}")
            return True
        else:
            logger.error(f"Failed to get watch: {response.text}")
            return False
    
    async def test_list_watches(self) -> bool:
        """Test listing domain watches."""
        logger.info("Testing list watches...")
        response = await self.client.get(f"{BASE_URL}/watches/")
        
        if response.status_code == 200:
            watches = response.json()
            logger.info(f"Found {len(watches)} watches")
            return len(watches) > 0
        else:
            logger.error(f"Failed to list watches: {response.text}")
            return False
    
    async def test_check_watch(self) -> bool:
        """Test checking a domain watch."""
        if not self.watch_id:
            logger.error("No watch ID available")
            return False
            
        logger.info(f"Testing check watch {self.watch_id}...")
        response = await self.client.post(
            f"{BASE_URL}/watches/{self.watch_id}/check-now"
        )
        
        if response.status_code == 200:
            logger.info(f"Check result: {response.json()}")
            return True
        else:
            logger.error(f"Failed to check watch: {response.text}")
            return False
    
    async def test_delete_watch(self) -> bool:
        """Test deleting a domain watch."""
        if not self.watch_id:
            logger.error("No watch ID available")
            return False
            
        logger.info(f"Testing delete watch {self.watch_id}...")
        response = await self.client.delete(f"{BASE_URL}/watches/{self.watch_id}")
        
        if response.status_code == 200:
            logger.info("Watch deleted successfully")
            self.watch_id = None
            return True
        else:
            logger.error(f"Failed to delete watch: {response.text}")
            return False
    
    async def run_tests(self):
        """Run all tests."""
        try:
            # Login first
            if not await self.login():
                logger.error("Login failed, aborting tests")
                return False
            
            # Run tests
            tests = [
                self.test_create_watch,
                self.test_get_watch,
                self.test_list_watches,
                self.test_check_watch,
                self.test_delete_watch
            ]
            
            results = {}
            for test in tests:
                test_name = test.__name__
                logger.info(f"\n=== Running test: {test_name} ===")
                try:
                    success = await test()
                    results[test_name] = "PASSED" if success else "FAILED"
                except Exception as e:
                    logger.error(f"Test {test_name} failed with error: {str(e)}", exc_info=True)
                    results[test_name] = "ERROR"
            
            # Print summary
            logger.info("\n=== Test Results ===")
            for test_name, result in results.items():
                logger.info(f"{test_name}: {result}")
            
            return all(v == "PASSED" for v in results.values())
            
        except Exception as e:
            logger.error(f"Test execution failed: {str(e)}", exc_info=True)
            return False
        finally:
            await self.client.aclose()

async def main():
    """Run the tests."""
    tester = TestDomainWatchAPI()
    success = await tester.run_tests()
    
    if success:
        logger.info("\n✅ All tests passed!")
    else:
        logger.error("\n❌ Some tests failed!")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
