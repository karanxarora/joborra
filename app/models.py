from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Import auth models to ensure they're available for relationships
from app.auth_models import User, JobFavorite, JobApplication

from datetime import datetime
from typing import List, Optional

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    website = Column(String(500))
    size = Column(String(50))  # startup, small, medium, large, enterprise
    industry = Column(String(100))
    location = Column(String(200))
    visa_sponsor_history = Column(Boolean, default=False)
    
    # Accredited sponsor information
    is_accredited_sponsor = Column(Boolean, default=False)
    sponsor_confidence = Column(Float, default=0.0)  # Confidence in sponsor match
    sponsor_abn = Column(String(20))
    sponsor_approval_date = Column(DateTime(timezone=True))
    
    # ATS information
    ats_type = Column(String(50))  # greenhouse, lever, workable, smartrecruiters
    ats_company_id = Column(String(100))  # Company identifier in ATS
    ats_last_scraped = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    jobs = relationship("Job", back_populates="company")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    company_id = Column(Integer, ForeignKey("companies.id"))
    location = Column(String(200), index=True)
    state = Column(String(50), index=True)
    city = Column(String(100), index=True)
    # Salary fields
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String(3), default="AUD")
    # Optional human-readable salary, e.g. "$120k-$150k + super"
    salary = Column(String(255))
    employment_type = Column(String(50))  # full-time, part-time, contract, internship
    # Job type e.g. "software_engineer", "data_scientist", free text from employer
    job_type = Column(String(100))
    experience_level = Column(String(50))  # entry, junior, mid, senior, lead
    remote_option = Column(Boolean, default=False)
    
    # Visa-friendly indicators
    visa_sponsorship = Column(Boolean, default=False)
    visa_sponsorship_confidence = Column(Float, default=0.0)  # 0-1 confidence score
    international_student_friendly = Column(Boolean, default=False)
    # Employer-specified visa type (e.g., "Subclass 482 TSS", "Subclass 500 Student")
    visa_type = Column(String(100))
    
    # Job source metadata
    source_website = Column(String(100), nullable=False)
    source_url = Column(String(1000), unique=True)
    source_job_id = Column(String(100))  # External job ID from source
    required_skills = Column(JSON)  # List of required skills
    preferred_skills = Column(JSON)  # List of preferred skills
    education_requirements = Column(Text)
    posted_date = Column(DateTime)
    expires_at = Column(DateTime)
    # Uploaded detailed job description/document path
    job_document_url = Column(String(500))
    
    # User-posted job fields
    posted_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_joborra_job = Column(Boolean, default=False)  # True for employer-posted jobs
    
    # Timestamps
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)
    is_duplicate = Column(Boolean, default=False)
    
    # Relationships
    company = relationship("Company", back_populates="jobs")
    posted_by_user = relationship("User", back_populates="posted_jobs")
    favorited_by = relationship("JobFavorite", back_populates="job")
    applications = relationship("JobApplication", back_populates="job")
    views = relationship("JobView", back_populates="job")

class VisaKeyword(Base):
    __tablename__ = "visa_keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(200), unique=True, nullable=False)
    keyword_type = Column(String(50))  # positive, negative, neutral
    weight = Column(Float, default=1.0)  # Importance weight for scoring
    category = Column(String(50))  # sponsorship, student_friendly, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ScrapingLog(Base):
    __tablename__ = "scraping_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    source_website = Column(String(100), nullable=False)
    jobs_found = Column(Integer, default=0)
    jobs_processed = Column(Integer, default=0)
    jobs_saved = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    status = Column(String(50), default="running")  # running, completed, failed
    error_details = Column(Text)
