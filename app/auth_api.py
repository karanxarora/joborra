"""
Authentication API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional

from .database import get_db
from .auth import AuthService, get_current_user, get_current_student, get_current_employer
from .auth_models import User, JobFavorite, JobApplication, JobView
from .auth_schemas import (
    UserCreate, UserLogin, TokenResponse, UserResponse, 
    JobFavoriteCreate, JobFavoriteResponse, JobFavoriteWithJob, JobApplicationCreate, JobApplicationResponse,
    StudentProfileUpdate, EmployerProfileUpdate, JobViewCreate, JobViewResponse, JobAnalytics, 
    EmployerJobCreate, EmployerJobUpdate
)
from .models import Job, Company
from .schemas import Job as JobSchema
from .session_service import SessionService
import logging
import uuid
from pathlib import Path
from sqlalchemy import text

logger = logging.getLogger(__name__)

router = APIRouter(tags=["authentication"])

@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (Student or Employer)"""
    auth_service = AuthService(db)
    user = auth_service.create_user(user_data)
    return user

@router.post("/login", response_model=TokenResponse)
def login_user(login_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login user and return tokens with session management"""
    auth_service = AuthService(db)
    
    user = auth_service.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = auth_service.create_access_token(user)
    refresh_token = auth_service.create_refresh_token(user, request)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=1800,  # 30 minutes
        user=UserResponse.from_orm(user)
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

# Student-specific endpoints
student_router = APIRouter(prefix="/student", tags=["student"])

@student_router.get("/favorites", response_model=List[JobFavoriteWithJob])
def get_student_favorites(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get student's favorite jobs"""
    favorites = db.query(JobFavorite).filter(
        JobFavorite.user_id == current_user.id
    ).all()
    
    result = []
    for favorite in favorites:
        job = db.query(Job).filter(Job.id == favorite.job_id).first()
        if job:
            job_dict = {
                "id": job.id,
                "title": job.title,
                "description": job.description,
                "location": job.location,
                "city": job.city,
                "state": job.state,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "employment_type": job.employment_type,
                "visa_sponsorship": job.visa_sponsorship,
                "international_student_friendly": job.international_student_friendly,
                "source_website": job.source_website,
                "source_url": job.source_url,
                "company": {
                    "name": job.company.name if job.company else "Unknown",
                    "website": job.company.website if job.company else None
                }
            }
            
            result.append(JobFavoriteWithJob(
                id=favorite.id,
                job_id=favorite.job_id,
                notes=favorite.notes,
                created_at=favorite.created_at,
                job=job_dict
            ))
    
    return result

@student_router.post("/favorites", response_model=JobFavoriteResponse)
def add_job_favorite(
    favorite_data: JobFavoriteCreate,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Add job to favorites"""
    # Check if job exists
    job = db.query(Job).filter(Job.id == favorite_data.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if already favorited
    existing = db.query(JobFavorite).filter(
        JobFavorite.user_id == current_user.id,
        JobFavorite.job_id == favorite_data.job_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Job already in favorites")
    
    favorite = JobFavorite(
        user_id=current_user.id,
        job_id=favorite_data.job_id,
        notes=favorite_data.notes
    )
    
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    
    logger.info(f"Student {current_user.id} added job {favorite_data.job_id} to favorites")
    return favorite

@student_router.delete("/favorites/{favorite_id}")
def remove_job_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Remove job from favorites"""
    favorite = db.query(JobFavorite).filter(
        JobFavorite.id == favorite_id,
        JobFavorite.user_id == current_user.id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    db.delete(favorite)
    db.commit()
    
    logger.info(f"Student {current_user.id} removed favorite {favorite_id}")
    return {"message": "Favorite removed successfully"}

@student_router.put("/profile", response_model=UserResponse)
def update_student_profile(
    profile_data: StudentProfileUpdate,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Update student profile"""
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"Student {current_user.id} updated profile")
    return current_user

# Employer-specific endpoints
employer_router = APIRouter(prefix="/employer", tags=["employer"])

@employer_router.post("/jobs", response_model=JobSchema)
def create_job_posting(
    job_data: EmployerJobCreate,
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Create a new job posting"""
    # Get or create company
    company = None
    if current_user.company_name:
        company = db.query(Company).filter(
            Company.name == current_user.company_name
        ).first()
        
        if not company:
            company = Company(
                name=current_user.company_name,
                website=current_user.company_website,
                size=current_user.company_size,
                industry=current_user.industry
            )
            db.add(company)
            db.commit()
            db.refresh(company)
    
    # Create job
    job = Job(
        title=job_data.title,
        description=job_data.description,
        location=job_data.location,
        city=job_data.city,
        state=job_data.state,
        salary_min=job_data.salary_min,
        salary_max=job_data.salary_max,
        salary_currency=job_data.salary_currency,
        salary=job_data.salary,
        employment_type=job_data.employment_type,
        job_type=job_data.job_type,
        experience_level=job_data.experience_level,
        remote_option=job_data.remote_option,
        visa_sponsorship=job_data.visa_sponsorship,
        visa_type=job_data.visa_type,
        international_student_friendly=job_data.international_student_friendly,
        source_website="joborra.com",
        source_url=f"https://joborra.com/jobs/{job_data.title.lower().replace(' ', '-')}",
        required_skills=job_data.required_skills,
        preferred_skills=job_data.preferred_skills,
        education_requirements=job_data.education_requirements,
        expires_at=job_data.expires_at,
        company_id=company.id if company else None,
        posted_by_user_id=current_user.id,
        is_joborra_job=True
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    logger.info(f"Employer {current_user.id} created job posting: {job.title}")
    return job

@employer_router.post("/jobs/{job_id}/document")
async def upload_job_document(
    job_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Upload a detailed job document for a specific employer-owned job.
    Stores under data/job_docs/<employer_id>/<job_id>/ and updates job.job_document_url.
    """
    # Validate ownership
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.posted_by_user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Validate file type
    allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.md']
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Prepare directory
    base_dir = Path("data/job_docs") / str(current_user.id) / str(job_id)
    base_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    unique_name = f"jobdoc_{uuid.uuid4()}{ext}"
    file_path = base_dir / unique_name
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Update DB
    job.job_document_url = f"/data/job_docs/{current_user.id}/{job_id}/{unique_name}"
    db.commit()
    db.refresh(job)

    logger.info(f"Employer {current_user.id} uploaded document for job {job_id}")
    return {
        "job_id": job.id,
        "job_document_url": job.job_document_url,
        "file_name": file.filename,
        "file_size": len(content)
    }

@employer_router.get("/jobs", response_model=List[JobSchema])
def get_employer_jobs(
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Get all jobs posted by current employer"""
    jobs = db.query(Job).filter(
        Job.posted_by_user_id == current_user.id
    ).all()
    
    return jobs

# Profile Management Endpoints
@router.put("/profile/student", response_model=UserResponse)
def update_student_profile(
    profile_data: StudentProfileUpdate,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Update student profile with enhanced fields"""
    # Update user fields
    for field, value in profile_data.dict(exclude_unset=True).items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"Updated student profile for user {current_user.id}")
    return current_user

@router.put("/profile/employer", response_model=UserResponse)
def update_employer_profile(
    profile_data: EmployerProfileUpdate,
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Update employer profile with enhanced fields"""
    # Update user fields
    for field, value in profile_data.dict(exclude_unset=True).items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"Updated employer profile for user {current_user.id}")
    return current_user

@router.post("/profile/resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a resume (PDF only) and store URL on the user profile"""
    # Validate file type
    allowed_extensions = ['.pdf']
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only PDF resumes are allowed")

    # Create upload directory
    upload_dir = Path("data/resumes") / str(current_user.id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    unique_name = f"resume_{uuid.uuid4()}{ext}"
    file_path = upload_dir / unique_name

    # Save file
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Update user profile
    try:
        current_user.resume_url = f"/data/resumes/{current_user.id}/{unique_name}"
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        # Attempt to add column if it doesn't exist (SQLite-friendly)
        try:
            db.execute(text("ALTER TABLE users ADD COLUMN resume_url VARCHAR(500)"))
            db.commit()
            current_user.resume_url = f"/data/resumes/{current_user.id}/{unique_name}"
            db.commit()
            db.refresh(current_user)
        except Exception:
            raise HTTPException(status_code=500, detail=f"Database error updating resume URL: {str(e)}")

    logger.info(f"User {current_user.id} uploaded resume: {current_user.resume_url}")
    return {
        "resume_url": current_user.resume_url,
        "file_name": file.filename,
        "file_size": len(content)
    }

# Job View Tracking
@router.post("/jobs/{job_id}/view", response_model=JobViewResponse)
def track_job_view(
    job_id: int,
    view_data: JobViewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track job view for analytics"""
    # Check if job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Create job view record
    job_view = JobView(
        job_id=job_id,
        user_id=current_user.id,
        referrer=view_data.referrer
    )
    
    db.add(job_view)
    db.commit()
    db.refresh(job_view)
    
    return job_view

# Employer Analytics
@employer_router.get("/analytics/jobs", response_model=List[JobAnalytics])
def get_job_analytics(
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Get analytics for employer's job postings"""
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Get employer's jobs with analytics
    jobs = db.query(Job).filter(Job.posted_by_user_id == current_user.id).all()
    
    analytics = []
    for job in jobs:
        # Total views
        total_views = db.query(JobView).filter(JobView.job_id == job.id).count()
        
        # Unique views (distinct users)
        unique_views = db.query(func.count(func.distinct(JobView.user_id))).filter(
            JobView.job_id == job.id,
            JobView.user_id.isnot(None)
        ).scalar() or 0
        
        # Student views (users with student role)
        student_views = db.query(JobView).join(User).filter(
            JobView.job_id == job.id,
            User.role == "STUDENT"
        ).count()
        
        # Anonymous views
        anonymous_views = db.query(JobView).filter(
            JobView.job_id == job.id,
            JobView.user_id.is_(None)
        ).count()
        
        # Views by referrer
        referrer_data = db.query(
            JobView.referrer,
            func.count(JobView.id).label('count')
        ).filter(JobView.job_id == job.id).group_by(JobView.referrer).all()
        
        views_by_referrer = {ref or 'direct': count for ref, count in referrer_data}
        
        # Views by date (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        date_data = db.query(
            func.date(JobView.viewed_at).label('date'),
            func.count(JobView.id).label('count')
        ).filter(
            JobView.job_id == job.id,
            JobView.viewed_at >= thirty_days_ago
        ).group_by(func.date(JobView.viewed_at)).all()
        
        views_by_date = {str(date): count for date, count in date_data}
        
        # Applications and favorites count
        applications_count = len(job.applications)
        favorites_count = len(job.favorited_by)
        
        analytics.append(JobAnalytics(
            job_id=job.id,
            title=job.title,
            total_views=total_views,
            unique_views=unique_views,
            student_views=student_views,
            anonymous_views=anonymous_views,
            views_by_referrer=views_by_referrer,
            views_by_date=views_by_date,
            applications_count=applications_count,
            favorites_count=favorites_count
        ))
    
    return analytics

@employer_router.put("/jobs/{job_id}", response_model=JobSchema)
def update_job_posting(
    job_id: int,
    job_data: EmployerJobUpdate,
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Update job posting"""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.posted_by_user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    for field, value in job_data.dict(exclude_unset=True).items():
        setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    
    logger.info(f"Employer {current_user.id} updated job {job_id}")
    return job

@employer_router.delete("/jobs/{job_id}")
def delete_job_posting(
    job_id: int,
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Delete job posting"""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.posted_by_user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    
    logger.info(f"Employer {current_user.id} deleted job {job_id}")
    return {"message": "Job deleted successfully"}

@employer_router.put("/profile", response_model=UserResponse)
def update_employer_profile(
    profile_data: EmployerProfileUpdate,
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Update employer profile"""
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"Employer {current_user.id} updated profile")
    return current_user

# Include sub-routers
router.include_router(student_router)
router.include_router(employer_router)
