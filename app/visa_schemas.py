"""
Pydantic schemas for visa verification system
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class VisaStatusEnum(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"
    UNDER_REVIEW = "under_review"

class VisaSubclassEnum(str, Enum):
    STUDENT_500 = "500"
    GRADUATE_485 = "485"
    WORKING_HOLIDAY_417 = "417"
    WORK_AND_HOLIDAY_462 = "462"
    OTHER = "other"

class WorkRightConditionEnum(str, Enum):
    CONDITION_8105 = "8105"
    CONDITION_8104 = "8104"
    UNLIMITED = "unlimited"
    RESTRICTED = "restricted"

class VisaVerificationCreate(BaseModel):
    """Schema for creating a new visa verification"""
    visa_grant_number: Optional[str] = Field(None, max_length=20, description="Visa Grant Number")
    transaction_reference_number: Optional[str] = Field(None, max_length=20, description="Transaction Reference Number")
    visa_subclass: VisaSubclassEnum = Field(..., description="Visa subclass")
    
    # Passport Information
    passport_number: str = Field(..., max_length=20, description="Passport number")
    passport_country: str = Field(..., max_length=3, description="Passport country (ISO 3-letter code)")
    passport_expiry: Optional[datetime] = Field(None, description="Passport expiry date")
    
    # Study Details moved to user profile
    
    @validator('passport_country')
    def validate_passport_country(cls, v):
        if len(v) != 3:
            raise ValueError('Passport country must be 3-letter ISO code')
        return v.upper()
    
    @validator('visa_grant_number', 'transaction_reference_number')
    def validate_visa_numbers(cls, v):
        if v and not v.replace('-', '').replace('/', '').isalnum():
            raise ValueError('Visa numbers must be alphanumeric')
        return v

class VisaVerificationUpdate(BaseModel):
    """Schema for updating visa verification"""
    visa_grant_number: Optional[str] = None
    transaction_reference_number: Optional[str] = None
    passport_expiry: Optional[datetime] = None
    # Study details removed from visa verification

class VisaVerificationResponse(BaseModel):
    """Schema for visa verification response"""
    id: int
    user_id: int
    visa_subclass: VisaSubclassEnum
    visa_status: VisaStatusEnum
    
    # Passport Information
    passport_number: str
    passport_country: str
    passport_expiry: Optional[datetime]
    
    # Visa Status and Dates
    visa_grant_date: Optional[datetime]
    visa_expiry_date: Optional[datetime]
    
    # Work Rights
    work_rights_condition: Optional[WorkRightConditionEnum]
    work_hours_limit: Optional[int]
    work_rights_details: Optional[str]
    
    # Study details are part of user profile
    
    # Verification Details
    verification_method: Optional[str]
    verification_date: Optional[datetime]
    last_vevo_check: Optional[datetime]
    
    # Status
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class VEVOVerificationRequest(BaseModel):
    """Schema for VEVO API verification request"""
    passport_number: str = Field(..., description="Passport number")
    passport_country: str = Field(..., description="Passport country code")
    visa_grant_number: Optional[str] = Field(None, description="Visa Grant Number")
    transaction_reference_number: Optional[str] = Field(None, description="Transaction Reference Number")
    
    @validator('passport_country')
    def validate_country_code(cls, v):
        return v.upper()

class VEVOVerificationResponse(BaseModel):
    """Schema for VEVO API verification response"""
    success: bool
    visa_found: bool = False
    visa_status: Optional[str] = None
    visa_subclass: Optional[str] = None
    visa_expiry_date: Optional[datetime] = None
    work_rights_condition: Optional[str] = None
    work_hours_limit: Optional[int] = None
    error_message: Optional[str] = None
    verification_reference: Optional[str] = None

class DocumentUploadResponse(BaseModel):
    """Schema for document upload response"""
    document_url: str
    document_type: str
    upload_date: datetime
    file_size: int
    file_name: str

class VisaVerificationSummary(BaseModel):
    """Schema for visa verification summary"""
    total_verifications: int
    pending_verifications: int
    verified_count: int
    rejected_count: int
    expired_count: int
    verification_rate: float

class StudentVisaInfo(BaseModel):
    """Schema for student visa information display"""
    has_verification: bool
    verification_status: Optional[VisaStatusEnum] = None
    visa_subclass: Optional[VisaSubclassEnum] = None
    work_hours_limit: Optional[int] = None
    visa_expiry_date: Optional[datetime] = None
    course_end_date: Optional[datetime] = None
    verification_required: bool = False
    verification_message: Optional[str] = None
    
    class Config:
        from_attributes = True
