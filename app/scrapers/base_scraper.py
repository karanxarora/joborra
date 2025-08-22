from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self, delay: int = 3):
        self.delay = delay
        self.max_retries = 3
        self.backoff_factor = 2
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_selenium_driver(self) -> webdriver.Chrome:
        """Initialize Selenium Chrome driver with headless options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        return webdriver.Chrome(options=chrome_options)
    
    def make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with error handling and rate limiting"""
        for attempt in range(self.max_retries):
            try:
                time.sleep(self.delay * (self.backoff_factor ** attempt))
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed for {url}: {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"All {self.max_retries} attempts failed for {url}")
                    return None
        return None
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """Parse HTML content with BeautifulSoup"""
        return BeautifulSoup(html_content, 'html.parser')
    
    @abstractmethod
    def scrape_jobs(self, search_terms: List[str], location: str = "Australia") -> List[Dict]:
        """Scrape jobs from the specific job site"""
        pass
    
    @abstractmethod
    def parse_job_details(self, job_element) -> Dict:
        """Parse individual job details from HTML element"""
        pass
    
    def extract_salary(self, salary_text: str) -> tuple:
        """Extract min and max salary from salary text"""
        if not salary_text:
            return None, None
            
        # Remove common currency symbols and text
        salary_text = salary_text.replace('$', '').replace(',', '').replace('AUD', '').strip()
        
        # Handle ranges like "80000 - 120000"
        if ' - ' in salary_text or ' to ' in salary_text:
            parts = salary_text.replace(' to ', ' - ').split(' - ')
            try:
                min_sal = float(parts[0].strip())
                max_sal = float(parts[1].strip())
                return min_sal, max_sal
            except (ValueError, IndexError):
                pass
        
        # Handle single values
        try:
            salary = float(salary_text)
            return salary, salary
        except ValueError:
            pass
            
        return None, None
    
    def normalize_location(self, location: str) -> tuple:
        """Normalize location string to city, state format"""
        if not location:
            return None, None
            
        location = location.strip()
        
        # Australian states mapping
        states = {
            'NSW': 'New South Wales',
            'VIC': 'Victoria', 
            'QLD': 'Queensland',
            'WA': 'Western Australia',
            'SA': 'South Australia',
            'TAS': 'Tasmania',
            'ACT': 'Australian Capital Territory',
            'NT': 'Northern Territory'
        }
        
        # Try to extract state
        for abbr, full_name in states.items():
            if abbr in location.upper() or full_name.lower() in location.lower():
                city = location.replace(abbr, '').replace(full_name, '').strip(' ,')
                return city if city else None, full_name
        
        # If no state found, treat as city
        return location, None
