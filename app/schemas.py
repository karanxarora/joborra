from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    website: Optional[str] = None
    size: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    visa_sponsor_history: bool = False

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class JobBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "AUD"
    # Human-readable salary string
    salary: Optional[str] = None
    employment_type: Optional[str] = None
    # Free-text job type category
    job_type: Optional[str] = None
    # Role category: SERVICE_RETAIL_HOSPITALITY or STUDY_ALIGNED_PROFESSIONAL
    role_category: Optional[str] = None
    experience_level: Optional[str] = None
    remote_option: bool = False
    visa_sponsorship: bool = False
    visa_sponsorship_confidence: float = 0.0
    international_student_friendly: bool = False
    # Employer-specified visa types (e.g., Subclass codes)
    visa_types: Optional[List[str]] = None
    source_website: str
    source_url: str
    source_job_id: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    education_requirements: Optional[str] = None
    posted_date: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    # URL of uploaded detailed job document
    job_document_url: Optional[str] = None

class JobCreate(JobBase):
    company_id: int

class Job(JobBase):
    id: int
    company_id: Optional[int] = None
    scraped_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    is_duplicate: bool = False
    company: Optional[Company] = None
    
    class Config:
        from_attributes = True

class JobDraftBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "AUD"
    salary: Optional[str] = None
    employment_type: Optional[str] = None
    job_type: Optional[str] = None
    role_category: Optional[str] = None
    experience_level: Optional[str] = None
    remote_option: bool = False
    visa_sponsorship: bool = False
    visa_types: Optional[List[str]] = None
    international_student_friendly: bool = False
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    education_requirements: Optional[str] = None
    expires_at: Optional[datetime] = None
    draft_name: Optional[str] = None
    step: int = 0

class JobDraftCreate(JobDraftBase):
    pass

class JobDraftUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    salary: Optional[str] = None
    employment_type: Optional[str] = None
    job_type: Optional[str] = None
    role_category: Optional[str] = None
    experience_level: Optional[str] = None
    remote_option: Optional[bool] = None
    visa_sponsorship: Optional[bool] = None
    visa_types: Optional[List[str]] = None
    international_student_friendly: Optional[bool] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    education_requirements: Optional[str] = None
    expires_at: Optional[datetime] = None
    draft_name: Optional[str] = None
    step: Optional[int] = None

class JobDraft(JobDraftBase):
    id: int
    created_by_user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class JobFilter(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    visa_sponsorship: Optional[bool] = None
    international_student_friendly: Optional[bool] = None
    remote_option: Optional[bool] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    skills: Optional[List[str]] = None
    company_name: Optional[str] = None
    source_website: Optional[str] = None
    posted_after: Optional[datetime] = None
    
class JobSearchResponse(BaseModel):
    jobs: List[Job]
    total: int
    page: int
    per_page: int
    total_pages: int

class VisaKeywordBase(BaseModel):
    keyword: str
    keyword_type: str
    weight: float = 1.0
    category: str

class VisaKeywordCreate(VisaKeywordBase):
    pass

class VisaKeyword(VisaKeywordBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
