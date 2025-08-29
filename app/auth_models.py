"""
Authentication and User Management Models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
from passlib.context import CryptContext
from jose import jwt
from typing import Optional

from .database import Base

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRole(enum.Enum):
    STUDENT = "student"
    EMPLOYER = "employer"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # OAuth fields (for Google Sign-In / account linking)
    oauth_provider = Column(String(50), nullable=True)  # e.g., 'google'
    oauth_sub = Column(String(255), unique=True, index=True, nullable=True)  # provider user id (Google 'sub')
    
    # Student-specific fields
    university = Column(String(255), nullable=True)
    degree = Column(String(255), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    visa_status = Column(String(100), nullable=True)  # e.g., "student_visa", "work_visa", "citizen"
    # Study details (moved from visa verification)
    course_name = Column(String(200), nullable=True)
    institution_name = Column(String(200), nullable=True)
    course_start_date = Column(DateTime, nullable=True)
    course_end_date = Column(DateTime, nullable=True)
    coe_number = Column(String(50), nullable=True)
    
    # Enhanced student profile fields
    skills = Column(Text, nullable=True)  # JSON string of skills
    experience_level = Column(String(50), nullable=True)  # entry, junior, mid, senior
    preferred_locations = Column(Text, nullable=True)  # JSON string of preferred cities/states
    salary_expectations_min = Column(Integer, nullable=True)
    salary_expectations_max = Column(Integer, nullable=True)
    work_authorization = Column(String(100), nullable=True)  # citizen, pr, work_visa, student_visa
    linkedin_profile = Column(String(500), nullable=True)
    github_profile = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    # Education & Experience stored as JSON strings
    education = Column(Text, nullable=True)  # JSON array of education items
    experience = Column(Text, nullable=True)  # JSON array of experience items
    # Resume storage
    resume_url = Column(String(500), nullable=True)
    
    # Employer-specific fields
    company_name = Column(String(255), nullable=True)
    company_website = Column(String(255), nullable=True)
    company_size = Column(String(100), nullable=True)
    industry = Column(String(255), nullable=True)
    
    # Enhanced employer profile fields
    company_description = Column(Text, nullable=True)
    company_logo_url = Column(String(500), nullable=True)
    company_location = Column(String(255), nullable=True)
    hiring_manager_name = Column(String(255), nullable=True)
    hiring_manager_title = Column(String(255), nullable=True)
    company_benefits = Column(Text, nullable=True)  # JSON string of benefits
    company_culture = Column(Text, nullable=True)
    
    # Relationships
    favorites = relationship("JobFavorite", back_populates="user")
    applications = relationship("JobApplication", back_populates="user")
    job_views = relationship("JobView", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")
    # One-to-one relationship with VisaVerification
    visa_verification = relationship(
        "VisaVerification",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    posted_jobs = relationship("Job", back_populates="posted_by_user", foreign_keys="Job.posted_by_user_id")
    job_favorites = relationship("JobFavorite", back_populates="user", cascade="all, delete-orphan")
    job_applications = relationship("JobApplication", back_populates="user", cascade="all, delete-orphan")
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(password, self.hashed_password)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        permissions = {
            UserRole.STUDENT: [
                "view_jobs", "favorite_jobs", "apply_jobs", "view_profile", "edit_profile"
            ],
            UserRole.EMPLOYER: [
                "view_jobs", "create_jobs", "edit_jobs", "delete_jobs", "view_applications",
                "view_profile", "edit_profile", "manage_company"
            ],
            UserRole.ADMIN: [
                "view_jobs", "create_jobs", "edit_jobs", "delete_jobs", "view_applications",
                "view_profile", "edit_profile", "manage_users", "manage_system"
            ]
        }
        return permission in permissions.get(self.role, [])

class JobFavorite(Base):
    __tablename__ = "job_favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)  # Personal notes about the job
    
    # Relationships
    user = relationship("User", back_populates="job_favorites")
    job = relationship("Job", back_populates="favorited_by")
    
    # Unique constraint to prevent duplicate favorites
    __table_args__ = (
        {"extend_existing": True},
    )

class JobApplication(Base):
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    status = Column(String(50), default="applied")  # applied, reviewed, interviewed, rejected, offered
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cover_letter = Column(Text, nullable=True)
    resume_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="job_applications")
    job = relationship("Job", back_populates="applications")

class JobView(Base):
    __tablename__ = "job_views"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Can be null for anonymous views
    viewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    referrer = Column(String(500), nullable=True)  # Where they came from
    session_id = Column(String(255), nullable=True)
    
    # Relationships
    job = relationship("Job", back_populates="views")
    user = relationship("User")

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Security fields
    device_fingerprint = Column(String(255), nullable=True)
    login_method = Column(String(50), default="password")  # password, oauth, etc.
    
    # Relationships
    user = relationship("User", back_populates="sessions")
