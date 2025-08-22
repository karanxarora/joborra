"""
Comprehensive scraping orchestrator for legitimate ATS APIs and job sources
"""

import logging
import asyncio
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database import get_db
from app.models import Job, Company, ScrapingLog
from app.visa_keywords import analyze_job_visa_friendliness
from app.accredited_sponsors import check_company_sponsor_status

from .ats_scraper import GreenhouseScraper, LeverScraper, WorkableScraper, SmartRecruitersScaper
from .adzuna_scraper import AdzunaScraper

logger = logging.getLogger(__name__)

class JobScrapingOrchestrator:
    """Orchestrate job scraping from multiple legitimate sources"""
    
    def __init__(self, 
                 adzuna_app_id: str = None,
                 adzuna_app_key: str = None,
                 workable_token: str = None):
        
        # Initialize scrapers
        self.greenhouse_scraper = GreenhouseScraper()
        self.lever_scraper = LeverScraper()
        self.workable_scraper = WorkableScraper(workable_token)
        self.smartrecruiters_scraper = SmartRecruitersScaper()
        
        if adzuna_app_id and adzuna_app_key:
            self.adzuna_scraper = AdzunaScraper(adzuna_app_id, adzuna_app_key)
        else:
            self.adzuna_scraper = None
            logger.warning("Adzuna API credentials not provided")
        
        # Target companies for each ATS (verified working company tokens)
        self.target_companies = {
            'greenhouse': [
                # Verified working Greenhouse board tokens
                'greenhouse', 'vaulttec', 'shopify', 'stripe', 'airbnb'
            ],
            'lever': [
                # Verified working Lever company names
                'netflix', 'uber', 'spotify', 'github', 'lever'
            ],
            'workable': [
                # Workable company subdomains (will test separately)
                'workable', 'example-company'
            ],
            'smartrecruiters': [
                # SmartRecruiters company IDs (will test separately)
                'smartrecruiters', 'company123'
            ]
        }
    
    def scrape_all_sources(self, location: str = "Australia") -> Dict[str, int]:
        """Scrape jobs from all configured sources"""
        results = {
            'total_jobs': 0,
            'visa_friendly_jobs': 0,
            'accredited_sponsor_jobs': 0,
            'sources': {}
        }
        
        db = next(get_db())
        
        try:
            # Scrape from each ATS
            for ats_type, companies in self.target_companies.items():
                if not companies:
                    continue
                
                logger.info(f"Starting {ats_type} scraping for {len(companies)} companies")
                
                jobs = self._scrape_ats_source(ats_type, companies, location)
                processed_count = self._process_and_save_jobs(db, jobs, ats_type)
                
                results['sources'][ats_type] = processed_count
                results['total_jobs'] += processed_count
                
                logger.info(f"Completed {ats_type}: {processed_count} jobs processed")
            
            # Scrape from Adzuna if available
            if self.adzuna_scraper:
                logger.info("Starting Adzuna visa-friendly job search")
                adzuna_jobs = self.adzuna_scraper.search_visa_friendly_jobs(location)
                processed_count = self._process_and_save_jobs(db, adzuna_jobs, 'adzuna')
                
                results['sources']['adzuna'] = processed_count
                results['total_jobs'] += processed_count
                
                logger.info(f"Completed Adzuna: {processed_count} jobs processed")
            
            # Update statistics
            visa_friendly_count = db.query(Job).filter(Job.visa_sponsorship == True).count()
            sponsor_jobs_count = db.query(Job).join(Company).filter(
                Company.is_accredited_sponsor == True
            ).count()
            
            results['visa_friendly_jobs'] = visa_friendly_count
            results['accredited_sponsor_jobs'] = sponsor_jobs_count
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error in scraping orchestration: {e}")
            db.rollback()
        finally:
            db.close()
        
        return results
    
    def _scrape_ats_source(self, ats_type: str, companies: List[str], location: str) -> List[Dict]:
        """Scrape jobs from a specific ATS source"""
        try:
            if ats_type == 'greenhouse':
                return self.greenhouse_scraper.scrape_jobs(companies, location)
            elif ats_type == 'lever':
                return self.lever_scraper.scrape_jobs(companies, location)
            elif ats_type == 'workable':
                return self.workable_scraper.scrape_jobs(companies, location)
            elif ats_type == 'smartrecruiters':
                return self.smartrecruiters_scraper.scrape_jobs(companies, location)
            else:
                logger.warning(f"Unknown ATS type: {ats_type}")
                return []
        except Exception as e:
            logger.error(f"Error scraping {ats_type}: {e}")
            return []
    
    def _process_and_save_jobs(self, db: Session, jobs: List[Dict], source_type: str) -> int:
        """Process and save jobs to database with enhanced analysis"""
        processed_count = 0
        
        for job_data in jobs:
            try:
                # Check for duplicates
                existing_job = db.query(Job).filter(
                    or_(
                        Job.source_url == job_data.get('source_url'),
                        and_(
                            Job.title == job_data.get('title'),
                            Job.company_id == self._get_or_create_company(db, job_data, source_type).id
                        )
                    )
                ).first()
                
                if existing_job:
                    continue
                
                # Get or create company
                company = self._get_or_create_company(db, job_data, source_type)
                
                # Enhanced visa analysis
                visa_analysis = analyze_job_visa_friendliness(
                    job_data.get('title', ''),
                    job_data.get('description', '')
                )
                
                # Create job record
                job = Job(
                    title=job_data.get('title', ''),
                    description=job_data.get('description', ''),
                    company_id=company.id,
                    location=job_data.get('location', ''),
                    city=job_data.get('city'),
                    state=job_data.get('state'),
                    salary_min=job_data.get('salary_min'),
                    salary_max=job_data.get('salary_max'),
                    salary_currency=job_data.get('salary_currency', 'AUD'),
                    employment_type=job_data.get('employment_type'),
                    source_website=job_data.get('source_website', ''),
                    source_url=job_data.get('source_url', ''),
                    source_job_id=job_data.get('source_job_id', ''),
                    posted_date=job_data.get('posted_date'),
                    visa_sponsorship=visa_analysis['is_visa_friendly'],
                    visa_sponsorship_confidence=visa_analysis['confidence_score'],
                    international_student_friendly=visa_analysis['is_student_friendly'],
                    is_active=True
                )
                
                db.add(job)
                processed_count += 1
                
                if processed_count % 50 == 0:
                    db.commit()
                    logger.info(f"Processed {processed_count} jobs from {source_type}")
                
            except Exception as e:
                logger.error(f"Error processing job from {source_type}: {e}")
                continue
        
        db.commit()
        return processed_count
    
    def _get_or_create_company(self, db: Session, job_data: Dict, source_type: str) -> Company:
        """Get existing company or create new one with sponsor analysis"""
        company_name = job_data.get('company_name', '')
        
        # Try to find existing company
        company = db.query(Company).filter(Company.name.ilike(f"%{company_name}%")).first()
        
        if not company:
            # Check sponsor status
            sponsor_status = check_company_sponsor_status(company_name)
            
            # Create new company
            company = Company(
                name=company_name,
                website=job_data.get('company_website', ''),
                location=job_data.get('location', ''),
                is_accredited_sponsor=sponsor_status['is_accredited_sponsor'],
                sponsor_confidence=sponsor_status['confidence'],
                ats_type=source_type,
                ats_company_id=job_data.get('company_id', company_name)
            )
            
            # Add sponsor details if available
            if sponsor_status['sponsor_info']:
                info = sponsor_status['sponsor_info']
                company.sponsor_abn = info.get('abn')
                if info.get('approval_date'):
                    try:
                        company.sponsor_approval_date = datetime.fromisoformat(info['approval_date'])
                    except:
                        pass
            
            db.add(company)
            db.commit()
            
            logger.info(f"Created company: {company_name} (Sponsor: {sponsor_status['is_accredited_sponsor']})")
        
        # Update ATS information
        if not company.ats_type or company.ats_type != source_type:
            company.ats_type = source_type
            company.ats_last_scraped = datetime.utcnow()
        
        return company
    
    def update_target_companies(self, ats_type: str, companies: List[str]):
        """Update target companies for a specific ATS"""
        if ats_type in self.target_companies:
            self.target_companies[ats_type] = companies
            logger.info(f"Updated {ats_type} target companies: {len(companies)} companies")
    
    def discover_ats_companies(self, company_websites: List[str]) -> Dict[str, List[str]]:
        """Discover which ATS each company uses by checking their career pages"""
        discovered = {
            'greenhouse': [],
            'lever': [],
            'workable': [],
            'smartrecruiters': []
        }
        
        # This would implement ATS detection logic
        # For now, returning empty - would need to implement career page analysis
        
        return discovered
    
    def get_scraping_stats(self, days: int = 7) -> Dict:
        """Get scraping statistics for the last N days"""
        db = next(get_db())
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            stats = {
                'total_jobs': db.query(Job).filter(Job.scraped_at >= cutoff_date).count(),
                'visa_friendly': db.query(Job).filter(
                    and_(Job.visa_sponsorship == True, Job.scraped_at >= cutoff_date)
                ).count(),
                'student_friendly': db.query(Job).filter(
                    and_(Job.international_student_friendly == True, Job.scraped_at >= cutoff_date)
                ).count(),
                'sponsor_companies': db.query(Company).filter(
                    Company.is_accredited_sponsor == True
                ).count(),
                'by_source': {}
            }
            
            # Stats by source
            sources = db.query(Job.source_website).filter(
                Job.scraped_at >= cutoff_date
            ).distinct().all()
            
            for (source,) in sources:
                count = db.query(Job).filter(
                    and_(Job.source_website == source, Job.scraped_at >= cutoff_date)
                ).count()
                stats['by_source'][source] = count
            
            return stats
            
        finally:
            db.close()


def run_full_scraping_cycle(location: str = "Australia", 
                           adzuna_app_id: str = None, 
                           adzuna_app_key: str = None) -> Dict:
    """Run a complete scraping cycle across all sources"""
    logger.info("Starting full scraping cycle")
    orchestrator = JobScrapingOrchestrator(adzuna_app_id, adzuna_app_key)
    results = orchestrator.scrape_all_sources(location)
    logger.info(f"Scraping cycle completed: {results}")
    return results
