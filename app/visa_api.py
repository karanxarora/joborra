"""
Visa verification API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .database import get_db
from .auth import get_current_user, get_current_student
from .auth_models import User
from .visa_models import VisaVerification, VisaVerificationHistory
from .visa_schemas import (
    VisaVerificationCreate, VisaVerificationUpdate, VisaVerificationResponse,
    VEVOVerificationRequest, VEVOVerificationResponse, StudentVisaInfo,
    VisaVerificationSummary, DocumentUploadResponse
)
from .visa_service import VisaVerificationService
from .supabase_utils import (
    upload_public_object,
    SUPABASE_STORAGE_BUCKET,
    supabase_configured,
    resolve_storage_url,
)
import logging
import os
import uuid
from pathlib import Path

router = APIRouter(prefix="/visa", tags=["visa"])
logger = logging.getLogger(__name__)

@router.get("/status", response_model=StudentVisaInfo)
async def get_visa_status(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get current user's visa verification status"""
    service = VisaVerificationService(db)
    verification = service.get_user_visa_status(current_user.id)
    
    if not verification:
        return StudentVisaInfo(
            has_verification=False,
            verification_required=True,
            verification_message="Please complete your visa verification to access all job features"
        )
    
    return StudentVisaInfo(
        has_verification=True,
        verification_status=verification.visa_status,
        visa_subclass=verification.visa_subclass,
        work_hours_limit=verification.work_hours_limit,
        visa_expiry_date=verification.visa_expiry_date,
        course_end_date=getattr(current_user, "course_end_date", None),
        verification_required=verification.visa_status.value in ['pending', 'rejected'],
        verification_message=_get_status_message(verification)
    )

@router.post("/verify", response_model=VisaVerificationResponse)
async def create_visa_verification(
    visa_data: VisaVerificationCreate,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Create a new visa verification request"""
    service = VisaVerificationService(db)
    
    # Check if user already has a verification
    existing = service.get_user_visa_status(current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Visa verification already exists. Use update endpoint to modify."
        )
    
    # Create verification record
    verification = service.create_visa_verification(
        user_id=current_user.id,
        visa_data=visa_data.dict()
    )
    
    return VisaVerificationResponse.from_orm(verification)

@router.put("/verify", response_model=VisaVerificationResponse)
async def update_visa_verification(
    visa_data: VisaVerificationUpdate,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Update existing visa verification"""
    service = VisaVerificationService(db)
    
    # Get existing verification
    existing = service.get_user_visa_status(current_user.id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No visa verification found. Create one first."
        )
    
    # Update verification
    verification = service.update_visa_verification(
        verification_id=existing.id,
        update_data=visa_data.dict(exclude_unset=True)
    )
    
    return VisaVerificationResponse.from_orm(verification)

@router.post("/verify/vevo", response_model=VEVOVerificationResponse)
async def verify_with_vevo(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Verify visa using VEVO system"""
    service = VisaVerificationService(db)
    
    # Get user's verification record
    verification = service.get_user_visa_status(current_user.id)
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No visa verification found. Please create one first."
        )
    
    # Perform VEVO verification
    result = service.verify_with_vevo(verification.id)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"VEVO verification failed: {result.error_message}"
        )
    
    return result

@router.post("/verify/refresh")
async def refresh_visa_status(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Refresh visa status from VEVO"""
    service = VisaVerificationService(db)
    
    verification = service.get_user_visa_status(current_user.id)
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No visa verification found"
        )
    
    success = service.refresh_vevo_status(verification.id)
    
    return {
        "success": success,
        "message": "Visa status refreshed successfully" if success else "Refresh not needed (checked recently)"
    }

@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_visa_document(
    document_type: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Upload visa-related documents"""
    # Validate document type
    allowed_types = ['passport', 'visa_grant', 'coe', 'vevo']
    if document_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Validate file type
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Read once
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read file: {str(e)}"
        )

    # Try Supabase first
    doc_url_value = None
    if supabase_configured():
        try:
            object_path = f"visa_documents/{current_user.id}/{document_type}_{uuid.uuid4()}{file_extension}"
            mime = {
                ".pdf": "application/pdf",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".doc": "application/msword",
                ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            }.get(file_extension, "application/octet-stream")
            uploaded = upload_public_object(
                bucket=SUPABASE_STORAGE_BUCKET,
                object_path=object_path,
                data=content,
                content_type=mime,
            )
            if uploaded:
                doc_url_value = uploaded
        except Exception:
            logger.exception("Supabase visa document upload failed; will fallback to local storage")

    # Fallback to local storage
    if not doc_url_value:
        upload_dir = Path("data/visa_documents") / str(current_user.id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        unique_filename = f"{document_type}_{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        try:
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            doc_url_value = f"/data/visa_documents/{current_user.id}/{unique_filename}"
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
    
    # Update verification record with document URL
    service = VisaVerificationService(db)
    verification = service.get_user_visa_status(current_user.id)
    
    if verification:
        update_data = {f"{document_type}_document_url": doc_url_value}
        service.update_visa_verification(verification.id, update_data)
    
    return DocumentUploadResponse(
        document_url=resolve_storage_url(doc_url_value),
        document_type=document_type,
        upload_date=datetime.utcnow(),
        file_size=len(content),
        file_name=file.filename
    )

@router.get("/history", response_model=List[dict])
async def get_verification_history(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get visa verification history"""
    service = VisaVerificationService(db)
    verification = service.get_user_visa_status(current_user.id)
    
    if not verification:
        return []
    
    history = db.query(VisaVerificationHistory).filter(
        VisaVerificationHistory.visa_verification_id == verification.id
    ).order_by(VisaVerificationHistory.created_at.desc()).all()
    
    return [
        {
            "id": h.id,
            "previous_status": h.previous_status.value,
            "new_status": h.new_status.value,
            "change_reason": h.change_reason,
            "verification_method": h.verification_method,
            "verified_by": h.verified_by,
            "created_at": h.created_at
        }
        for h in history
    ]

# Admin endpoints
@router.get("/admin/summary", response_model=VisaVerificationSummary)
async def get_verification_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get visa verification summary (admin only)"""
    if current_user.role.value != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    total = db.query(VisaVerification).count()
    pending = db.query(VisaVerification).filter(VisaVerification.visa_status == 'pending').count()
    verified = db.query(VisaVerification).filter(VisaVerification.visa_status == 'verified').count()
    rejected = db.query(VisaVerification).filter(VisaVerification.visa_status == 'rejected').count()
    expired = db.query(VisaVerification).filter(VisaVerification.visa_status == 'expired').count()
    
    verification_rate = (verified / total * 100) if total > 0 else 0
    
    return VisaVerificationSummary(
        total_verifications=total,
        pending_verifications=pending,
        verified_count=verified,
        rejected_count=rejected,
        expired_count=expired,
        verification_rate=verification_rate
    )

@router.get("/admin/pending", response_model=List[VisaVerificationResponse])
async def get_pending_verifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending visa verifications (admin only)"""
    if current_user.role.value != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    pending_verifications = db.query(VisaVerification).filter(
        VisaVerification.visa_status == 'pending'
    ).order_by(VisaVerification.created_at.desc()).all()
    
    return [VisaVerificationResponse.from_orm(v) for v in pending_verifications]

def _get_status_message(verification: VisaVerification) -> str:
    """Get status message for verification"""
    if verification.visa_status.value == 'pending':
        return "Your visa verification is being processed. This may take 1-2 business days."
    elif verification.visa_status.value == 'verified':
        if verification.visa_expiry_date and (verification.visa_expiry_date - datetime.utcnow()).days < 30:
            return "Your visa is verified but expires soon. Please renew your visa."
        return "Your visa is verified and you can access all job features."
    elif verification.visa_status.value == 'rejected':
        return f"Visa verification was rejected: {verification.rejection_reason or 'Please check your details and try again.'}"
    elif verification.visa_status.value == 'expired':
        return "Your visa has expired. Please update your visa information."
    elif verification.visa_status.value == 'under_review':
        return "Your visa verification is under manual review. We'll contact you if additional information is needed."
    else:
        return "Please complete your visa verification to access job features."
