#!/usr/bin/env python3
"""
Improved Selenium Automation Script
A more robust and maintainable version with better error handling and configuration management.
"""

import logging
import csv
import os
import time
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException


@dataclass
class Config:
    """Configuration class to manage all settings."""
    default_timeout: int = 10
    send_message_timeout: int = 15
    api_url: str = "https://apisms.eghlym.com/api/Sms/GetMessage?SendByOperatorCode=p2tMpw1C&"
    chrome_profile_path: str = "/Users/shaghayegh-rahmani/Desktop/wbot/chrome_profile/Default"
    log_level: str = "INFO"
    log_file: str = "selenium_automation.log"


class SeleniumAutomation:
    """Main class for Selenium automation with improved error handling."""
    
    def __init__(self, config: Config):
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self) -> bool:
        """Initialize Chrome WebDriver with proper configuration."""
        try:
            chrome_options = Options()
            
            # Add Chrome profile if it exists
            if os.path.exists(self.config.chrome_profile_path):
                chrome_options.add_argument(f"--user-data-dir={os.path.dirname(self.config.chrome_profile_path)}")
                chrome_options.add_argument(f"--profile-directory={os.path.basename(self.config.chrome_profile_path)}")
                self.logger.info(f"Using Chrome profile: {self.config.chrome_profile_path}")
            else:
                self.logger.warning(f"Chrome profile not found: {self.config.chrome_profile_path}")
            
            # Additional Chrome options for stability
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Initialize driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.config.default_timeout)
            
            self.logger.info("Chrome WebDriver initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            return False
    
    def safe_find_element(self, by: By, value: str, timeout: Optional[int] = None) -> Optional[webdriver.remote.webelement.WebElement]:
        """Safely find an element with timeout and error handling."""
        try:
            wait_time = timeout or self.config.default_timeout
            wait = WebDriverWait(self.driver, wait_time)
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except TimeoutException:
            self.logger.warning(f"Element not found within {wait_time} seconds: {by}={value}")
            return None
        except Exception as e:
            self.logger.error(f"Error finding element {by}={value}: {str(e)}")
            return None
    
    def safe_click(self, by: By, value: str, timeout: Optional[int] = None) -> bool:
        """Safely click an element with error handling."""
        element = self.safe_find_element(by, value, timeout)
        if element:
            try:
                element.click()
                self.logger.info(f"Successfully clicked element: {by}={value}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to click element {by}={value}: {str(e)}")
                return False
        return False
    
    def safe_send_keys(self, by: By, value: str, text: str, timeout: Optional[int] = None) -> bool:
        """Safely send keys to an element with error handling."""
        element = self.safe_find_element(by, value, timeout)
        if element:
            try:
                element.clear()
                element.send_keys(text)
                self.logger.info(f"Successfully sent keys to element: {by}={value}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to send keys to element {by}={value}: {str(e)}")
                return False
        return False
    
    def make_api_request(self, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make API request with error handling."""
        try:
            response = requests.get(self.config.api_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            return None
    
    def save_to_csv(self, data: list, filename: str) -> bool:
        """Save data to CSV file with error handling."""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if data and isinstance(data[0], dict):
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
                else:
                    writer = csv.writer(csvfile)
                    writer.writerows(data)
            
            self.logger.info(f"Data saved to CSV: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save CSV file {filename}: {str(e)}")
            return False
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing WebDriver: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        if not self.setup_driver():
            raise RuntimeError("Failed to setup WebDriver")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


def main():
    """Main function to run the automation."""
    # Initialize configuration
    config = Config()
    
    # Run automation with context manager
    try:
        with SeleniumAutomation(config) as automation:
            # Add your automation logic here
            # Example:
            # automation.driver.get("https://example.com")
            # automation.safe_click(By.ID, "login-button")
            # automation.safe_send_keys(By.NAME, "username", "your_username")
            
            automation.logger.info("Automation completed successfully")
            
    except Exception as e:
        logging.error(f"Automation failed: {str(e)}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)