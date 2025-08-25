from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models import Job, Company, VisaKeyword, ScrapingLog
from app.schemas import JobCreate, CompanyCreate, JobFilter, JobSearchResponse
from app.visa_keywords import analyze_job_visa_friendliness
from app.scrapers.orchestrator import JobScrapingOrchestrator
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Restrict surfaced jobs to these sources
ALLOWED_SOURCES = [
    'adzuna.com.au',
    'greenhouse.io',
    'test.com',  # allow tests data
]

class JobService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_or_get_company(self, company_name: str, **kwargs) -> Company:
        """Create or get existing company"""
        company = self.db.query(Company).filter(Company.name == company_name).first()
        
        if not company:
            company_data = CompanyCreate(name=company_name, **kwargs)
            company = Company(**company_data.dict())
            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)
            
        return company
    
    def process_scraped_job(self, job_data: Dict) -> Optional[Job]:
        """Process and save a scraped job with visa analysis and enhanced duplicate detection"""
        try:
            # Enhanced duplicate detection - check by source URL and title+company combination
            source_url = job_data.get('source_url')
            title = job_data.get('title', '')
            company_name = job_data.get('company_name', '')
            
            # Primary check: source URL
            if source_url:
                existing_job = self.db.query(Job).filter(
                    Job.source_url == source_url
                ).first()
                
                if existing_job:
                    logger.debug(f"Duplicate job found by URL, skipping: {title} at {source_url}")
                    return existing_job
            
            # Secondary check: title + company combination (for cases where URL might be different)
            if title and company_name:
                existing_job = self.db.query(Job).join(Company).filter(
                    Job.title.ilike(f"%{title}%"),
                    Company.name.ilike(f"%{company_name}%"),
                    Job.is_active == True
                ).first()
                
                if existing_job:
                    logger.debug(f"Duplicate job found by title+company, skipping: {title} at {company_name}")
                    return existing_job
            
            # Create or get company
            company = self.create_or_get_company(job_data['company_name'])
            
            # Analyze visa friendliness using new system
            analysis = analyze_job_visa_friendliness(
                job_data.get('title', ''),
                job_data.get('description', '')
            )
            visa_sponsorship = analysis['is_visa_friendly']
            confidence = analysis['confidence_score']
            student_friendly = analysis['is_student_friendly']
            
            # Extract skills from description (basic implementation)
            required_skills = []
            preferred_skills = []
            
            # Create job
            job_create_data = {
                **job_data,
                'company_id': company.id,
                'visa_sponsorship': visa_sponsorship,
                'visa_sponsorship_confidence': confidence,
                'international_student_friendly': student_friendly,
                'required_skills': required_skills,
                'preferred_skills': preferred_skills
            }
            
            # Remove company_name as it's not in the Job model
            job_create_data.pop('company_name', None)
            
            job = Job(**job_create_data)
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)
            
            logger.info(f"Saved job: {job.title} at {company.name}")
            return job
            
        except Exception as e:
            logger.error(f"Error processing job: {e}")
            self.db.rollback()
            return None
    
    def search_jobs(self, filters: JobFilter, page: int = 1, per_page: int = 20) -> JobSearchResponse:
        """Search jobs with filters"""
        query = self.db.query(Job).filter(
            Job.is_active == True,
            Job.source_website.in_(ALLOWED_SOURCES)
        )
        
        # Apply filters
        if filters.title:
            query = query.filter(Job.title.ilike(f"%{filters.title}%"))
            
        if filters.location:
            query = query.filter(
                or_(
                    Job.location.ilike(f"%{filters.location}%"),
                    Job.city.ilike(f"%{filters.location}%"),
                    Job.state.ilike(f"%{filters.location}%")
                )
            )
            
        if filters.state:
            query = query.filter(Job.state.ilike(f"%{filters.state}%"))
            
        if filters.city:
            query = query.filter(Job.city.ilike(f"%{filters.city}%"))
            
        if filters.employment_type:
            query = query.filter(Job.employment_type == filters.employment_type)
            
        if filters.experience_level:
            query = query.filter(Job.experience_level == filters.experience_level)
            
        if filters.visa_sponsorship is not None:
            query = query.filter(Job.visa_sponsorship == filters.visa_sponsorship)
            
        if filters.international_student_friendly is not None:
            query = query.filter(Job.international_student_friendly == filters.international_student_friendly)
            
        if filters.remote_option is not None:
            query = query.filter(Job.remote_option == filters.remote_option)
            
        if filters.salary_min:
            query = query.filter(Job.salary_min >= filters.salary_min)
            
        if filters.salary_max:
            query = query.filter(Job.salary_max <= filters.salary_max)
            
        if filters.company_name:
            query = query.join(Company).filter(Company.name.ilike(f"%{filters.company_name}%"))
            
        if filters.source_website:
            query = query.filter(Job.source_website.ilike(f"%{filters.source_website}%"))
            
        if filters.posted_after:
            query = query.filter(Job.posted_date >= filters.posted_after)
            
        if filters.skills:
            for skill in filters.skills:
                query = query.filter(
                    or_(
                        Job.required_skills.contains([skill]),
                        Job.preferred_skills.contains([skill])
                    )
                )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        jobs = query.offset(offset).limit(per_page).all()
        
        total_pages = (total + per_page - 1) // per_page
        
        return JobSearchResponse(
            jobs=jobs,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    
    def get_job_stats(self) -> Dict:
        """Get job statistics"""
        total_jobs = self.db.query(Job).filter(
            Job.is_active == True,
            Job.source_website.in_(ALLOWED_SOURCES)
        ).count()
        visa_friendly = self.db.query(Job).filter(
            and_(Job.is_active == True, Job.visa_sponsorship == True, Job.source_website.in_(ALLOWED_SOURCES))
        ).count()
        student_friendly = self.db.query(Job).filter(
            and_(Job.is_active == True, Job.international_student_friendly == True, Job.source_website.in_(ALLOWED_SOURCES))
        ).count()
        
        # Jobs by state
        state_stats = self.db.query(
            Job.state, func.count(Job.id)
        ).filter(
            Job.is_active == True,
            Job.source_website.in_(ALLOWED_SOURCES)
        ).group_by(Job.state).all()
        
        # Jobs by source
        source_stats = self.db.query(
            Job.source_website, func.count(Job.id)
        ).filter(
            Job.is_active == True,
            Job.source_website.in_(ALLOWED_SOURCES)
        ).group_by(Job.source_website).all()
        
        return {
            'total_jobs': total_jobs,
            'visa_friendly_jobs': visa_friendly,
            'student_friendly_jobs': student_friendly,
            'visa_friendly_percentage': (visa_friendly / total_jobs * 100) if total_jobs > 0 else 0,
            'student_friendly_percentage': (student_friendly / total_jobs * 100) if total_jobs > 0 else 0,
            'jobs_by_state': dict(state_stats),
            'jobs_by_source': dict(source_stats)
        }

class ScrapingService:
    def __init__(self, db: Session):
        self.db = db
        self.job_service = JobService(db)
        # No third-party scrapers like Seek/Indeed are used in the app
        self.orchestrator = JobScrapingOrchestrator()
    
    def scrape_all_sources(self, search_terms: List[str], location: str = "Australia") -> Dict:
        try:
            # Use orchestrator for comprehensive multi-source scraping
            results = self.orchestrator.scrape_all_sources(location)
            
            # Log scraping activity for each source
            for source, count in results.get('sources', {}).items():
                self._log_scraping_activity(
                    source=source,
                    jobs_found=count,
                    success=True
                )
            
            logger.info(f"Multi-source scraping completed: {results['total_jobs']} total jobs from {len(results['sources'])} sources")
            return results
            
        except Exception as e:
            logger.error(f"Error in multi-source scraping service: {e}")
            self._log_scraping_activity(
                source="orchestrator",
                jobs_found=0,
                success=False,
                error_message=str(e)
            )
            raise
    
    def cleanup_old_jobs(self, days: int = 30):
        """Remove jobs older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted_count = self.db.query(Job).filter(
            Job.scraped_at < cutoff_date
        ).delete()
        
        self.db.commit()
        logger.info(f"Cleaned up {deleted_count} old jobs")
        
        return deleted_count
