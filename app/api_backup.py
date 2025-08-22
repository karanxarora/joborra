from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
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

@router.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Joborra API is running", "status": "healthy"}

@router.get("/jobs/search", response_model=JobSearchResponse)
async def search_jobs(
    search: Optional[str] = Query(None, description="General search term for title/description"),
    title: Optional[str] = Query(None, description="Job title keyword"),
    location: Optional[str] = Query(None, description="Location (city, state, or general)"),
    state: Optional[str] = Query(None, description="Australian state"),
    city: Optional[str] = Query(None, description="City name"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search jobs with various filters"""
    try:
        from app.models import Job as JobModel
        from sqlalchemy import or_
        
        query_obj = db.query(JobModel).filter(JobModel.is_active == True)
        
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
    
    if employment_type:
        query_obj = query_obj.filter(Job.employment_type == employment_type)
    
    if visa_sponsorship is not None:
        query_obj = query_obj.filter(Job.visa_sponsorship == visa_sponsorship)
    
    if international_student_friendly is not None:
        query_obj = query_obj.filter(Job.international_student_friendly == international_student_friendly)
    
    if salary_min is not None:
        query_obj = query_obj.filter(Job.salary_min >= salary_min)
    
    if salary_max is not None:
        query_obj = query_obj.filter(Job.salary_max <= salary_max)
    
    if experience_level:
        query_obj = query_obj.filter(Job.experience_level == experience_level)
    
    if remote_option is not None:
        query_obj = query_obj.filter(Job.remote_option == remote_option)
    
    if source_website:
        query_obj = query_obj.filter(Job.source_website == source_website)
    
    jobs = query_obj.offset(offset).limit(limit).all()
    return jobs

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
    query_obj = db.query(Job).filter(Job.is_active == True)
    
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
            score += len(matching_skills) * 15
    
    # Experience level match
    if user.experience_level and job.experience_level:
        if user.experience_level == job.experience_level:
            score += 20
        elif (user.experience_level == 'entry' and job.experience_level in ['entry', 'junior']) or \
             (user.experience_level == 'junior' and job.experience_level in ['entry', 'junior', 'mid']):
            score += 10
    
    # Location preference match
    if user.preferred_locations and job.city:
        preferred_cities = [l.strip().lower() for l in user.preferred_locations.split(',') if l.strip()]
        if job.city.lower() in preferred_cities or 'remote' in preferred_cities and job.remote_option:
            score += 20
    
    # Salary expectations match
    if user.salary_expectations_min and job.salary_min:
        if job.salary_min >= user.salary_expectations_min:
            score += 15
        elif job.salary_max and job.salary_max >= user.salary_expectations_min:
            score += 10
    
    # Work authorization match
    if user.work_authorization:
        if user.work_authorization in ['citizen', 'pr'] and not job.visa_sponsorship:
            score += 10  # Bonus for not needing sponsorship
        elif user.work_authorization == 'requires_sponsorship' and job.visa_sponsorship:
            score += 25  # High bonus for sponsorship availability
    
    return score

@router.post("/jobs/scrape")
async def start_scraping(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Start background job scraping"""
    try:
        # Check if user has admin privileges (optional)
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

@router.get("/jobs/{job_id}", response_model=Job)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get job by ID"""
    from app.models import Job as JobModel
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

@router.get("/visa-keywords", response_model=List[VisaKeyword])
async def get_visa_keywords(db: Session = Depends(get_db)):
    """Get all visa keywords"""
    from app.models import VisaKeyword as VisaKeywordModel
    keywords = db.query(VisaKeywordModel).all()
    return keywords

@router.post("/visa-keywords", response_model=VisaKeyword)
async def create_visa_keyword(
    keyword_data: VisaKeywordCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new visa keyword"""
    try:
        from app.models import VisaKeyword as VisaKeywordModel
        
        # Create new keyword
        keyword = VisaKeywordModel(
            keyword=keyword_data.keyword,
            category=keyword_data.category,
            weight=keyword_data.weight,
            is_positive=keyword_data.is_positive
        )
        
        db.add(keyword)
        db.commit()
        db.refresh(keyword)
        
        return keyword
    except Exception as e:
        logger.error(f"Error creating visa keyword: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/jobs/visa-friendly")
async def get_visa_friendly_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    min_confidence: float = Query(0.5, ge=0.0, le=1.0, description="Minimum confidence score"),
    db: Session = Depends(get_db)
):
    """Get jobs that are likely to offer visa sponsorship"""
    try:
        job_service = JobService(db)
        
        filters = JobFilter(visa_sponsorship=True)
        result = job_service.search_jobs(filters, page, per_page)
        
        # Filter by confidence if specified
        if min_confidence > 0:
            filtered_jobs = [
                job for job in result.jobs 
                if job.visa_sponsorship_confidence >= min_confidence
            ]
            result.jobs = filtered_jobs
            result.total = len(filtered_jobs)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting visa friendly jobs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

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

@router.get("/jobs/stats")
async def get_job_statistics(db: Session = Depends(get_db)):
    """Get comprehensive job statistics for dashboard"""
    try:
        from sqlalchemy import func
        
        from app.models import Job as JobModel
        
        # Total jobs
        total_jobs = db.query(JobModel).filter(JobModel.is_active == True).count()
        
        # Visa-friendly jobs
        visa_friendly_jobs = db.query(JobModel).filter(
            JobModel.is_active == True,
            JobModel.visa_sponsorship == True
        ).count()
        
        # Student-friendly jobs
        student_friendly_jobs = db.query(JobModel).filter(
            JobModel.is_active == True,
            JobModel.international_student_friendly == True
        ).count()
        
        # Jobs by state
        jobs_by_state = dict(
            db.query(JobModel.state, func.count(JobModel.id))
            .filter(JobModel.is_active == True)
            .group_by(JobModel.state)
            .all()
        )
        
        # Jobs by employment type
        jobs_by_employment_type = dict(
            db.query(JobModel.employment_type, func.count(JobModel.id))
            .filter(JobModel.is_active == True)
            .group_by(JobModel.employment_type)
            .all()
        )
        
        # Jobs by experience level
        jobs_by_experience = dict(
            db.query(JobModel.experience_level, func.count(JobModel.id))
            .filter(JobModel.is_active == True)
            .group_by(JobModel.experience_level)
            .all()
        )
        
        # Average visa confidence
        avg_visa_confidence = db.query(func.avg(JobModel.visa_sponsorship_confidence)).filter(
            JobModel.is_active == True,
            JobModel.visa_sponsorship_confidence.isnot(None)
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

@router.get("/jobs/{job_id}", response_model=Job)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get job by ID"""
    from app.models import Job as JobModel
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

# Note: Authentication routes are included in main.py
