import time
import subprocess
import json
from datetime import datetime
import requests

class BuildMonitor:
    def __init__(self, build_id=None, check_interval=5):
        self.build_id = build_id
        self.check_interval = check_interval
        self.last_status = None
        self.logs = []
        
    def start_monitoring(self, build_id=None):
        if build_id:
            self.build_id = build_id
        if not self.build_id:
            raise ValueError("Build ID must be provided")
            
        print(f"Starting build monitoring for build ID: {self.build_id}")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                status = self.check_build_status()
                if status != self.last_status:
                    self.last_status = status
                    print(f"\nBuild Status Changed: {status}")
                    print("-" * 50)
                
                if status == "completed":
                    print("\nBuild completed!")
                    break
                    
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            
    def check_build_status(self):
        try:
            # This is a placeholder - replace with actual API endpoint
            response = requests.get(f"http://localhost:5003/api/v1/builds/{self.build_id}/status")
            response.raise_for_status()
            
            data = response.json()
            status = data.get('status', 'unknown')
            
            # Get logs if available
            logs = data.get('logs', [])
            if logs:
                new_logs = [log for log in logs if log not in self.logs]
                if new_logs:
                    print("\nNew Build Logs:")
                    for log in new_logs:
                        print(f"{log['timestamp']}: {log['message']}")
                    self.logs.extend(new_logs)
                    
            return status
            
        except requests.exceptions.RequestException as e:
            print(f"Error checking build status: {str(e)}")
            return "error"
            
    def get_logs(self):
        try:
            response = requests.get(f"http://localhost:5003/api/v1/builds/{self.build_id}/logs")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching build logs: {str(e)}")
            return []

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Build Monitoring Script')
    parser.add_argument('--build-id', required=True, help='Build ID to monitor')
    parser.add_argument('--interval', type=int, default=5, help='Check interval in seconds')
    
    args = parser.parse_args()
    
    monitor = BuildMonitor(build_id=args.build_id, check_interval=args.interval)
    monitor.start_monitoring()
