from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from app.database import get_db
from app.schemas import Job, JobFilter, JobSearchResponse, VisaKeyword, VisaKeywordCreate
from app.services import JobService, ScrapingService
from .auth import AuthService, get_current_user
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Provide a FastAPI instance for test clients that import `app` from this module
# This keeps backward-compatibility with tests expecting `from app.api import app`
app = FastAPI()

# Restrict surfaced jobs to these sources
ALLOWED_SOURCES = [
    'adzuna.com.au',
    'greenhouse.io',
    'test.com',  # allow tests data
]

@router.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Joborra API is running", "status": "healthy"}

# Job search endpoint
@router.get("/jobs/search", response_model=JobSearchResponse)
async def search_jobs(
    search: Optional[str] = Query(None, description="General search term for title/description"),
    title: Optional[str] = Query(None, description="Job title keyword"),
    location: Optional[str] = Query(None, description="Location (city, state, or general)"),
    state: Optional[str] = Query(None, description="Australian state"),
    city: Optional[str] = Query(None, description="City name"),
    # New filters
    visa_sponsorship: Optional[bool] = Query(None, description="Require visa sponsorship"),
    student_friendly: Optional[bool] = Query(None, description="International student friendly"),
    employment_type: Optional[str] = Query(None, description="Employment type e.g. Full-time, Part-time, Contract, Internship"),
    category: Optional[str] = Query(None, description="casual or career"),
    remote: Optional[bool] = Query(None, description="Remote friendly"),
    visa_types: Optional[str] = Query(None, description="Comma-separated visa type keywords to match"),
    industry: Optional[str] = Query(None, description="Company industry"),
    salary_min: Optional[float] = Query(None, description="Minimum salary filter"),
    salary_max: Optional[float] = Query(None, description="Maximum salary filter"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search jobs with various filters"""
    try:
        from app.models import Job as JobModel, Company as CompanyModel
        
        query_obj = db.query(JobModel).filter(
            JobModel.is_active == True,
            JobModel.source_website.in_(ALLOWED_SOURCES)
        )
        
        if search:
            query_obj = query_obj.filter(
                or_(
                    JobModel.title.contains(search),
                    JobModel.description.contains(search),
                    JobModel.required_skills.contains(search)
                )
            )
        
        if location:
            query_obj = query_obj.filter(
                or_(
                    JobModel.location.contains(location),
                    JobModel.city.contains(location),
                    JobModel.state.contains(location)
                )
            )

        # Additional filters
        if title:
            query_obj = query_obj.filter(JobModel.title.contains(title))

        if state:
            query_obj = query_obj.filter(JobModel.state.ilike(f"%{state}%"))

        if city:
            query_obj = query_obj.filter(JobModel.city.ilike(f"%{city}%"))

        if visa_sponsorship is not None:
            query_obj = query_obj.filter(JobModel.visa_sponsorship == bool(visa_sponsorship))

        if student_friendly is not None:
            query_obj = query_obj.filter(JobModel.international_student_friendly == bool(student_friendly))

        if employment_type:
            query_obj = query_obj.filter(JobModel.employment_type.ilike(f"%{employment_type}%"))

        if remote is not None:
            query_obj = query_obj.filter(JobModel.remote_option == bool(remote))

        if visa_types:
            # Match if any of the provided visa type tokens appear in visa_type field
            tokens = [t.strip() for t in visa_types.split(',') if t.strip()]
            if tokens:
                like_clauses = [JobModel.visa_type.ilike(f"%{t}%") for t in tokens]
                query_obj = query_obj.filter(or_(*like_clauses))

        if industry:
            # join company for industry filter
            query_obj = query_obj.join(CompanyModel, CompanyModel.id == JobModel.company_id)
            query_obj = query_obj.filter(CompanyModel.industry.ilike(f"%{industry}%"))

        # Salary overlap: job range intersects with filter range
        if salary_min is not None:
            query_obj = query_obj.filter(
                or_(
                    JobModel.salary_min.is_(None),
                    JobModel.salary_max.is_(None),
                    JobModel.salary_max >= float(salary_min)
                )
            )
        if salary_max is not None:
            query_obj = query_obj.filter(
                or_(
                    JobModel.salary_min.is_(None),
                    JobModel.salary_max.is_(None),
                    JobModel.salary_min <= float(salary_max)
                )
            )

        if category:
            cat = category.strip().lower()
            if cat == 'casual':
                query_obj = query_obj.filter(
                    or_(
                        JobModel.employment_type.ilike('%part%'),
                        JobModel.title.ilike('%casual%'),
                        JobModel.description.ilike('%casual%')
                    )
                )
            elif cat == 'career':
                # heuristic: prefer full-time or permanent, exclude explicit casual
                query_obj = query_obj.filter(
                    or_(
                        JobModel.employment_type.ilike('%full%'),
                        JobModel.employment_type.ilike('%permanent%')
                    )
                ).filter(
                    ~or_(
                        JobModel.title.ilike('%casual%'),
                        JobModel.description.ilike('%casual%')
                    )
                )
        
        # Get total count
        total = query_obj.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        jobs = query_obj.offset(offset).limit(per_page).all()
        
        return {
            "jobs": jobs,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
        
    except Exception as e:
        logger.error(f"Error searching jobs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Job statistics endpoint - MUST come before /jobs/{job_id}
@router.get("/jobs/stats")
async def get_job_statistics(db: Session = Depends(get_db)):
    """Get comprehensive job statistics for dashboard"""
    try:
        from app.models import Job as JobModel
        
        # Total jobs
        total_jobs = db.query(JobModel).filter(
            JobModel.is_active == True,
            JobModel.source_website.in_(ALLOWED_SOURCES)
        ).count()
        
        # Visa-friendly jobs
        visa_friendly_jobs = db.query(JobModel).filter(
            JobModel.is_active == True,
            JobModel.visa_sponsorship == True,
            JobModel.source_website.in_(ALLOWED_SOURCES)
        ).count()
        
        # Student-friendly jobs
        student_friendly_jobs = db.query(JobModel).filter(
            JobModel.is_active == True,
            JobModel.international_student_friendly == True,
            JobModel.source_website.in_(ALLOWED_SOURCES)
        ).count()
        
        # Jobs by state
        jobs_by_state = dict(
            db.query(JobModel.state, func.count(JobModel.id))
            .filter(
                JobModel.is_active == True,
                JobModel.source_website.in_(ALLOWED_SOURCES)
            )
            .group_by(JobModel.state)
            .all()
        )
        
        # Jobs by employment type
        jobs_by_employment_type = dict(
            db.query(JobModel.employment_type, func.count(JobModel.id))
            .filter(
                JobModel.is_active == True,
                JobModel.source_website.in_(ALLOWED_SOURCES)
            )
            .group_by(JobModel.employment_type)
            .all()
        )
        
        # Jobs by experience level
        jobs_by_experience = dict(
            db.query(JobModel.experience_level, func.count(JobModel.id))
            .filter(
                JobModel.is_active == True,
                JobModel.source_website.in_(ALLOWED_SOURCES)
            )
            .group_by(JobModel.experience_level)
            .all()
        )
        
        # Average visa confidence
        avg_visa_confidence = db.query(func.avg(JobModel.visa_sponsorship_confidence)).filter(
            JobModel.is_active == True,
            JobModel.visa_sponsorship_confidence.isnot(None),
            JobModel.source_website.in_(ALLOWED_SOURCES)
        ).scalar() or 0.0
        
        return {
            "total_jobs": total_jobs,
            "visa_friendly_jobs": visa_friendly_jobs,
            "student_friendly_jobs": student_friendly_jobs,
            "jobs_by_state": jobs_by_state,
            "jobs_by_employment_type": jobs_by_employment_type,
            "jobs_by_experience": jobs_by_experience,
            "avg_visa_confidence": round(float(avg_visa_confidence), 2)
        }
        
    except Exception as e:
        logger.error(f"Error getting job statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Visa-friendly jobs endpoint
@router.get("/jobs/visa-friendly")
async def get_visa_friendly_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    min_confidence: float = Query(0.5, ge=0.0, le=1.0, description="Minimum confidence score"),
    db: Session = Depends(get_db)
):
    """Get jobs that are visa-friendly"""
    try:
        job_service = JobService(db)
        
        filters = JobFilter(visa_sponsorship=True)
        result = job_service.search_jobs(filters, page, per_page)
        
        # Filter by confidence if specified
        if min_confidence > 0:
            filtered_jobs = [
                job for job in result.jobs 
                if job.visa_sponsorship_confidence and job.visa_sponsorship_confidence >= min_confidence
            ]
            result.jobs = filtered_jobs
            result.total = len(filtered_jobs)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting visa friendly jobs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Student-friendly jobs endpoint
@router.get("/jobs/student-friendly")
async def get_student_friendly_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get jobs that are friendly to international students"""
    try:
        job_service = JobService(db)
        
        filters = JobFilter(international_student_friendly=True)
        return job_service.search_jobs(filters, page, per_page)
        
    except Exception as e:
        logger.error(f"Error getting student-friendly jobs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Recommended jobs endpoint
@router.get("/jobs/recommended")
def get_recommended_jobs(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get personalized job recommendations based on user profile"""
    from app.auth_models import User
    
    # Get user profile
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user or user.role.value != "student":
        return []
    
    # Build recommendation query
    from app.models import Job as JobModel
    query_obj = db.query(JobModel).filter(
        JobModel.is_active == True,
        JobModel.source_website.in_(ALLOWED_SOURCES)
    )
    
    # Score jobs based on profile matching
    jobs = query_obj.all()
    scored_jobs = []
    
    for job in jobs:
        score = calculate_job_match_score(user, job)
        if score > 0:
            scored_jobs.append((job, score))
    
    # Sort by score and return top matches
    scored_jobs.sort(key=lambda x: x[1], reverse=True)
    return [job for job, score in scored_jobs[:limit]]

def calculate_job_match_score(user, job):
    """Calculate how well a job matches a user's profile"""
    score = 0
    
    # Base score for all jobs
    score += 10
    
    # Visa sponsorship match
    if user.visa_status in ['student_visa', 'work_visa'] and job.visa_sponsorship:
        score += 30
    
    # International student friendly
    if user.visa_status == 'student_visa' and job.international_student_friendly:
        score += 25
    
    # Skills matching
    if user.skills and job.required_skills:
        user_skills = [s.strip().lower() for s in user.skills.split(',') if s.strip()]
        job_skills = [s.strip().lower() for s in job.required_skills.split(',') if s.strip()]
        
        matching_skills = set(user_skills) & set(job_skills)
        if matching_skills:
            score += len(matching_skills) * 5
    
    # Work authorization match
    if user.work_authorization:
        if user.work_authorization in ['citizen', 'pr'] and not job.visa_sponsorship:
            score += 10  # Bonus for not needing sponsorship
        elif user.work_authorization == 'requires_sponsorship' and job.visa_sponsorship:
            score += 25  # High bonus for sponsorship availability
    
    return score

# Location suggestions endpoint
@router.get("/locations/suggest")
async def suggest_locations(
    q: str = Query(..., min_length=1, description="Search text for location autocomplete"),
    limit: int = Query(8, ge=1, le=25),
    db: Session = Depends(get_db)
):
    """Return a list of distinct location suggestions matching the query.
    Combines `location`, `city`, and `state` fields from jobs and returns unique values.
    """
    try:
        from app.models import Job as JobModel
        # Build case-insensitive match
        pattern = f"%{q}%"

        # Select distinct values from multiple columns
        locs = (
            db.query(JobModel.location.label("val"))
            .filter(JobModel.location.isnot(None), JobModel.location.ilike(pattern))
        ).union(
            db.query(JobModel.city.label("val"))
            .filter(JobModel.city.isnot(None), JobModel.city.ilike(pattern))
        ).union(
            db.query(JobModel.state.label("val"))
            .filter(JobModel.state.isnot(None), JobModel.state.ilike(pattern))
        ).limit(limit * 3).all()

        # Deduplicate while preserving order, prefer longer strings (more specific)
        seen = set()
        results = []
        for row in sorted((l.val for l in locs if l and l.val), key=lambda s: (-len(s), s)):
            key = row.strip()
            if key and key.lower() not in seen:
                seen.add(key.lower())
                results.append(key)
            if len(results) >= limit:
                break
        return {"items": results}
    except Exception as e:
        logger.error(f"Error suggesting locations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Scraping endpoints
@router.post("/jobs/scrape")
async def start_scraping(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Start background job scraping"""
    try:
        scraping_service = ScrapingService(db)
        
        # Start scraping in background
        background_tasks.add_task(scraping_service.scrape_all_sources)
        
        return {"message": "Scraping started successfully", "status": "started"}
    except Exception as e:
        logger.error(f"Error starting scraping: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/jobs/scraping-status")
async def get_scraping_status(db: Session = Depends(get_db)):
    """Get current scraping status"""
    try:
        from app.models import ScrapingLog
        
        # Get latest scraping logs
        latest_logs = db.query(ScrapingLog).order_by(
            ScrapingLog.created_at.desc()
        ).limit(10).all()
        
        # Get overall status
        active_scraping = db.query(ScrapingLog).filter(
            ScrapingLog.status == "running"
        ).count()
        
        return {
            "active_scraping": active_scraping > 0,
            "recent_logs": [
                {
                    "source": log.source,
                    "status": log.status,
                    "jobs_found": log.jobs_found,
                    "created_at": log.created_at.isoformat(),
                    "message": log.message
                }
                for log in latest_logs
            ]
        }
    except Exception as e:
        logger.error(f"Error getting scraping status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Visa keywords endpoints
@router.get("/visa-keywords", response_model=List[VisaKeyword])
async def get_visa_keywords(db: Session = Depends(get_db)):
    """Get all visa keywords"""
    from app.models import VisaKeyword as VisaKeywordModel
    keywords = db.query(VisaKeywordModel).all()
    return keywords

@router.post("/visa-keywords", response_model=VisaKeyword)
async def create_visa_keyword(
    keyword_data: VisaKeywordCreate,
    db: Session = Depends(get_db)
):
    """Create a new visa keyword"""
    try:
        from app.models import VisaKeyword as VisaKeywordModel
        
        # Create new keyword
        keyword = VisaKeywordModel(
            keyword=keyword_data.keyword,
            keyword_type=keyword_data.keyword_type,
            weight=keyword_data.weight,
            category=keyword_data.category
        )
        
        db.add(keyword)
        db.commit()
        db.refresh(keyword)
        
        return keyword
        
    except Exception as e:
        logger.error(f"Error creating visa keyword: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Cleanup endpoint
@router.delete("/jobs/cleanup")
async def cleanup_old_jobs(
    days: int = Query(30, description="Delete jobs older than this many days"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Clean up old inactive jobs"""
    try:
        from app.models import Job as JobModel
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Delete old jobs
        deleted_count = db.query(JobModel).filter(
            JobModel.created_at < cutoff_date,
            JobModel.is_active == False
        ).delete()
        
        db.commit()
        
        return {
            "message": f"Cleaned up {deleted_count} old jobs",
            "deleted_count": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
    except Exception as e:
        logger.error(f"Error cleaning up jobs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Individual job endpoint - MUST BE LAST to avoid conflicts
@router.get("/jobs/{job_id}")
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get job by ID - MUST BE LAST ROUTE"""
    try:
        from app.models import Job as JobModel
        job = db.query(JobModel).filter(JobModel.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job
    except HTTPException as e:
        # Propagate known HTTP errors (e.g., 404)
        raise e
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Include routes AFTER all have been defined so they register correctly
app.include_router(router)
