"""
Authentication and User Schema
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from app.auth_models import UserRole

# User Registration/Creation
class UserCreate(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    password: str
    full_name: Optional[str] = None
    contact_number: Optional[str] = None
    role: Optional[UserRole] = UserRole.STUDENT
    
    # Student-specific fields
    university: Optional[str] = None
    degree: Optional[str] = None
    graduation_year: Optional[int] = None
    visa_status: Optional[str] = None
    city_suburb: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    # Study details (moved from visa verification)
    course_name: Optional[str] = None
    institution_name: Optional[str] = None
    course_start_date: Optional[datetime] = None
    course_end_date: Optional[datetime] = None

    
    # Employer-specific fields
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('graduation_year')
    def validate_graduation_year(cls, v):
        if v and (v < 2000 or v > 2030):
            raise ValueError('Graduation year must be between 2000 and 2030')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    contact_number: Optional[str]
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    # Student fields
    university: Optional[str]
    degree: Optional[str]
    graduation_year: Optional[int]
    visa_status: Optional[str]
    city_suburb: Optional[str]
    date_of_birth: Optional[datetime]
    skills: Optional[str]
    experience_level: Optional[str]
    preferred_locations: Optional[str]
    salary_expectations_min: Optional[int]
    salary_expectations_max: Optional[int]
    work_authorization: Optional[str]
    linkedin_profile: Optional[str]
    github_profile: Optional[str]
    portfolio_url: Optional[str]
    bio: Optional[str]
    # JSON strings (arrays) for profile sections
    education: Optional[str]
    experience: Optional[str]
    resume_url: Optional[str]
    # Study details (moved from visa verification)
    course_name: Optional[str]
    institution_name: Optional[str]
    course_start_date: Optional[datetime]
    course_end_date: Optional[datetime]

    
    # Employer fields
    company_name: Optional[str]
    company_website: Optional[str]
    company_size: Optional[str]
    industry: Optional[str]
    company_description: Optional[str]
    company_logo_url: Optional[str]
    company_location: Optional[str]
    hiring_manager_name: Optional[str]
    hiring_manager_title: Optional[str]
    company_benefits: Optional[str]
    company_culture: Optional[str]
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

# Job Favorites
class JobFavoriteCreate(BaseModel):
    job_id: int
    notes: Optional[str] = None

class JobFavoriteResponse(BaseModel):
    id: int
    job_id: int
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobFavoriteWithJob(JobFavoriteResponse):
    job: dict  # Will contain job details
    
    class Config:
        from_attributes = True

# Job Applications
class JobApplicationCreate(BaseModel):
    job_id: int
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    notes: Optional[str] = None

class JobApplicationResponse(BaseModel):
    id: int
    job_id: int
    status: str
    applied_at: datetime
    updated_at: datetime
    cover_letter: Optional[str]
    resume_url: Optional[str]
    notes: Optional[str]
    
    class Config:
        from_attributes = True

# Application with job details for student listings
class JobApplicationWithJob(JobApplicationResponse):
    job: dict  # includes minimal job fields and company info
    
    class Config:
        from_attributes = True

# Employer view: application with applicant (student) info
class EmployerApplicationWithUser(JobApplicationResponse):
    user: dict  # minimal user fields: id, full_name, email, university, degree, graduation_year, resume_url
    job: dict   # minimal job fields
    
    class Config:
        from_attributes = True

# Employer updates application status
class ApplicationStatusUpdate(BaseModel):
    status: str  # applied, reviewed, interviewed, rejected, offered
    notes: Optional[str] = None

# Employer Job Creation
class EmployerJobCreate(BaseModel):
    title: str
    description: str
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "AUD"
    salary: Optional[str] = None
    employment_type: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    remote_option: bool = False
    visa_sponsorship: bool = False
    visa_type: Optional[str] = None
    international_student_friendly: bool = False
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    education_requirements: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Job title must be at least 5 characters long')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if len(v.strip()) < 50:
            raise ValueError('Job description must be at least 50 characters long')
        return v.strip()

class EmployerJobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary: Optional[str] = None
    employment_type: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    remote_option: Optional[bool] = None
    visa_sponsorship: Optional[bool] = None
    visa_type: Optional[str] = None
    international_student_friendly: Optional[bool] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    education_requirements: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None

# User Profile Updates
class StudentProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    contact_number: Optional[str] = None
    university: Optional[str] = None
    degree: Optional[str] = None
    graduation_year: Optional[int] = None
    visa_status: Optional[str] = None
    city_suburb: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    skills: Optional[str] = None
    experience_level: Optional[str] = None
    preferred_locations: Optional[str] = None
    salary_expectations_min: Optional[int] = None
    salary_expectations_max: Optional[int] = None
    work_authorization: Optional[str] = None
    linkedin_profile: Optional[str] = None
    github_profile: Optional[str] = None
    portfolio_url: Optional[str] = None
    bio: Optional[str] = None
    # JSON strings (arrays) for profile sections
    education: Optional[str] = None
    experience: Optional[str] = None
    # Study details (moved from visa verification)
    course_name: Optional[str] = None
    institution_name: Optional[str] = None
    course_start_date: Optional[datetime] = None
    course_end_date: Optional[datetime] = None


class EmployerProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    contact_number: Optional[str] = None
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    company_description: Optional[str] = None
    company_logo_url: Optional[str] = None
    company_location: Optional[str] = None
    hiring_manager_name: Optional[str] = None
    hiring_manager_title: Optional[str] = None
    company_benefits: Optional[str] = None
    company_culture: Optional[str] = None

# Job View Tracking
class JobViewCreate(BaseModel):
    job_id: int
    referrer: Optional[str] = None

class JobViewResponse(BaseModel):
    id: int
    job_id: int
    user_id: Optional[int]
    viewed_at: datetime
    referrer: Optional[str]
    
    class Config:
        from_attributes = True

# Job Analytics for Employers
class JobAnalytics(BaseModel):
    job_id: int
    title: str
    total_views: int
    unique_views: int
    student_views: int
    anonymous_views: int
    views_by_referrer: dict
    views_by_date: dict
    applications_count: int
    favorites_count: int
