#!/usr/bin/env python3
"""
Build Monitor Script

This script monitors build processes and provides real-time updates on their status.
It can be used to track long-running builds and check their progress.
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from typing import Optional, Dict, List, Tuple

class BuildMonitor:
    def __init__(self, check_interval: int = 30, max_attempts: int = 120):
        """Initialize the build monitor.
        
        Args:
            check_interval: Seconds to wait between status checks
            max_attempts: Maximum number of checks before giving up
        """
        self.check_interval = check_interval
        self.max_attempts = max_attempts
        self.log_file = "build_monitor.log"
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up logging for the build monitor."""
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log_status(self, message: str, level: str = "info"):
        """Log a status message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        if level.lower() == "error":
            self.logger.error(log_message)
        elif level.lower() == "warning":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def check_process_running(self, process_name: str) -> bool:
        """Check if a process is currently running."""
        try:
            output = subprocess.check_output(['pgrep', '-f', process_name])
            return bool(output.strip())
        except subprocess.CalledProcessError:
            return False
    
    def monitor_build(self, process_name: str, build_command: str):
        """Monitor a build process.
        
        Args:
            process_name: Name of the process to monitor
            build_command: Command to run the build
        """
        self.log_status(f"Starting build monitoring for: {process_name}")
        
        # Start the build process
        try:
            self.log_status(f"Starting build with command: {build_command}")
            process = subprocess.Popen(
                build_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor the process
            attempt = 0
            while attempt < self.max_attempts:
                if process.poll() is not None:  # Process has finished
                    break
                    
                # Read output if available
                output = process.stdout.readline()
                if output:
                    self.log_status(f"[BUILD] {output.strip()}")
                
                # Check process status
                if not self.check_process_running(process_name):
                    self.log_status("Build process not found. It may have completed or failed.", "warning")
                    break
                
                attempt += 1
                if attempt < self.max_attempts:
                    time.sleep(self.check_interval)
            
            # Check final status
            if process.poll() is None:
                self.log_status("Build monitoring timed out.", "error")
                process.terminate()
            elif process.returncode == 0:
                self.log_status("Build completed successfully!")
            else:
                self.log_status(f"Build failed with return code {process.returncode}", "error")
                
        except Exception as e:
            self.log_status(f"Error monitoring build: {str(e)}", "error")
        finally:
            if 'process' in locals() and process.poll() is None:
                process.terminate()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor build processes.')
    parser.add_argument('process_name', help='Name of the process to monitor')
    parser.add_argument('build_command', help='Command to run the build')
    parser.add_argument('--interval', type=int, default=30, 
                        help='Seconds between status checks (default: 30)')
    parser.add_argument('--attempts', type=int, default=120,
                        help='Maximum number of checks (default: 120)')
    
    args = parser.parse_args()
    
    monitor = BuildMonitor(
        check_interval=args.interval,
        max_attempts=args.attempts
    )
    
    monitor.monitor_build(args.process_name, args.build_command)

if __name__ == "__main__":
    main()
