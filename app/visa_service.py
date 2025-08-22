"""
Visa verification service for Australian student visas
"""
import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .visa_models import VisaVerification, VisaVerificationHistory, VEVOApiLog, VisaStatus, VisaSubclass, WorkRightCondition
import logging

logger = logging.getLogger(__name__)

@dataclass
class VEVOVerificationResponse:
    success: bool
    visa_found: bool
    error_message: Optional[str] = None
    visa_status: Optional[str] = None
    visa_subclass: Optional[str] = None
    visa_expiry_date: Optional[datetime] = None
    work_rights_condition: Optional[str] = None
    work_hours_limit: Optional[int] = None
    verification_reference: Optional[str] = None


class VisaVerificationService:
    """Service for handling visa verification operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.vevo_api_key = None  # To be configured
        self.vsure_api_key = None  # To be configured
        
    def create_visa_verification(self, user_id: int, visa_data: Dict[str, Any]) -> VisaVerification:
        """Create a new visa verification record"""
        verification = VisaVerification(
            user_id=user_id,
            visa_grant_number=visa_data.get('visa_grant_number'),
            transaction_reference_number=visa_data.get('transaction_reference_number'),
            visa_subclass=VisaSubclass(visa_data['visa_subclass']),
            passport_number=visa_data['passport_number'],
            passport_country=visa_data['passport_country'],
            passport_expiry=visa_data.get('passport_expiry'),
            course_name=visa_data.get('course_name'),
            institution_name=visa_data.get('institution_name'),
            course_start_date=visa_data.get('course_start_date'),
            course_end_date=visa_data.get('course_end_date'),
            coe_number=visa_data.get('coe_number'),
            visa_status=VisaStatus.PENDING
        )
        
        self.db.add(verification)
        self.db.commit()
        self.db.refresh(verification)
        
        # Log the creation
        self._log_status_change(verification.id, None, VisaStatus.PENDING, "Initial verification created")
        
        return verification
    
    def update_visa_verification(self, verification_id: int, update_data: Dict[str, Any]) -> Optional[VisaVerification]:
        """Update an existing visa verification"""
        verification = self.db.query(VisaVerification).filter(VisaVerification.id == verification_id).first()
        if not verification:
            return None
            
        for key, value in update_data.items():
            if hasattr(verification, key) and value is not None:
                setattr(verification, key, value)
        
        verification.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(verification)
        
        return verification
    
    def verify_with_vevo(self, verification_id: int) -> VEVOVerificationResponse:
        """Verify visa using VEVO API (via vSure or direct)"""
        verification = self.db.query(VisaVerification).filter(VisaVerification.id == verification_id).first()
        if not verification:
            return VEVOVerificationResponse(success=False, visa_found=False, error_message="Verification record not found")
        
        # Prepare VEVO request data
        vevo_request_data = {
            "passport_number": verification.passport_number,
            "passport_country": verification.passport_country,
            "visa_grant_number": verification.visa_grant_number,
            "transaction_reference_number": verification.transaction_reference_number
        }
        
        # Try vSure API first (more reliable for student visas)
        if hasattr(self, 'vsure_api_key') and self.vsure_api_key:
            result = self._verify_with_vsure(verification, vevo_request_data)
        else:
            # Fallback to mock verification for development
            result = self._mock_vevo_verification(verification, vevo_request_data)
        
        # Update verification record based on result
        if result.success and result.visa_found:
            self._update_verification_from_vevo(verification, result)
        elif result.success and not result.visa_found:
            self._mark_verification_rejected(verification, "Visa not found in VEVO system")
        else:
            self._mark_verification_failed(verification, result.error_message or "VEVO verification failed")
        
        return result
    
    def _verify_with_vsure(self, verification: VisaVerification, request: Dict[str, Any]) -> VEVOVerificationResponse:
        """Verify using vSure API"""
        api_url = "https://api.vsure.com.au/v2/visa-checks/student"
        
        headers = {
            "Authorization": f"Bearer {self.vsure_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "passport_number": request.get("passport_number"),
            "passport_country": request.get("passport_country"),
            "visa_grant_number": request.get("visa_grant_number"),
            "transaction_reference_number": request.get("transaction_reference_number")
        }
        
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=30.0)
            response_data = response.json()
            
            # Log API call
            self._log_vevo_api_call(verification.id, "vSure", payload, response_data, response.status_code == 200)
            
            if response.status_code == 200 and response_data.get("success"):
                return self._parse_vsure_response(response_data)
            else:
                error_msg = response_data.get("error", "Unknown API error")
                return VEVOVerificationResponse(success=False, visa_found=False, error_message=error_msg)
                    
        except Exception as e:
            logger.error(f"vSure API error: {str(e)}")
            self._log_vevo_api_call(verification.id, "vSure", payload, {"error": str(e)}, False)
            return VEVOVerificationResponse(success=False, visa_found=False, error_message=f"API connection error: {str(e)}")
    
    def _mock_vevo_verification(self, verification: VisaVerification, request: Dict[str, Any]) -> VEVOVerificationResponse:
        """Mock VEVO verification for development/testing"""
        # Simulate different scenarios based on passport number patterns
        passport = request.get("passport_number", "").upper()
        
        if passport.startswith("VALID"):
            return VEVOVerificationResponse(
                success=True,
                visa_found=True,
                visa_status="active",
                visa_subclass="500",
                visa_expiry_date=datetime.now() + timedelta(days=365),
                work_rights_condition="8105",
                work_hours_limit=48,
                verification_reference=f"MOCK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
        elif passport.startswith("EXPIRED"):
            return VEVOVerificationResponse(
                success=True,
                visa_found=True,
                visa_status="expired",
                visa_subclass="500",
                visa_expiry_date=datetime.now() - timedelta(days=30),
                work_rights_condition="8105",
                work_hours_limit=48,
                verification_reference=f"MOCK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
        elif passport.startswith("NOTFOUND"):
            return VEVOVerificationResponse(
                success=True,
                visa_found=False,
                error_message="No visa found for provided details"
            )
        else:
            # Default to valid student visa
            return VEVOVerificationResponse(
                success=True,
                visa_found=True,
                visa_status="active",
                visa_subclass="500",
                visa_expiry_date=datetime.now() + timedelta(days=730),
                work_rights_condition="8105",
                work_hours_limit=48,
                verification_reference=f"MOCK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
    
    def _parse_vsure_response(self, response_data: Dict[str, Any]) -> VEVOVerificationResponse:
        """Parse vSure API response"""
        visa_data = response_data.get("visa", {})
        
        return VEVOVerificationResponse(
            success=True,
            visa_found=visa_data.get("found", False),
            visa_status=visa_data.get("status"),
            visa_subclass=visa_data.get("subclass"),
            visa_expiry_date=self._parse_date(visa_data.get("expiry_date")),
            work_rights_condition=visa_data.get("work_condition"),
            work_hours_limit=visa_data.get("work_hours_limit"),
            verification_reference=response_data.get("reference_id")
        )
    
    def _update_verification_from_vevo(self, verification: VisaVerification, vevo_result: VEVOVerificationResponse):
        """Update verification record from VEVO result"""
        old_status = verification.visa_status
        
        # Determine new status based on VEVO result
        if vevo_result.visa_status == "active":
            new_status = VisaStatus.VERIFIED
        elif vevo_result.visa_status == "expired":
            new_status = VisaStatus.EXPIRED
        else:
            new_status = VisaStatus.UNDER_REVIEW
        
        # Update verification fields
        verification.visa_status = new_status
        verification.visa_expiry_date = vevo_result.visa_expiry_date
        verification.work_rights_condition = WorkRightCondition(vevo_result.work_rights_condition) if vevo_result.work_rights_condition else None
        verification.work_hours_limit = vevo_result.work_hours_limit
        verification.verification_method = "VEVO"
        verification.verification_date = datetime.utcnow()
        verification.verification_reference = vevo_result.verification_reference
        verification.last_vevo_check = datetime.utcnow()
        verification.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        # Log status change
        self._log_status_change(verification.id, old_status, new_status, f"VEVO verification completed: {vevo_result.visa_status}")
    
    def _mark_verification_rejected(self, verification: VisaVerification, reason: str):
        """Mark verification as rejected"""
        old_status = verification.visa_status
        verification.visa_status = VisaStatus.REJECTED
        verification.rejection_reason = reason
        verification.verification_date = datetime.utcnow()
        verification.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        self._log_status_change(verification.id, old_status, VisaStatus.REJECTED, reason)
    
    def _mark_verification_failed(self, verification: VisaVerification, error: str):
        """Mark verification as failed (technical error)"""
        verification.verification_notes = f"Verification failed: {error}"
        verification.updated_at = datetime.utcnow()
        
        self.db.commit()
    
    def _log_status_change(self, verification_id: int, old_status: Optional[VisaStatus], new_status: VisaStatus, reason: str):
        """Log status change in history"""
        history = VisaVerificationHistory(
            visa_verification_id=verification_id,
            previous_status=old_status or VisaStatus.PENDING,
            new_status=new_status,
            change_reason=reason,
            verified_by="System"
        )
        
        self.db.add(history)
        self.db.commit()
    
    def _log_vevo_api_call(self, verification_id: int, provider: str, request_data: Dict, response_data: Dict, success: bool):
        """Log VEVO API call"""
        log_entry = VEVOApiLog(
            visa_verification_id=verification_id,
            api_provider=provider,
            request_data=json.dumps(request_data),
            response_data=json.dumps(response_data),
            success=success,
            error_message=response_data.get("error") if not success else None
        )
        
        self.db.add(log_entry)
        self.db.commit()
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str:
            return None
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
    
    def get_user_visa_status(self, user_id: int) -> Optional[VisaVerification]:
        """Get current visa verification status for user"""
        return self.db.query(VisaVerification).filter(
            VisaVerification.user_id == user_id
        ).first()
    
    def check_visa_expiry_reminders(self) -> List[VisaVerification]:
        """Get visas expiring in the next 30 days"""
        expiry_threshold = datetime.utcnow() + timedelta(days=30)
        
        return self.db.query(VisaVerification).filter(
            VisaVerification.visa_status == VisaStatus.VERIFIED,
            VisaVerification.visa_expiry_date <= expiry_threshold,
            VisaVerification.visa_expiry_date > datetime.utcnow()
        ).all()
    
    def refresh_vevo_status(self, verification_id: int) -> bool:
        """Refresh VEVO status for a verification"""
        verification = self.db.query(VisaVerification).filter(VisaVerification.id == verification_id).first()
        if not verification:
            return False
        
        # Only refresh if last check was more than 24 hours ago
        if verification.last_vevo_check and (datetime.utcnow() - verification.last_vevo_check).days < 1:
            return False
        
        result = self.verify_with_vevo(verification_id)
        return result.success
