"""
Visa verification API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
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
    upload_visa_document as supabase_upload_visa_document,
    upload_resume as supabase_upload_resume,
    supabase_configured,
    resolve_storage_url,
    get_supabase_client,
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

@router.post("/documents/upload")
async def upload_visa_document(
    file: UploadFile = File(...),
    document_type: str = Query("vevo", description="Type of document to upload"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload VEVO document and store URL on the user profile (exactly like resume upload)"""
    # Accept document_type parameter for compatibility with frontend
    
    # Debug logging
    logger.info(f"VEVO upload endpoint reached for user {current_user.id}")
    logger.info(f"File received: {file.filename}, content_type: {file.content_type}")
    logger.info(f"Document type: {document_type}")
    
    # Validate document_type parameter
    allowed_document_types = ["vevo", "passport", "visa_grant", "coe"]
    if document_type not in allowed_document_types:
        raise HTTPException(status_code=400, detail=f"Invalid document type. Allowed: {', '.join(allowed_document_types)}")
    
    # Validate file type and filename (same as resume upload)
    allowed_extensions = ['.pdf']
    allowed_mime_types = ['application/pdf']
    
    # Check filename
    if not file.filename:
        logger.error("No filename provided")
        raise HTTPException(status_code=400, detail="Filename is required")
    
    # Check file extension
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only PDF VEVO documents are allowed")
    
    # Check for malicious filenames
    if any(char in file.filename for char in ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']):
        raise HTTPException(status_code=400, detail="Invalid filename characters")

    # Read content once
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")
    
    # Validate file size (10MB limit)
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
    
    # Validate MIME type for additional security (optional)
    try:
        import magic
        mime_type = magic.from_buffer(content, mime=True)
        if mime_type not in allowed_mime_types:
            logger.warning(f"Invalid MIME type detected: {mime_type}")
            # Don't fail for MIME type mismatch, just log it
    except ImportError:
        # python-magic not available, skip MIME validation
        logger.info("python-magic not available, skipping MIME type validation")
    except Exception as e:
        logger.warning(f"MIME type validation failed: {e}")
        # Continue without MIME validation if it fails

    # Use Supabase storage with master bucket (proper visa document upload)
    if supabase_configured():
        try:
            # Use the proper visa document upload function
            vevo_url_value = await supabase_upload_visa_document(current_user.id, document_type, content, file.filename)
            if not vevo_url_value:
                logger.error("Supabase upload returned None - client creation or upload failed")
                raise HTTPException(status_code=500, detail="File upload service is temporarily unavailable. Please try again later.")
        except Exception as e:
            logger.error(f"Supabase upload error: {e}")
            raise HTTPException(status_code=500, detail="File upload service is temporarily unavailable. Please try again later.")
    else:
        logger.error("Supabase not configured - missing environment variables")
        raise HTTPException(
            status_code=503, 
            detail="File upload service is currently unavailable. Please contact support or try again later."
        )

    # Update user profile (exactly like resume upload)
    try:
        current_user.vevo_document_url = vevo_url_value
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        # Attempt to add column if it doesn't exist (SQLite-friendly)
        try:
            db.execute(text("ALTER TABLE users ADD COLUMN vevo_document_url VARCHAR(500)"))
            db.commit()
            current_user.vevo_document_url = vevo_url_value
            db.commit()
            db.refresh(current_user)
        except Exception:
            raise HTTPException(status_code=500, detail=f"Database error updating VEVO document URL: {str(e)}")

    # For response, resolve to public/signed URL
    resolved_url = resolve_storage_url(current_user.vevo_document_url)
    logger.info(f"User {current_user.id} uploaded VEVO document: {resolved_url}")
    logger.info(f"Stored URL: {current_user.vevo_document_url}")
    logger.info(f"Resolved URL: {resolved_url}")
    
    return {
        "document_url": resolved_url,
        "vevo_document_url": resolved_url,  # Keep both for compatibility
        "file_name": file.filename,
        "file_size": len(content)
    }

@router.get("/health")
async def visa_health_check():
    """Health check endpoint to test production environment"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": "production" if "joborra.com" in str(__file__) else "development",
            "supabase_configured": supabase_configured(),
            "imports_working": True,
            "version": "v1.1-with-query-fix",  # Version marker to verify deployment
            "document_type_fix": "applied"  # Marker to confirm our fix is deployed
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/documents")
async def list_visa_documents(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """List uploaded visa documents for the current student.
    Returns a mapping of document_type -> { url, resolved_url } when available.
    """
    service = VisaVerificationService(db)
    verification = service.get_user_visa_status(current_user.id)
    if not verification:
        return {}

    def entry(value: str | None):
        if not value:
            return None
        try:
            return {
                "url": value,
                "resolved_url": resolve_storage_url(value),
            }
        except Exception:
            logger.exception("Failed to resolve storage URL in list_visa_documents")
            return {"url": value, "resolved_url": value}

    return {
        "passport": entry(getattr(verification, "passport_document_url", None)),
        "visa_grant": entry(getattr(verification, "visa_grant_document_url", None)),
        "coe": entry(getattr(verification, "coe_document_url", None)),
        "vevo": entry(getattr(verification, "vevo_document_url", None)),
    }

@router.delete("/documents/{document_type}")
async def delete_visa_document(
    document_type: str,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Delete a specific visa document by type for the current student.
    Clears the DB reference and best-effort deletes local files (under /data/visa_documents).
    Allowed document_type: passport | visa_grant | coe | vevo
    """
    allowed_types = {"passport", "visa_grant", "coe", "vevo"}
    if document_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document type. Allowed: {', '.join(sorted(allowed_types))}"
        )

    service = VisaVerificationService(db)
    verification = service.get_user_visa_status(current_user.id)
    if not verification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No visa verification found")

    field_name = f"{document_type}_document_url"
    existing_url = getattr(verification, field_name, None)

    # Clear DB reference first
    service.update_visa_verification(verification.id, {field_name: None})

    # Try to delete a locally stored file if applicable
    try:
        if isinstance(existing_url, str) and existing_url.startswith("/data/visa_documents/"):
            # Map URL path to local filesystem path (strip leading slash)
            local_path = Path(existing_url.lstrip("/"))
            if local_path.exists():
                local_path.unlink(missing_ok=True)
    except Exception:
        logger.exception("Failed to delete local visa document file; continuing")

    return {"message": "Document deleted", "document_type": document_type}

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
    elif verification.visa_status.value in ['verified', 'under_review']:
        # Simplified: treat under_review as verified for user experience
        if verification.visa_expiry_date and (verification.visa_expiry_date - datetime.utcnow()).days < 30:
            return "Your visa is verified but expires soon. Please renew your visa."
        return "Your visa is verified and you can access all job features."
    elif verification.visa_status.value == 'rejected':
        return f"Visa verification was rejected: {verification.rejection_reason or 'Please check your details and try again.'}"
    elif verification.visa_status.value == 'expired':
        return "Your visa has expired. Please update your visa information."
    else:
        return "Please complete your visa verification to access job features."
