"""
Visa verification models for Australian student visa validation
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class VisaStatus(enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"
    UNDER_REVIEW = "under_review"

class VisaSubclass(enum.Enum):
    STUDENT_500 = "500"  # Student visa
    GRADUATE_485 = "485"  # Temporary Graduate visa
    WORKING_HOLIDAY_417 = "417"  # Working Holiday visa
    WORK_AND_HOLIDAY_462 = "462"  # Work and Holiday visa
    OTHER = "other"

class WorkRightCondition(enum.Enum):
    CONDITION_8105 = "8105"  # 48 hours per fortnight
    CONDITION_8104 = "8104"  # No work rights
    UNLIMITED = "unlimited"  # No restrictions
    RESTRICTED = "restricted"  # Other restrictions

class VisaVerification(Base):
    __tablename__ = "visa_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Visa Details
    visa_grant_number = Column(String(20), nullable=True)
    transaction_reference_number = Column(String(20), nullable=True)
    visa_subclass = Column(SQLEnum(VisaSubclass), nullable=False)
    
    # Passport Information
    passport_number = Column(String(20), nullable=False)
    passport_country = Column(String(3), nullable=False)  # ISO 3-letter code
    passport_expiry = Column(DateTime, nullable=True)
    
    # Visa Status and Dates
    visa_status = Column(SQLEnum(VisaStatus), default=VisaStatus.PENDING)
    visa_grant_date = Column(DateTime, nullable=True)
    visa_expiry_date = Column(DateTime, nullable=True)
    
    # Work Rights
    work_rights_condition = Column(SQLEnum(WorkRightCondition), nullable=True)
    work_hours_limit = Column(Integer, nullable=True)  # Hours per fortnight
    work_rights_details = Column(Text, nullable=True)
    
    # Study details moved to user profile (removed from visa verification)
    
    # Verification Details
    verification_method = Column(String(50), nullable=True)  # VEVO, Manual, API
    verification_date = Column(DateTime, nullable=True)
    verification_reference = Column(String(100), nullable=True)
    
    # Document Uploads
    passport_document_url = Column(String(500), nullable=True)
    visa_grant_document_url = Column(String(500), nullable=True)
    coe_document_url = Column(String(500), nullable=True)
    vevo_document_url = Column(String(500), nullable=True)
    
    # Verification Notes and History
    verification_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    last_vevo_check = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="visa_verification")

class VisaVerificationHistory(Base):
    __tablename__ = "visa_verification_history"
    
    id = Column(Integer, primary_key=True, index=True)
    visa_verification_id = Column(Integer, ForeignKey("visa_verifications.id"), nullable=False)
    
    # Status Change
    previous_status = Column(SQLEnum(VisaStatus), nullable=False)
    new_status = Column(SQLEnum(VisaStatus), nullable=False)
    change_reason = Column(Text, nullable=True)
    
    # Verification Details
    verification_method = Column(String(50), nullable=True)
    verification_result = Column(Text, nullable=True)
    verified_by = Column(String(100), nullable=True)  # System, Admin, API
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    visa_verification = relationship("VisaVerification")

class VEVOApiLog(Base):
    __tablename__ = "vevo_api_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    visa_verification_id = Column(Integer, ForeignKey("visa_verifications.id"), nullable=False)
    
    # API Call Details
    api_provider = Column(String(50), nullable=False)  # vSure, Direct VEVO, etc.
    request_data = Column(Text, nullable=True)  # JSON request
    response_data = Column(Text, nullable=True)  # JSON response
    
    # Result
    success = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    verification_result = Column(Text, nullable=True)
    
    # Cost and Usage
    api_cost = Column(String(10), nullable=True)  # Cost in AUD
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    visa_verification = relationship("VisaVerification")
