#!/usr/bin/env python3
"""
Simple test of Adzuna API to debug the 400 error
"""

import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adzuna API credentials
ADZUNA_APP_ID = "81a172a4"
ADZUNA_APP_KEY = "b003298d4b1d24c1302d9aad5183ec6b"

def test_adzuna_direct():
    """Test Adzuna API directly with minimal parameters"""
    
    # Basic search URL
    url = "https://api.adzuna.com/v1/api/jobs/au/search/1"
    
    params = {
        'app_id': ADZUNA_APP_ID,
        'app_key': ADZUNA_APP_KEY
    }
    
    logger.info(f"Testing Adzuna API: {url}")
    logger.info(f"Parameters: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Success! Found {data.get('count', 0)} jobs")
            logger.info(f"Results: {len(data.get('results', []))}")
            
            # Show first job
            if data.get('results'):
                job = data['results'][0]
                logger.info(f"Sample job: {job.get('title', 'N/A')} at {job.get('company', {}).get('display_name', 'N/A')}")
            
            return data
        else:
            logger.error(f"API Error: {response.status_code}")
            logger.error(f"Response text: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return None

def test_with_search_terms():
    """Test with specific search terms"""
    
    url = "https://api.adzuna.com/v1/api/jobs/au/search/1"
    
    params = {
        'app_id': ADZUNA_APP_ID,
        'app_key': ADZUNA_APP_KEY,
        'what': 'software developer',
        'where': 'sydney',
        'results_per_page': 10
    }
    
    logger.info(f"Testing with search terms: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Success! Found {data.get('count', 0)} software developer jobs in Sydney")
            return data
        else:
            logger.error(f"API Error: {response.status_code}")
            logger.error(f"Response text: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return None

if __name__ == "__main__":
    logger.info("Testing Adzuna API directly...")
    
    # Test 1: Basic request
    result1 = test_adzuna_direct()
    
    # Test 2: With search terms
    if result1:
        result2 = test_with_search_terms()
