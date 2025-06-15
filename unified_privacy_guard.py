#!/usr/bin/env python3
"""
Unified Privacy Guard Script

This script integrates all components:
- Browser Extension + Central Server data retrieval
- Face Detection API
- LLM Sensitivity Analysis
- Screen Brightness Control

The script automatically dims the screen when:
1. More than 1 face is detected AND
2. The current browser content is deemed sensitive by the LLM
"""

import asyncio
import aiohttp
import requests
import time
import json
import logging
import subprocess
import os
from typing import Dict, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScreenController:
    """Controls screen brightness on Windows systems."""
    
    def __init__(self):
        self._original_brightness = self._get_current_brightness()
        self._dimmed_brightness = 30  # Default dimmed brightness percentage
        self._is_dimmed = False
    
    def _get_current_brightness(self) -> int:
        """Get the current screen brightness using PowerShell."""
        try:
            cmd = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                check=True
            )
            brightness = int(result.stdout.strip())
            return brightness
        except Exception as e:
            logger.error(f"Error getting screen brightness: {e}")
            return 100
    
    def dim_screen(self, dim_percentage: Optional[int] = None) -> bool:
        """Dim the screen to the specified percentage."""
        if dim_percentage is not None:
            self._dimmed_brightness = dim_percentage
        
        try:
            cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {self._dimmed_brightness})"
            subprocess.run(["powershell", "-Command", cmd], check=True)
            self._is_dimmed = True
            logger.info(f"Screen dimmed to {self._dimmed_brightness}%")
            return True
        except Exception as e:
            logger.error(f"Error dimming screen: {e}")
            return False
    
    def restore_brightness(self) -> bool:
        """Restore the screen brightness to its original value."""
        try:
            cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {self._original_brightness})"
            subprocess.run(["powershell", "-Command", cmd], check=True)
            self._is_dimmed = False
            logger.info(f"Screen brightness restored to {self._original_brightness}%")
            return True
        except Exception as e:
            logger.error(f"Error restoring screen brightness: {e}")
            return False
    
    @property
    def is_dimmed(self) -> bool:
        return self._is_dimmed

class FaceDetectionClient:
    """Client for face detection API."""
    
    def __init__(self, api_url: str = "http://127.0.0.1:8000/face-count"):
        self.api_url = api_url
    
    def get_face_count(self) -> int:
        """Get the current face count from the face detection API."""
        try:
            response = requests.get(self.api_url, timeout=3)
            response.raise_for_status()
            data = response.json()
            return int(data.get("count", 0))
        except Exception as e:
            logger.error(f"Error getting face count: {e}")
            return 0

class BrowserDataClient:
    """Client for browser extension data via central server."""
    
    def __init__(self, server_url: str = "http://localhost:3000/api/storage"):
        self.server_url = server_url
        self.storage_key = "latest_tab_event"
    
    def get_latest_browser_data(self) -> Dict[str, Any]:
        """Get the latest browser data from central server."""
        try:
            response = requests.get(f"{self.server_url}/{self.storage_key}", timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data.get("success") and "data" in data:
                event_data = data["data"]
                
                # Extract relevant information from the event
                browser_data = {
                    "url": "",
                    "title": "",
                    "dom": "",
                    "screenshot": "",
                    "timestamp": event_data.get("timestamp", 0)
                }
                
                # Handle different event types
                event_type = event_data.get("event", "")
                event_payload = event_data.get("data", {})
                
                if event_type in ["tab_activated", "tab_updated", "tab_data_captured"]:
                    browser_data["url"] = event_payload.get("url", "")
                    browser_data["title"] = event_payload.get("title", "")
                    browser_data["screenshot"] = event_payload.get("screenshot", "")
                
                elif event_type == "full_html_captured":
                    browser_data["url"] = event_payload.get("url", "")
                    browser_data["title"] = event_payload.get("title", "")
                    browser_data["dom"] = event_payload.get("bodyHTML", "")
                
                elif event_type == "dom_data_updated":
                    browser_data["url"] = event_payload.get("url", "")
                    dom_data = event_payload.get("domData", {})
                    browser_data["dom"] = dom_data.get("bodyText", "")
                
                return browser_data
            
            return {"url": "", "title": "", "dom": "", "screenshot": "", "timestamp": 0}
            
        except Exception as e:
            logger.error(f"Error getting browser data: {e}")
            return {"url": "", "title": "", "dom": "", "screenshot": "", "timestamp": 0}

class SensitivityChecker:
    """LLM-based content sensitivity checker."""
    
    def __init__(self, llm_url: str = "http://localhost:3001/api/v1/openai/chat/completions"):
        self.llm_url = llm_url
        self.api_token = os.environ.get("API_TOKEN", "")
        self.workspace_name = os.environ.get("WORKSPACE_NAME", "default")
    
    def is_sensitive(self, content: str, url: str) -> bool:
        """Check if the given content is sensitive using LLM."""
        system_prompt = (
            "You are a helpful assistant that determines if web content is sensitive. "
            "If the content contains personal, financial, confidential, or private information, answer 'yes'. "
            "Otherwise, answer 'no'. Respond with only 'yes' or 'no'."
        )
        
        user_prompt = (
            f"URL: {url}\n"
            f"Content: {content[:2000]}\n"  # Truncate to 2000 chars
            "Is the content sensitive?"
        )
        
        payload = {
            "model": self.workspace_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0
        }
        
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_token:
                headers['Authorization'] = f'Bearer {self.api_token}'
            
            response = requests.post(self.llm_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            answer = data["choices"][0]["message"]["content"].strip().lower()
            is_sensitive = answer.startswith("y")
            
            logger.info(f"Content sensitivity check: {is_sensitive} for URL: {url[:50]}...")
            return is_sensitive
            
        except Exception as e:
            logger.error(f"Error checking content sensitivity: {e}")
            return False  # Default to not sensitive if LLM fails

class UnifiedPrivacyGuard:
    """Main privacy guard controller that integrates all components."""
    
    def __init__(self, 
                 face_api_url: str = "http://127.0.0.1:8000/face-count",
                 browser_server_url: str = "http://localhost:3000/api/storage",
                 llm_url: str = "http://localhost:3001/api/v1/openai/chat/completions",
                 check_interval: float = 2.0):
        
        self.face_client = FaceDetectionClient(face_api_url)
        self.browser_client = BrowserDataClient(browser_server_url)
        self.sensitivity_checker = SensitivityChecker(llm_url)
        self.screen_controller = ScreenController()
        self.check_interval = check_interval
        
        self.last_check_time = 0
        self.last_browser_data = {}
        self.running = False
        
        logger.info("Unified Privacy Guard initialized")
    
    def should_dim_screen(self) -> tuple[bool, str]:
        """
        Determine if screen should be dimmed based on face count and content sensitivity.
        Returns (should_dim, reason)
        """
        # Get face count
        face_count = self.face_client.get_face_count()
        logger.debug(f"Face count: {face_count}")
        
        # If only 1 or fewer faces, no need to dim
        if face_count <= 1:
            return False, f"Only {face_count} face(s) detected"
        
        # Get browser data
        browser_data = self.browser_client.get_latest_browser_data()
        
        # Check if we have new data
        if browser_data["timestamp"] == self.last_browser_data.get("timestamp", 0):
            # No new data, use previous decision but check face count
            if face_count > 1 and self.screen_controller.is_dimmed:
                return True, "Multiple faces detected, keeping screen dimmed"
            return False, "No new browser data"
        
        self.last_browser_data = browser_data
        
        url = browser_data.get("url", "")
        dom_content = browser_data.get("dom", "")
        title = browser_data.get("title", "")
        
        # Combine available content for sensitivity analysis
        content_to_analyze = f"{title} {dom_content}".strip()
        
        if not content_to_analyze and not url:
            return False, "No content to analyze"
        
        # Check content sensitivity
        is_sensitive = self.sensitivity_checker.is_sensitive(content_to_analyze, url)
        
        if face_count > 1 and is_sensitive:
            return True, f"Multiple faces ({face_count}) detected with sensitive content"
        
        return False, f"Content not sensitive or insufficient faces ({face_count})"
    
    def update_screen_state(self):
        """Update screen brightness based on current conditions."""
        should_dim, reason = self.should_dim_screen()
        
        if should_dim and not self.screen_controller.is_dimmed:
            logger.info(f"Dimming screen: {reason}")
            self.screen_controller.dim_screen()
        elif not should_dim and self.screen_controller.is_dimmed:
            logger.info(f"Restoring screen brightness: {reason}")
            self.screen_controller.restore_brightness()
        else:
            logger.debug(f"Screen state unchanged: {reason}")
    
    def run_once(self):
        """Run a single check cycle."""
        try:
            self.update_screen_state()
        except Exception as e:
            logger.error(f"Error in check cycle: {e}")
    
    def run(self):
        """Run the privacy guard continuously."""
        self.running = True
        logger.info("Starting Unified Privacy Guard...")
        logger.info(f"Check interval: {self.check_interval} seconds")
        
        try:
            while self.running:
                start_time = time.time()
                
                self.run_once()
                
                # Calculate sleep time to maintain consistent interval
                elapsed = time.time() - start_time
                sleep_time = max(0, self.check_interval - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the privacy guard and restore screen brightness."""
        self.running = False
        logger.info("Stopping Unified Privacy Guard...")
        
        # Restore screen brightness before exiting
        if self.screen_controller.is_dimmed:
            self.screen_controller.restore_brightness()
        
        logger.info("Privacy Guard stopped")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Privacy Guard")
    parser.add_argument(
        "--face-api-url",
        default="http://127.0.0.1:8000/face-count",
        help="Face detection API URL"
    )
    parser.add_argument(
        "--browser-server-url",
        default="http://localhost:3000/api/storage",
        help="Browser extension central server URL"
    )
    parser.add_argument(
        "--llm-url",
        default="http://localhost:3001/api/v1/openai/chat/completions",
        help="LLM API URL"
    )
    parser.add_argument(
        "--check-interval",
        type=float,
        default=2.0,
        help="Check interval in seconds"
    )
    parser.add_argument(
        "--test-once",
        action="store_true",
        help="Run once and exit (for testing)"
    )
    
    args = parser.parse_args()
    
    # Create privacy guard instance
    privacy_guard = UnifiedPrivacyGuard(
        face_api_url=args.face_api_url,
        browser_server_url=args.browser_server_url,
        llm_url=args.llm_url,
        check_interval=args.check_interval
    )
    
    if args.test_once:
        logger.info("Running single test cycle...")
        privacy_guard.run_once()
        logger.info("Test completed")
    else:
        # Run continuously
        privacy_guard.run()

if __name__ == "__main__":
    main()
