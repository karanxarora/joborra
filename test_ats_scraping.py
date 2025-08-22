#!/usr/bin/env python3
"""
Test the new ATS scraping system with real Adzuna data
"""

import logging
import os
from datetime import datetime
from app.scrapers.adzuna_scraper import AdzunaScraper
from app.scrapers.orchestrator import JobScrapingOrchestrator
from app.database import get_db
from app.models import Job, Company
from app.accredited_sponsors import sponsor_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adzuna API credentials
ADZUNA_APP_ID = "81a172a4"
ADZUNA_APP_KEY = "b003298d4b1d24c1302d9aad5183ec6b"

def test_adzuna_scraping():
    """Test Adzuna API scraping with visa-friendly searches"""
    logger.info("Testing Adzuna API scraping...")
    
    # Initialize Adzuna scraper
    adzuna = AdzunaScraper(ADZUNA_APP_ID, ADZUNA_APP_KEY)
    
    # Test basic search
    logger.info("Testing basic job search...")
    jobs = adzuna.search_jobs(what="software developer", where="sydney", results_per_page=10)
    logger.info(f"Found {len(jobs)} software developer jobs in Sydney")
    
    # Test visa-friendly search
    logger.info("Testing visa-friendly job search...")
    visa_jobs = adzuna.search_visa_friendly_jobs(location="australia")
    logger.info(f"Found {len(visa_jobs)} visa-friendly jobs")
    
    # Display sample jobs
    for i, job in enumerate(visa_jobs[:3]):
        logger.info(f"Sample Job {i+1}:")
        logger.info(f"  Title: {job.get('title', 'N/A')}")
        logger.info(f"  Company: {job.get('company_name', 'N/A')}")
        logger.info(f"  Location: {job.get('location', 'N/A')}")
        logger.info(f"  URL: {job.get('source_url', 'N/A')}")
        logger.info(f"  Visa Friendly: {job.get('visa_sponsorship', False)}")
        logger.info(f"  Confidence: {job.get('visa_sponsorship_confidence', 0.0):.2f}")
        logger.info("---")
    
    return visa_jobs

def test_full_orchestrator():
    """Test the full orchestrator with Adzuna integration"""
    logger.info("Testing full scraping orchestrator...")
    
    # Initialize orchestrator with Adzuna credentials
    orchestrator = JobScrapingOrchestrator(
        adzuna_app_id=ADZUNA_APP_ID,
        adzuna_app_key=ADZUNA_APP_KEY
    )
    
    # Update target companies (empty for now since we don't have ATS access)
    orchestrator.update_target_companies('greenhouse', [])
    orchestrator.update_target_companies('lever', [])
    orchestrator.update_target_companies('workable', [])
    orchestrator.update_target_companies('smartrecruiters', [])
    
    # Run scraping (will only use Adzuna for now)
    results = orchestrator.scrape_all_sources(location="Australia")
    
    logger.info("Scraping Results:")
    logger.info(f"  Total jobs: {results['total_jobs']}")
    logger.info(f"  Visa-friendly jobs: {results['visa_friendly_jobs']}")
    logger.info(f"  Accredited sponsor jobs: {results['accredited_sponsor_jobs']}")
    logger.info(f"  Sources: {results['sources']}")
    
    return results

def verify_job_urls():
    """Verify that job URLs are properly captured in the database"""
    logger.info("Verifying job URLs in database...")
    
    db = next(get_db())
    try:
        jobs = db.query(Job).limit(10).all()
        
        logger.info(f"Checking {len(jobs)} jobs for URL capture:")
        
        urls_captured = 0
        for job in jobs:
            if job.source_url:
                urls_captured += 1
                logger.info(f"✓ Job '{job.title}' has URL: {job.source_url}")
            else:
                logger.warning(f"✗ Job '{job.title}' missing URL")
        
        logger.info(f"URL capture rate: {urls_captured}/{len(jobs)} ({urls_captured/len(jobs)*100:.1f}%)")
        
        return urls_captured == len(jobs)
        
    finally:
        db.close()

def check_database_stats():
    """Check database statistics after scraping"""
    logger.info("Checking database statistics...")
    
    db = next(get_db())
    try:
        total_jobs = db.query(Job).count()
        total_companies = db.query(Company).count()
        visa_friendly = db.query(Job).filter(Job.visa_sponsorship == True).count()
        student_friendly = db.query(Job).filter(Job.international_student_friendly == True).count()
        
        logger.info(f"Database Statistics:")
        logger.info(f"  Total jobs: {total_jobs}")
        logger.info(f"  Total companies: {total_companies}")
        logger.info(f"  Visa-friendly jobs: {visa_friendly}")
        logger.info(f"  Student-friendly jobs: {student_friendly}")
        
        # Show sample companies with sponsor status
        companies = db.query(Company).limit(5).all()
        logger.info("Sample companies:")
        for company in companies:
            logger.info(f"  {company.name} - Sponsor: {company.is_accredited_sponsor}")
        
    finally:
        db.close()

def main():
    """Run all tests"""
    logger.info("Starting ATS scraping system tests...")
    logger.info(f"Using Adzuna credentials: App ID {ADZUNA_APP_ID}")
    
    try:
        # Test 1: Basic Adzuna functionality
        visa_jobs = test_adzuna_scraping()
        
        # Test 2: Full orchestrator
        results = test_full_orchestrator()
        
        # Test 3: Verify URLs are captured
        urls_ok = verify_job_urls()
        
        # Test 4: Database statistics
        check_database_stats()
        
        logger.info("All tests completed successfully!")
        logger.info(f"✓ Adzuna API working: {len(visa_jobs)} jobs found")
        logger.info(f"✓ Orchestrator working: {results['total_jobs']} jobs processed")
        logger.info(f"✓ URLs captured: {'Yes' if urls_ok else 'No'}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    main()
