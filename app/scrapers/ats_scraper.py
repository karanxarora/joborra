"""
ATS API Scrapers for legitimate job data collection
Supports Greenhouse, Lever, Workable, and SmartRecruiters APIs
"""

import requests
import time
import logging
from typing import List, Dict, Optional, Set
from datetime import datetime, timezone
import json
from urllib.parse import urljoin, quote
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class ATSScraper(BaseScraper):
    """Base class for ATS API scrapers"""
    
    def __init__(self, delay: int = 1):
        super().__init__(delay)
        self.visa_keywords = self._load_visa_keywords()
        
    def _load_visa_keywords(self) -> Dict[str, List[str]]:
        """Load visa-related keywords for filtering"""
        return {
            'positive': [
                'international students', 'student visa', 'graduate visa',
                '485 visa', '500 visa', 'subclass 485', 'subclass 500',
                'subclass 482', '482 visa', 'TSS visa', 'sponsorship',
                'visa sponsorship', 'employer sponsorship', 'work rights',
                'full working rights', 'valid visa', 'eligible to work in Australia',
                'work permit', 'internship', 'graduate program', 'graduate role',
                'trainee program', 'cadetship', 'welcome international',
                'open to candidates requiring sponsorship', 'overseas applicants welcome',
                'visa support', 'support for relocation'
            ],
            'negative': [
                'Australian citizen only', 'must be an Australian citizen',
                'Australian citizenship required', 'must be PR',
                'permanent resident only', 'security clearance required',
                'baseline clearance', 'NV1 clearance', 'NV2 clearance'
            ]
        }
    
    def analyze_visa_friendliness(self, job_data: Dict) -> tuple:
        """Analyze job description for visa-friendly indicators"""
        text = f"{job_data.get('title', '')} {job_data.get('description', '')}".lower()
        
        positive_score = 0
        negative_score = 0
        
        for keyword in self.visa_keywords['positive']:
            if keyword.lower() in text:
                positive_score += 1
                
        for keyword in self.visa_keywords['negative']:
            if keyword.lower() in text:
                negative_score += 2  # Negative keywords have higher weight
        
        # Calculate confidence score (0-1)
        total_keywords = len(self.visa_keywords['positive']) + len(self.visa_keywords['negative'])
        confidence = min(positive_score / (total_keywords * 0.1), 1.0) if positive_score > 0 else 0.0
        
        # Reduce confidence if negative keywords found
        if negative_score > 0:
            confidence = max(0.0, confidence - (negative_score * 0.3))
        
        is_visa_friendly = positive_score > 0 and negative_score == 0
        is_student_friendly = any(kw in text for kw in ['student', 'graduate', 'internship', 'trainee'])
        
        return is_visa_friendly, confidence, is_student_friendly


class GreenhouseScraper(ATSScraper):
    """Scraper for Greenhouse Job Board API"""
    
    def __init__(self, delay: int = 1):
        super().__init__(delay)
        self.base_url = "https://boards-api.greenhouse.io/v1/boards"
    
    def parse_job_details(self, job_element) -> Dict:
        """Parse individual job details from API response"""
        return self._process_greenhouse_job(job_element, "")
    
    def get_company_jobs(self, company_token: str) -> List[Dict]:
        """Get all jobs for a specific company from Greenhouse"""
        url = f"{self.base_url}/{company_token}/jobs"
        
        try:
            response = self.make_request(url)
            if not response:
                return []
            
            jobs_data = response.json()
            jobs = []
            
            for job in jobs_data.get('jobs', []):
                processed_job = self._process_greenhouse_job(job, company_token)
                if processed_job:
                    jobs.append(processed_job)
            
            logger.info(f"Found {len(jobs)} jobs from Greenhouse company {company_token}")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping Greenhouse company {company_token}: {e}")
            return []
    
    def _process_greenhouse_job(self, job_data: Dict, company_token: str) -> Optional[Dict]:
        """Process individual Greenhouse job"""
        try:
            # Extract job details
            title = job_data.get('title', '')
            description = job_data.get('content', '')
            
            # Get location info
            location_data = job_data.get('location', {})
            location = location_data.get('name', '') if location_data else ''
            city, state = self.normalize_location(location)
            
            # Analyze visa friendliness
            visa_friendly, confidence, student_friendly = self.analyze_visa_friendliness({
                'title': title,
                'description': description
            })
            
            return {
                'title': title,
                'description': description,
                'company_name': company_token,  # Will need to resolve to actual company name
                'location': location,
                'city': city,
                'state': state,
                'employment_type': self._extract_employment_type(description),
                'source_website': 'greenhouse.io',
                'source_url': job_data.get('absolute_url', ''),
                'source_job_id': str(job_data.get('id', '')),
                'posted_date': self._parse_date(job_data.get('updated_at')),
                'visa_sponsorship': visa_friendly,
                'visa_sponsorship_confidence': confidence,
                'international_student_friendly': student_friendly,
                'is_active': True
            }
            
        except Exception as e:
            logger.error(f"Error processing Greenhouse job: {e}")
            return None
    
    def scrape_jobs(self, company_tokens: List[str], location: str = "Australia") -> List[Dict]:
        """Scrape jobs from multiple Greenhouse companies"""
        all_jobs = []
        
        for token in company_tokens:
            jobs = self.get_company_jobs(token)
            all_jobs.extend(jobs)
            time.sleep(self.delay)
        
        return all_jobs


class LeverScraper(ATSScraper):
    """Scraper for Lever Postings API"""
    
    def __init__(self, delay: int = 1):
        super().__init__(delay)
        self.base_url = "https://api.lever.co/v0/postings"
    
    def parse_job_details(self, job_element) -> Dict:
        """Parse individual job details from API response"""
        return self._process_lever_job(job_element, "")
    
    def get_company_jobs(self, company_name: str) -> List[Dict]:
        """Get all jobs for a specific company from Lever"""
        url = f"{self.base_url}/{company_name}"
        
        try:
            response = self.make_request(url)
            if not response:
                return []
            
            jobs_data = response.json()
            jobs = []
            
            for job in jobs_data:
                processed_job = self._process_lever_job(job, company_name)
                if processed_job:
                    jobs.append(processed_job)
            
            logger.info(f"Found {len(jobs)} jobs from Lever company {company_name}")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping Lever company {company_name}: {e}")
            return []
    
    def _process_lever_job(self, job_data: Dict, company_name: str) -> Optional[Dict]:
        """Process individual Lever job"""
        try:
            title = job_data.get('text', '')
            description = job_data.get('description', '')
            
            # Get location info
            location_data = job_data.get('categories', {}).get('location', '')
            city, state = self.normalize_location(location_data)
            
            # Analyze visa friendliness
            visa_friendly, confidence, student_friendly = self.analyze_visa_friendliness({
                'title': title,
                'description': description
            })
            
            return {
                'title': title,
                'description': description,
                'company_name': company_name,
                'location': location_data,
                'city': city,
                'state': state,
                'employment_type': job_data.get('categories', {}).get('commitment', ''),
                'source_website': 'lever.co',
                'source_url': job_data.get('hostedUrl', ''),
                'source_job_id': job_data.get('id', ''),
                'posted_date': self._parse_date(job_data.get('createdAt')),
                'visa_sponsorship': visa_friendly,
                'visa_sponsorship_confidence': confidence,
                'international_student_friendly': student_friendly,
                'is_active': True
            }
            
        except Exception as e:
            logger.error(f"Error processing Lever job: {e}")
            return None
    
    def scrape_jobs(self, company_names: List[str], location: str = "Australia") -> List[Dict]:
        """Scrape jobs from multiple Lever companies"""
        all_jobs = []
        
        for company in company_names:
            jobs = self.get_company_jobs(company)
            all_jobs.extend(jobs)
            time.sleep(self.delay)
        
        return all_jobs


class WorkableScraper(ATSScraper):
    """Scraper for Workable Jobs API"""
    
    def __init__(self, api_token: str = None, delay: int = 1):
        super().__init__(delay)
        self.api_token = api_token
        self.base_url = "https://www.workable.com/spi/v3"
        if api_token:
            self.session.headers.update({
                'Authorization': f'Bearer {api_token}'
            })
    
    def parse_job_details(self, job_element) -> Dict:
        """Parse individual job details from API response"""
        return self._process_workable_job(job_element, "")
    
    def get_company_jobs(self, company_subdomain: str) -> List[Dict]:
        """Get all jobs for a specific company from Workable"""
        # Public endpoint (no auth required)
        url = f"https://{company_subdomain}.workable.com/api/v1/published"
        
        try:
            response = self.make_request(url)
            if not response:
                return []
            
            jobs_data = response.json()
            jobs = []
            
            for job in jobs_data.get('jobs', []):
                processed_job = self._process_workable_job(job, company_subdomain)
                if processed_job:
                    jobs.append(processed_job)
            
            logger.info(f"Found {len(jobs)} jobs from Workable company {company_subdomain}")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping Workable company {company_subdomain}: {e}")
            return []
    
    def _process_workable_job(self, job_data: Dict, company_subdomain: str) -> Optional[Dict]:
        """Process individual Workable job"""
        try:
            title = job_data.get('title', '')
            description = job_data.get('description', '')
            
            # Get location info
            location = job_data.get('location', {}).get('city', '')
            city, state = self.normalize_location(location)
            
            # Analyze visa friendliness
            visa_friendly, confidence, student_friendly = self.analyze_visa_friendliness({
                'title': title,
                'description': description
            })
            
            return {
                'title': title,
                'description': description,
                'company_name': company_subdomain,
                'location': location,
                'city': city,
                'state': state,
                'employment_type': job_data.get('type', ''),
                'source_website': 'workable.com',
                'source_url': job_data.get('url', ''),
                'source_job_id': job_data.get('id', ''),
                'posted_date': self._parse_date(job_data.get('published')),
                'visa_sponsorship': visa_friendly,
                'visa_sponsorship_confidence': confidence,
                'international_student_friendly': student_friendly,
                'is_active': True
            }
            
        except Exception as e:
            logger.error(f"Error processing Workable job: {e}")
            return None
    
    def scrape_jobs(self, company_subdomains: List[str], location: str = "Australia") -> List[Dict]:
        """Scrape jobs from multiple Workable companies"""
        all_jobs = []
        
        for subdomain in company_subdomains:
            jobs = self.get_company_jobs(subdomain)
            all_jobs.extend(jobs)
            time.sleep(self.delay)
        
        return all_jobs


class SmartRecruitersScaper(ATSScraper):
    """Scraper for SmartRecruiters Jobs API"""
    
    def __init__(self, delay: int = 1):
        super().__init__(delay)
        self.base_url = "https://api.smartrecruiters.com/v1"
    
    def parse_job_details(self, job_element) -> Dict:
        """Parse individual job details from API response"""
        return self._process_smartrecruiters_job(job_element, "")
    
    def get_company_jobs(self, company_id: str) -> List[Dict]:
        """Get all jobs for a specific company from SmartRecruiters"""
        url = f"{self.base_url}/companies/{company_id}/postings"
        
        try:
            response = self.make_request(url)
            if not response:
                return []
            
            jobs_data = response.json()
            jobs = []
            
            for job in jobs_data.get('content', []):
                processed_job = self._process_smartrecruiters_job(job, company_id)
                if processed_job:
                    jobs.append(processed_job)
            
            logger.info(f"Found {len(jobs)} jobs from SmartRecruiters company {company_id}")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping SmartRecruiters company {company_id}: {e}")
            return []
    
    def _process_smartrecruiters_job(self, job_data: Dict, company_id: str) -> Optional[Dict]:
        """Process individual SmartRecruiters job"""
        try:
            title = job_data.get('name', '')
            description = job_data.get('jobAd', {}).get('sections', {}).get('jobDescription', {}).get('text', '')
            
            # Get location info
            location_data = job_data.get('location', {})
            location = f"{location_data.get('city', '')}, {location_data.get('country', '')}"
            city, state = self.normalize_location(location)
            
            # Analyze visa friendliness
            visa_friendly, confidence, student_friendly = self.analyze_visa_friendliness({
                'title': title,
                'description': description
            })
            
            return {
                'title': title,
                'description': description,
                'company_name': job_data.get('company', {}).get('name', company_id),
                'location': location,
                'city': city,
                'state': state,
                'employment_type': job_data.get('typeOfEmployment', {}).get('label', ''),
                'source_website': 'smartrecruiters.com',
                'source_url': job_data.get('ref', ''),
                'source_job_id': job_data.get('id', ''),
                'posted_date': self._parse_date(job_data.get('releasedDate')),
                'visa_sponsorship': visa_friendly,
                'visa_sponsorship_confidence': confidence,
                'international_student_friendly': student_friendly,
                'is_active': True
            }
            
        except Exception as e:
            logger.error(f"Error processing SmartRecruiters job: {e}")
            return None
    
    def scrape_jobs(self, company_ids: List[str], location: str = "Australia") -> List[Dict]:
        """Scrape jobs from multiple SmartRecruiters companies"""
        all_jobs = []
        
        for company_id in company_ids:
            jobs = self.get_company_jobs(company_id)
            all_jobs.extend(jobs)
            time.sleep(self.delay)
        
        return all_jobs


# Shared utility methods for all ATS scrapers
def _extract_employment_type(description: str) -> str:
    """Extract employment type from job description"""
    description_lower = description.lower()
    
    if any(term in description_lower for term in ['intern', 'internship']):
        return 'internship'
    elif any(term in description_lower for term in ['contract', 'contractor', 'freelance']):
        return 'contract'
    elif any(term in description_lower for term in ['part-time', 'part time']):
        return 'part-time'
    else:
        return 'full-time'

def _parse_date(date_string: str) -> Optional[datetime]:
    """Parse date string to datetime object"""
    if not date_string:
        return None
    
    try:
        # Handle ISO format
        if 'T' in date_string:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        else:
            return datetime.strptime(date_string, '%Y-%m-%d')
    except (ValueError, TypeError):
        return None

# Add these methods to the base class
ATSScraper._extract_employment_type = staticmethod(_extract_employment_type)
ATSScraper._parse_date = staticmethod(_parse_date)
