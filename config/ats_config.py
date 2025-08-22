"""
Configuration for ATS API scrapers and legitimate job sources
"""

import os
from typing import Dict, List

class ATSConfig:
    """Configuration for ATS API access and target companies"""
    
    # API Credentials (set via environment variables)
    ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID')
    ADZUNA_APP_KEY = os.getenv('ADZUNA_APP_KEY')
    WORKABLE_API_TOKEN = os.getenv('WORKABLE_API_TOKEN')
    
    # Target companies for each ATS (discovered through research)
    TARGET_COMPANIES = {
        'greenhouse': [
            # Tech companies using Greenhouse in Australia
            'atlassian',
            'canva', 
            'shopify',
            'stripe',
            'airbnb',
            'uber',
            'spotify',
            'github',
            'slack',
            'dropbox'
        ],
        'lever': [
            # Companies using Lever
            'netflix',
            'uber',
            'spotify', 
            'github',
            'box',
            'coursera',
            'mixpanel',
            'segment'
        ],
        'workable': [
            # Companies using Workable (subdomain format)
            'example-company',
            'startup-co',
            'tech-firm'
        ],
        'smartrecruiters': [
            # Companies using SmartRecruiters (company IDs)
            'company123',
            'startup456'
        ]
    }
    
    # Visa-friendly search terms for Adzuna
    VISA_SEARCH_TERMS = [
        'international students',
        'visa sponsorship',
        'graduate program', 
        'internship',
        'trainee program',
        '482 visa',
        '485 visa',
        'working holiday',
        'overseas applicants'
    ]
    
    # Scraping configuration
    SCRAPING_CONFIG = {
        'delay_between_requests': 2,  # seconds
        'max_retries': 3,
        'timeout': 30,
        'batch_size': 50,
        'max_jobs_per_company': 100
    }
    
    # Australian locations to target
    TARGET_LOCATIONS = [
        'Sydney, NSW',
        'Melbourne, VIC', 
        'Brisbane, QLD',
        'Perth, WA',
        'Adelaide, SA',
        'Canberra, ACT',
        'Australia'
    ]

# Example company discovery data
KNOWN_ATS_COMPANIES = {
    'greenhouse': {
        'atlassian': {
            'name': 'Atlassian',
            'website': 'https://www.atlassian.com',
            'careers_url': 'https://www.atlassian.com/company/careers',
            'greenhouse_url': 'https://boards.greenhouse.io/atlassian',
            'likely_sponsor': True,
            'sectors': ['technology', 'software']
        },
        'canva': {
            'name': 'Canva',
            'website': 'https://www.canva.com',
            'careers_url': 'https://www.canva.com/careers/',
            'greenhouse_url': 'https://boards.greenhouse.io/canva',
            'likely_sponsor': True,
            'sectors': ['technology', 'design']
        }
    },
    'lever': {
        'netflix': {
            'name': 'Netflix',
            'website': 'https://www.netflix.com',
            'careers_url': 'https://jobs.netflix.com',
            'lever_url': 'https://jobs.lever.co/netflix',
            'likely_sponsor': True,
            'sectors': ['technology', 'entertainment']
        }
    }
}

def get_ats_config() -> Dict:
    """Get complete ATS configuration"""
    return {
        'credentials': {
            'adzuna_app_id': ATSConfig.ADZUNA_APP_ID,
            'adzuna_app_key': ATSConfig.ADZUNA_APP_KEY,
            'workable_token': ATSConfig.WORKABLE_API_TOKEN
        },
        'target_companies': ATSConfig.TARGET_COMPANIES,
        'search_terms': ATSConfig.VISA_SEARCH_TERMS,
        'scraping_config': ATSConfig.SCRAPING_CONFIG,
        'locations': ATSConfig.TARGET_LOCATIONS
    }

def validate_config() -> List[str]:
    """Validate configuration and return any issues"""
    issues = []
    
    if not ATSConfig.ADZUNA_APP_ID:
        issues.append("ADZUNA_APP_ID environment variable not set")
    
    if not ATSConfig.ADZUNA_APP_KEY:
        issues.append("ADZUNA_APP_KEY environment variable not set")
    
    if not any(ATSConfig.TARGET_COMPANIES.values()):
        issues.append("No target companies configured for any ATS")
    
    return issues
