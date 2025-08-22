"""
Adzuna Jobs API Scraper for legitimate job aggregation
"""

import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
from .ats_scraper import ATSScraper

logger = logging.getLogger(__name__)

class AdzunaScraper(ATSScraper):
    """Scraper for Adzuna Jobs API - legitimate aggregator"""
    
    def __init__(self, app_id: str, app_key: str, delay: int = 1):
        super().__init__(delay)
        self.app_id = app_id
        self.app_key = app_key
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self.country = "au"  # Australia
    
    def parse_job_details(self, job_element) -> Dict:
        """Parse individual job details from API response"""
        return self._process_adzuna_job(job_element)
        
    def search_jobs(self, 
                   what: str = "", 
                   where: str = "australia", 
                   max_days_old: int = 30,
                   results_per_page: int = 20,
                   page: int = 1) -> List[Dict]:
        """Search jobs using Adzuna API"""
        
        url = f"{self.base_url}/{self.country}/search/{page}"
        
        params = {
            'app_id': self.app_id,
            'app_key': self.app_key,
            'results_per_page': min(results_per_page, 50)  # Max 50 per API docs
        }
        
        if what:
            params['what'] = what
        if where and where.lower() != 'australia':
            params['where'] = where
        if max_days_old:
            params['max_days_old'] = max_days_old
            
        try:
            # Use GET request with params
            import requests
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            jobs = []
            
            for job_data in data.get('results', []):
                processed_job = self._process_adzuna_job(job_data)
                if processed_job:
                    jobs.append(processed_job)
            
            logger.info(f"Found {len(jobs)} jobs from Adzuna for query: '{what}' in '{where}'")
            return jobs
            
        except Exception as e:
            logger.error(f"Error searching Adzuna jobs: {e}")
            return []
    
    def search_visa_friendly_jobs(self, location: str = "australia") -> List[Dict]:
        """Search for visa-friendly jobs using relevant keywords"""
        all_jobs = []
        
        # Search terms that are likely to yield visa-friendly results
        search_terms = [
            "international students",
            "visa sponsorship", 
            "graduate program",
            "internship",
            "trainee program",
            "482 visa",
            "485 visa"
        ]
        
        for term in search_terms:
            jobs = self.search_jobs(what=term, where=location)
            all_jobs.extend(jobs)
            
        # Remove duplicates based on source_job_id
        seen_ids = set()
        unique_jobs = []
        for job in all_jobs:
            job_id = job.get('source_job_id')
            if job_id and job_id not in seen_ids:
                seen_ids.add(job_id)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _process_adzuna_job(self, job_data: Dict) -> Optional[Dict]:
        """Process individual Adzuna job"""
        try:
            title = job_data.get('title', '')
            description = job_data.get('description', '')
            
            # Get location info
            location_data = job_data.get('location', {})
            location_display = location_data.get('display_name', '')
            city, state = self.normalize_location(location_display)
            
            # Get company info
            company_data = job_data.get('company', {})
            company_name = company_data.get('display_name', '')
            
            # Get salary info
            salary_min = job_data.get('salary_min')
            salary_max = job_data.get('salary_max')
            
            # Analyze visa friendliness
            visa_friendly, confidence, student_friendly = self.analyze_visa_friendliness({
                'title': title,
                'description': description
            })
            
            return {
                'title': title,
                'description': description,
                'company_name': company_name,
                'location': location_display,
                'city': city,
                'state': state,
                'salary_min': salary_min,
                'salary_max': salary_max,
                'salary_currency': 'AUD',
                'employment_type': self._extract_employment_type(description),
                'source_website': 'adzuna.com.au',
                'source_url': job_data.get('redirect_url', ''),
                'source_job_id': job_data.get('id', ''),
                'posted_date': self._parse_date(job_data.get('created')),
                'visa_sponsorship': visa_friendly,
                'visa_sponsorship_confidence': confidence,
                'international_student_friendly': student_friendly,
                'is_active': True
            }
            
        except Exception as e:
            logger.error(f"Error processing Adzuna job: {e}")
            return None
    
    def scrape_jobs(self, search_terms: List[str], location: str = "Australia") -> List[Dict]:
        """Scrape jobs using multiple search terms"""
        all_jobs = []
        
        for term in search_terms:
            jobs = self.search_jobs(what=term, where=location)
            all_jobs.extend(jobs)
        
        # Remove duplicates
        seen_ids = set()
        unique_jobs = []
        for job in all_jobs:
            job_id = job.get('source_job_id')
            if job_id and job_id not in seen_ids:
                seen_ids.add(job_id)
                unique_jobs.append(job)
        
        return unique_jobs
