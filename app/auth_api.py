"""
Authentication API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import os
import secrets
import json
import time

from .database import get_db
from .auth import AuthService, get_current_user, get_current_student, get_current_employer
from .auth_models import User, JobFavorite, JobApplication, JobView
from .auth_schemas import (
    UserCreate, UserLogin, TokenResponse, UserResponse, 
    JobFavoriteCreate, JobFavoriteResponse, JobFavoriteWithJob, JobApplicationCreate, JobApplicationResponse,
    StudentProfileUpdate, EmployerProfileUpdate, JobViewCreate, JobViewResponse, JobAnalytics, 
    EmployerJobCreate, EmployerJobUpdate, JobApplicationWithJob, EmployerApplicationWithUser, ApplicationStatusUpdate,
    ForgotPasswordRequest, ForgotPasswordResponse, ResetPasswordRequest, ResetPasswordResponse
)
from .models import Job, Company, JobDraft
from .schemas import Job as JobSchema, JobDraft as JobDraftSchema, JobDraftCreate, JobDraftUpdate
from .session_service import SessionService
import logging
import uuid
from pathlib import Path
from sqlalchemy import text
from .supabase_utils import (
    upload_resume as supabase_upload_resume,
    upload_company_logo as supabase_upload_company_logo,
    upload_job_document as supabase_upload_job_document,
    supabase_configured,
    resolve_storage_url,
)

logger = logging.getLogger(__name__)

def safe_json_loads(json_str):
    """Safely parse JSON string, return None if invalid or empty - PROD FIX"""
    # If it's already a list or dict, return it as is
    if isinstance(json_str, (list, dict)):
        return json_str
    
    # If it's not a string or is empty, return None
    if not json_str or not isinstance(json_str, str) or not json_str.strip() or json_str == 'null':
        return None
    
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None

router = APIRouter(tags=["authentication"])

# Simple in-memory rate limiting and token invalidation for verification
from typing import Dict
# VERIFICATION_STATE: Dict[int, dict] = {}
  # DISABLED FOR NOW
RATE_LIMIT_SECONDS = 60  # min interval between requests per user

@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (Student or Employer)"""
    auth_service = AuthService(db)
    # Prevent registering a password account if email belongs to an OAuth account
    existing = db.query(User).filter(User.email == user_data.email.lower().strip()).first()
    if existing and existing.oauth_sub:
        raise HTTPException(status_code=409, detail="This email is registered with Google. Use Google Sign-In.")
    user = auth_service.create_user(user_data)
    return user

# # Email verification endpoints - DISABLED FOR NOW
# @router.post("/verify/request")
# def request_email_verification(
#     current_user: User = Depends(get_current_user),
#     request: Request = None,
#     db: Session = Depends(get_db)
# ):
#     """Issue an email verification token for the current user.
#     For now, we return the token and a frontend URL for manual testing.
#     """
#     try:
#         if current_user.is_verified:
#             return {"message": "Email already verified"}

#         # Rate limit per user
#         state = VERIFICATION_STATE.get(current_user.id)
#         now = datetime.utcnow()
#         if state:
#             last = state.get("issued_at")
#             if last and (now - last).total_seconds() < RATE_LIMIT_SECONDS:
#                 raise HTTPException(status_code=429, detail="Please wait before requesting another verification email")

#         auth_service = AuthService(db)
#         # Create a short-lived token specifically for email verification
#         from jose import jwt
#         from .auth import SECRET_KEY, ALGORITHM

#         import uuid
#         token_id = uuid.uuid4().hex
#         payload = {
#             "sub": str(current_user.id),
#             "type": "email_verify",
#             "email": current_user.email,
#             "jti": token_id,
#             "exp": datetime.utcnow() + timedelta(hours=24),
#             "iat": datetime.utcnow(),
#         }
#         try:
#             token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
#         except Exception as e:
#             logger.exception("Failed to create verification token")
#             raise HTTPException(status_code=500, detail=f"Failed to create verification token: {str(e)}")

#         # Construct a frontend URL using FRONTEND_ORIGIN if provided, else request.base_url
#         try:
#             frontend_origin = os.getenv("FRONTEND_ORIGIN")
#             if frontend_origin:
#                 base = frontend_origin.rstrip('/')
#             else:
#                 base = str(request.base_url).rstrip('/') if request else ""
#             verify_url = f"{base}/verify-email?token={token}" if base else f"/verify-email?token={token}"
#         except Exception as e:
#             logger.exception("Failed to construct verify_url")
#             raise HTTPException(status_code=500, detail=f"Failed to construct verify_url: {str(e)}")

#         # Save state for invalidation and rate limiting
#         VERIFICATION_STATE[current_user.id] = {"issued_at": now, "token_id": token_id}

#         # Attempt to send email if SMTP configured
#         try:
#             from .email_utils import send_email
#             subject = "Verify your Joborra email"
#             body = (
#                 f"Hello {current_user.full_name},\n\n"
#                 f"Please verify your email by clicking the link below:\n{verify_url}\n\n"
#                 f"This link expires in 24 hours.\n\nIf you didn't request this, you can ignore this email.\n\n— Joborra"
#             )
#             html = (
#                 f"<p>Hello {current_user.full_name},</p>"
#                 f"<p>Please verify your email by clicking the button below:</p>"
#                 f"<p><a href=\"{verify_url}\" style=\"display:inline-block;padding:10px 16px;background:#2563eb;color:#ffffff;text-decoration:none;border-radius:6px\">Verify Email</a></p>"
#                 f"<p>Or copy and paste this link into your browser:<br><a href=\"{verify_url}\">{verify_url}</a></p>"
#                 f"<p>This link expires in 24 hours.</p>"
#                 f"<p>If you didn't request this, you can ignore this email.</p>"
#                 f"<p>— Joborra</p>"
#             )
#             sent = send_email(current_user.email, subject, body, html)
#         except Exception:
#             sent = False

#         return {
#             "message": "Verification email (token) issued",
#             "verification_token": token,
#             "verify_url": verify_url,
#             "email_sent": sent,
#         }
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.exception("/auth/verify/request failed unexpectedly")
#         raise HTTPException(status_code=500, detail=f"Unexpected error in verify/request: {str(e)}")

# @router.get("/verify/confirm", response_model=UserResponse)
# def confirm_email_verification(token: str, db: Session = Depends(get_db)):
#     """Confirm user email via verification token and set is_verified=True."""
#     from jose import jwt
#     from .auth import SECRET_KEY, ALGORITHM

#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         if payload.get("type") != "email_verify":
#             raise HTTPException(status_code=400, detail="Invalid verification token type")
#         user_id = int(payload.get("sub"))
#         token_id = payload.get("jti")
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=400, detail="Verification token has expired")
#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid verification token")

#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Check invalidation state
#     state = VERIFICATION_STATE.get(user.id)
#     if state and state.get("token_id") and token_id != state.get("token_id"):
#         raise HTTPException(status_code=400, detail="This verification link has been superseded. Please request a new one.")

#     if user.is_verified:
#         return user

#     user.is_verified = True
#     db.commit()
#     db.refresh(user)
#     return user

@router.post("/login", response_model=TokenResponse)
def login_user(login_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login user and return tokens with session management"""
    auth_service = AuthService(db)
    # Block password login if the account is Google-linked only
    existing = db.query(User).filter(User.email == login_data.email.lower().strip()).first()
    if existing and existing.oauth_sub:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This email uses Google Sign-In. Please continue with Google.")

    user = auth_service.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = auth_service.create_access_token(user)
    refresh_token = auth_service.create_refresh_token(user, request)
    
    # Resolve user URLs for token response
    try:
        user.resume_url = resolve_storage_url(getattr(user, "resume_url", None))
        user.company_logo_url = resolve_storage_url(getattr(user, "company_logo_url", None))
    except Exception:
        logger.exception("Failed to resolve media URLs in login_user")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=1800,  # 30 minutes
        user=UserResponse.from_orm(user)
    )

# ----------------------------
# Google OAuth 2.0 Endpoints
# ----------------------------

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

def _default_google_redirect_base(request: Request) -> str:
    # Prefer FRONTEND_ORIGIN for building absolute URLs, fallback to request base
    frontend_origin = os.getenv("FRONTEND_ORIGIN")
    if frontend_origin:
        return frontend_origin.rstrip('/')
    return str(request.base_url).rstrip('/')

def _get_google_redirect_uri(request: Request) -> str:
    # Use explicit env override if provided, else try to infer API base + path
    explicit = os.getenv("GOOGLE_REDIRECT_URI")
    if explicit:
        return explicit
    # Infer based on current request host to support local/prod without config changes
    base = str(request.base_url).rstrip('/')
    return f"{base}/api/auth/google/callback"

@router.get("/google/login")
def google_login(request: Request):
    """Initiate Google OAuth by redirecting to Google's consent screen."""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth not configured: missing GOOGLE_CLIENT_ID")

    redirect_uri = _get_google_redirect_uri(request)
    state = secrets.token_urlsafe(16)
    nonce = secrets.token_urlsafe(16)

    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "nonce": nonce,
        "access_type": "offline",
        "prompt": "consent",
    }
    from urllib.parse import urlencode
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/google/callback", response_model=TokenResponse)
def google_callback(code: Optional[str] = None, error: Optional[str] = None, request: Request = None, db: Session = Depends(get_db)):
    """Handle Google's OAuth redirect: exchange code for tokens, upsert/link user, and return Joborra tokens."""
    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET):
        raise HTTPException(status_code=500, detail="Google OAuth not configured")

    redirect_uri = _get_google_redirect_uri(request)

    # Exchange authorization code for tokens
    import requests
    token_resp = requests.post("https://oauth2.googleapis.com/token", data={
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    })
    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Failed to exchange code: {token_resp.text}")
    token_data = token_resp.json()
    id_token = token_data.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="No id_token in Google response")

    # Validate ID token and extract user info via Google tokeninfo
    info_resp = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": id_token})
    if info_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid Google id_token")
    info = info_resp.json()

    aud = info.get("aud")
    if aud != GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=400, detail="Google token audience mismatch")
    sub = info.get("sub")
    email = (info.get("email") or "").lower().strip()
    # email_verified = info.get("email_verified") in (True, "true", "1", 1)  # DISABLED FOR NOW
    name = info.get("name") or email.split('@')[0]

    if not sub or not email:
        raise HTTPException(status_code=400, detail="Google token missing subject or email")

    # Upsert/link user according to rules
    auth_service = AuthService(db)
    user_by_sub = db.query(User).filter(User.oauth_sub == sub).first()
    if user_by_sub:
        user = user_by_sub
    else:
        user_by_email = db.query(User).filter(User.email == email.lower().strip()).first()
        if user_by_email:
            # If existing standalone account, require linking first
            if not user_by_email.oauth_sub:
                raise HTTPException(status_code=409, detail="link_required")
            user = user_by_email
        else:
            # Create new Google user
            from app.auth_models import UserRole
            random_password = secrets.token_urlsafe(24)
            user = User(
                email=email,
                username=email.split('@')[0],
                hashed_password=User.hash_password(random_password),
                full_name=name,
                role=UserRole.STUDENT,
                is_active=True,
        # is_verified=bool(email_verified),  # DISABLED FOR NOW
                oauth_provider="google",
                oauth_sub=sub,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

    # Issue Joborra tokens
    access_token = auth_service.create_access_token(user)
    refresh_token = auth_service.create_refresh_token(user, request)
    try:
        user.resume_url = resolve_storage_url(getattr(user, "resume_url", None))
        user.company_logo_url = resolve_storage_url(getattr(user, "company_logo_url", None))
    except Exception:
        logger.exception("Failed to resolve media URLs in google_callback")
    # If FRONTEND_ORIGIN is configured, redirect to frontend with tokens
    frontend_origin = os.getenv("FRONTEND_ORIGIN")
    if frontend_origin:
        from urllib.parse import urlencode
        q = urlencode({
            "oauth": "success",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": 1800,
        })
        return RedirectResponse(url=f"{frontend_origin.rstrip('/')}/auth?{q}")

    # Fallback to JSON response (useful for local testing)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=1800,
        user=UserResponse.from_orm(user)
    )

@router.post("/oauth/google", response_model=TokenResponse)
def oauth_google_login(payload: dict, request: Request, db: Session = Depends(get_db)):
    """Login or signup via Google ID token posted by frontend (Google Identity Services)."""
    id_token = payload.get("id_token") if isinstance(payload, dict) else None
    if not id_token:
        raise HTTPException(status_code=400, detail="id_token is required")
    import requests
    info_resp = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": id_token})
    if info_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid Google id_token")
    info = info_resp.json()
    if info.get("aud") != GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=400, detail="Google token audience mismatch")
    sub = info.get("sub")
    email = (info.get("email") or "").lower().strip()
    # email_verified = info.get("email_verified") in (True, "true", "1", 1)  # DISABLED FOR NOW
    name = info.get("name") or email.split('@')[0]
    if not sub or not email:
        raise HTTPException(status_code=400, detail="Google token missing subject or email")

    auth_service = AuthService(db)
    user = db.query(User).filter(User.oauth_sub == sub).first()
    if not user:
        user_by_email = db.query(User).filter(User.email == email.lower().strip()).first()
        if user_by_email and not user_by_email.oauth_sub:
            raise HTTPException(status_code=409, detail="link_required")
        if not user_by_email:
            from app.auth_models import UserRole
            random_password = secrets.token_urlsafe(24)
            user = User(
                email=email.lower().strip(),
                username=email.split('@')[0],
                hashed_password=User.hash_password(random_password),
                full_name=name,
                role=UserRole.STUDENT,
                is_active=True,
        # is_verified=bool(email_verified),  # DISABLED FOR NOW
                oauth_provider="google",
                oauth_sub=sub,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user = user_by_email
    access_token = auth_service.create_access_token(user)
    refresh_token = auth_service.create_refresh_token(user, request)
    try:
        user.resume_url = resolve_storage_url(getattr(user, "resume_url", None))
        user.company_logo_url = resolve_storage_url(getattr(user, "company_logo_url", None))
    except Exception:
        logger.exception("Failed to resolve media URLs in oauth_google_login")
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, expires_in=1800, user=UserResponse.from_orm(user))

@router.post("/oauth/google/link", response_model=UserResponse)
def oauth_google_link(payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Link Google account to an existing standalone account using an ID token."""
    id_token = payload.get("id_token") if isinstance(payload, dict) else None
    if not id_token:
        raise HTTPException(status_code=400, detail="id_token is required")
    if current_user.oauth_sub:
        return current_user
    import requests
    info_resp = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": id_token})
    if info_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid Google id_token")
    info = info_resp.json()
    if info.get("aud") != GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=400, detail="Google token audience mismatch")
    sub = info.get("sub")
    email = (info.get("email") or "").lower().strip()
    if not sub or not email:
        raise HTTPException(status_code=400, detail="Google token missing subject or email")
    if email != (current_user.email or "").lower().strip():
        raise HTTPException(status_code=400, detail="Google email does not match your account email")
    # Ensure no other account is already linked with this sub
    existing = db.query(User).filter(User.oauth_sub == sub).first()
    if existing and existing.id != current_user.id:
        raise HTTPException(status_code=409, detail="This Google account is already linked to another user")
    current_user.oauth_provider = "google"
    current_user.oauth_sub = sub
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile with resolved media URLs"""
    # Resolve potentially private storage URLs
    try:
        if hasattr(current_user, "resume_url"):
            current_user.resume_url = resolve_storage_url(getattr(current_user, "resume_url", None))
        if hasattr(current_user, "company_logo_url"):
            current_user.company_logo_url = resolve_storage_url(getattr(current_user, "company_logo_url", None))
    except Exception:
        logger.exception("Failed to resolve user media URLs in /auth/me")
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

@student_router.post("/applications", response_model=JobApplicationResponse)
def submit_job_application(
    app_data: JobApplicationCreate,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Student submits an application to a job."""
    # Validate job exists
    job = db.query(Job).filter(Job.id == app_data.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Prevent duplicate applications
    existing = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.job_id == app_data.job_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied to this job")

    application = JobApplication(
        user_id=current_user.id,
        job_id=app_data.job_id,
        cover_letter=app_data.cover_letter,
        resume_url=app_data.resume_url,
        notes=app_data.notes,
        status="applied",
        applied_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    logger.info(f"Student {current_user.id} applied to job {app_data.job_id}")
    return application

@student_router.get("/applications", response_model=List[JobApplicationWithJob])
def list_student_applications(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """List applications submitted by the current student with job info."""
    apps = db.query(JobApplication).filter(JobApplication.user_id == current_user.id).all()
    results: List[JobApplicationWithJob] = []
    for app in apps:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        if not job:
            continue
        job_dict = {
            "id": job.id,
            "title": job.title,
            "location": job.location,
            "city": job.city,
            "state": job.state,
            "company": {
                "id": job.company.id if job.company else None,
                "name": job.company.name if job.company else None,
                "website": job.company.website if job.company else None,
            },
        }
        results.append(JobApplicationWithJob(
            id=app.id,
            job_id=app.job_id,
            status=app.status,
            applied_at=app.applied_at,
            updated_at=app.updated_at,
            cover_letter=app.cover_letter,
            resume_url=resolve_storage_url(app.resume_url),
            notes=app.notes,
            job=job_dict,
        ))
    return results

 

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
    
    # Resolve media URLs for response
    try:
        if hasattr(current_user, "resume_url"):
            current_user.resume_url = resolve_storage_url(getattr(current_user, "resume_url", None))
    except Exception:
        logger.exception("Failed to resolve media URLs in update_student_profile")
    logger.info(f"Student {current_user.id} updated profile")
    return current_user

# Employer-specific endpoints
employer_router = APIRouter(prefix="/employer", tags=["employer"])


@employer_router.get("/candidates/recommended")
def recommended_candidates(
    job_id: int,
    limit: int = 20,
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Return top student candidates recommended for an employer-owned job.
    Basic scoring uses skills overlap and visa/international-friendly flags.
    """
    # Ensure job is owned by employer
    job = db.query(Job).filter(Job.id == job_id, Job.posted_by_user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Prepare job skill sets
    req_skills = set((job.required_skills or []) if isinstance(job.required_skills, list) else [])
    pref_skills = set((job.preferred_skills or []) if isinstance(job.preferred_skills, list) else [])

    # Fetch students
    from .auth_models import UserRole
    students = db.query(User).filter(User.role == UserRole.STUDENT).all()

    def parse_skills(s: str | None) -> set[str]:
        if not s:
            return set()
        try:
            # stored as comma-separated or JSON; try JSON first
            import json
            if s.strip().startswith('['):
                return set(x.strip().lower() for x in json.loads(s) if isinstance(x, str))
        except Exception:
            pass
        # fallback: comma-separated
        return set(x.strip().lower() for x in s.split(',') if x.strip())

    def score_user(u: User) -> float:
        score = 0.0
        u_skills = parse_skills(getattr(u, 'skills', None))
        # required skills: +3 each
        score += 3.0 * len(u_skills & set(map(str.lower, req_skills)))
        # preferred skills: +1 each
        score += 1.0 * len(u_skills & set(map(str.lower, pref_skills)))
        # visa/international fit
        if job.international_student_friendly:
            score += 0.5
        if job.visa_sponsorship and (getattr(u, 'work_authorization', '') or '').lower() in {"student_visa", "work_visa"}:
            score += 0.5
        # location preference simple boost
        try:
            prefs = parse_skills(getattr(u, 'preferred_locations', None))
            loc_tokens = {t.strip().lower() for t in [job.city or '', job.state or '', job.location or ''] if t}
            if prefs and (prefs & loc_tokens):
                score += 0.5
        except Exception:
            pass
        return score

    ranked = []
    for stu in students:
        ranked.append((score_user(stu), stu))
    ranked.sort(key=lambda x: x[0], reverse=True)
    ranked = [r for r in ranked if r[0] > 0][: max(1, min(limit, 100))]

    results = []
    for sc, stu in ranked:
        results.append({
            "score": sc,
            "user": {
                "id": stu.id,
                "full_name": stu.full_name,
                "email": stu.email,
                "university": getattr(stu, 'university', None),
                "degree": getattr(stu, 'degree', None),
                "graduation_year": getattr(stu, 'graduation_year', None),
                "skills": getattr(stu, 'skills', None),
                "resume_url": resolve_storage_url(getattr(stu, 'resume_url', None)),
            }
        })
    return {"job_id": job.id, "count": len(results), "items": results}

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
        role_category=job_data.role_category,
        experience_level=job_data.experience_level,
        remote_option=job_data.remote_option,
        visa_sponsorship=job_data.visa_sponsorship,
        visa_types=json.dumps(job_data.visa_types) if job_data.visa_types else None,
        international_student_friendly=job_data.international_student_friendly,
        source_website="joborra.com",
        source_url=f"https://joborra.com/jobs/{job_data.title.lower().replace(' ', '-')}-{int(time.time())}",
        required_skills=job_data.required_skills,
        preferred_skills=job_data.preferred_skills,
        education_requirements=job_data.education_requirements,
        expires_at=job_data.expires_at,
        company_id=company.id if company else None,
        posted_by_user_id=current_user.id,
        is_joborra_job=True,
        posted_date=datetime.now()
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    logger.info(f"Employer {current_user.id} created job posting: {job.title}")
    
    # Return properly formatted response
    return {
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "location": job.location,
        "state": job.state,
        "city": job.city,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "salary_currency": job.salary_currency,
        "salary": job.salary,
        "employment_type": job.employment_type,
        "job_type": job.job_type,
        "role_category": job.role_category,
        "experience_level": job.experience_level,
        "remote_option": job.remote_option,
        "visa_sponsorship": job.visa_sponsorship,
        "visa_sponsorship_confidence": job.visa_sponsorship_confidence,
        "international_student_friendly": job.international_student_friendly,
        "visa_types": safe_json_loads(job.visa_types),
        "source_website": job.source_website,
        "source_url": job.source_url,
        "source_job_id": job.source_job_id,
        "required_skills": job.required_skills,
        "preferred_skills": job.preferred_skills,
        "education_requirements": job.education_requirements,
        "posted_date": job.posted_date,
        "expires_at": job.expires_at,
        "job_document_url": job.job_document_url,
        "posted_by_user_id": job.posted_by_user_id,
        "is_joborra_job": job.is_joborra_job,
        "scraped_at": job.scraped_at,
        "updated_at": job.updated_at,
        "is_active": job.is_active,
        "is_duplicate": job.is_duplicate,
        "company_id": job.company_id
    }

@employer_router.post("/jobs/{job_id}/document")
async def upload_employer_job_document(
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
    # Read once
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

    # Use Supabase storage with master bucket
    if supabase_configured():
        try:
            doc_url_value = await supabase_upload_job_document(current_user.id, job_id, content, file.filename)
            if not doc_url_value:
                raise HTTPException(status_code=500, detail="Failed to upload job document")
        except Exception as e:
            logger.error(f"Supabase upload error: {e}")
            raise HTTPException(status_code=500, detail="Storage upload failed")
    else:
        logger.error("Supabase not configured - missing environment variables")
        raise HTTPException(
            status_code=503, 
            detail="File upload service is currently unavailable. Please contact support or try again later."
        )

    # Update DB
    job.job_document_url = doc_url_value
    db.commit()
    db.refresh(job)

    resolved_url = resolve_storage_url(job.job_document_url)
    logger.info(f"Employer {current_user.id} uploaded document for job {job_id}")
    return {
        "job_id": job.id,
        "job_document_url": resolved_url,
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
    
    # Return properly formatted response for each job
    return [
        {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "location": job.location,
            "state": job.state,
            "city": job.city,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "salary_currency": job.salary_currency,
            "salary": job.salary,
            "employment_type": job.employment_type,
            "job_type": job.job_type,
            "role_category": job.role_category,
            "experience_level": job.experience_level,
            "remote_option": job.remote_option,
            "visa_sponsorship": job.visa_sponsorship,
            "visa_sponsorship_confidence": job.visa_sponsorship_confidence,
            "international_student_friendly": job.international_student_friendly,
            "visa_types": safe_json_loads(job.visa_types),
            "source_website": job.source_website,
            "source_url": job.source_url,
            "source_job_id": job.source_job_id,
            "required_skills": job.required_skills,
            "preferred_skills": job.preferred_skills,
            "education_requirements": job.education_requirements,
            "posted_date": job.posted_date,
            "expires_at": job.expires_at,
            "job_document_url": job.job_document_url,
            "posted_by_user_id": job.posted_by_user_id,
            "is_joborra_job": job.is_joborra_job,
            "scraped_at": job.scraped_at,
            "updated_at": job.updated_at,
            "is_active": job.is_active,
            "is_duplicate": job.is_duplicate,
            "company_id": job.company_id
        }
        for job in jobs
    ]

# Job Draft Management Endpoints
@employer_router.post("/job-drafts")
def create_job_draft(
    draft_data: JobDraftCreate,
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Create a new job draft"""
    try:
        # Serialize skills to JSON strings with better error handling
        import json
        try:
            required_skills_json = json.dumps(draft_data.required_skills) if draft_data.required_skills else None
            preferred_skills_json = json.dumps(draft_data.preferred_skills) if draft_data.preferred_skills else None
            visa_types_json = json.dumps(draft_data.visa_types) if draft_data.visa_types else None
            logger.info(f"Creating draft with skills: required={draft_data.required_skills}, preferred={draft_data.preferred_skills}")
        except Exception as e:
            logger.error(f"Error serializing skills: {e}")
            required_skills_json = None
            preferred_skills_json = None
            visa_types_json = None
        
        # Use ORM instead of raw SQL for better error handling
        draft = JobDraft(
            title=draft_data.title,
            description=draft_data.description,
            location=draft_data.location,
            city=draft_data.city,
            state=draft_data.state,
            salary_min=draft_data.salary_min,
            salary_max=draft_data.salary_max,
            salary_currency=draft_data.salary_currency or "AUD",
            salary=draft_data.salary,
            employment_type=draft_data.employment_type,
            job_type=draft_data.job_type,
            role_category=draft_data.role_category,
            experience_level=draft_data.experience_level,
            remote_option=draft_data.remote_option or False,
            visa_sponsorship=draft_data.visa_sponsorship or False,
            visa_types=visa_types_json,
            international_student_friendly=draft_data.international_student_friendly or False,
            required_skills=required_skills_json,
            preferred_skills=preferred_skills_json,
            education_requirements=draft_data.education_requirements,
            expires_at=draft_data.expires_at,
            draft_name=draft_data.draft_name,
            step=draft_data.step or 0,
            created_by_user_id=current_user.id
        )
        
        db.add(draft)
        try:
            db.commit()
            db.refresh(draft)
            draft_id = draft.id
        except Exception as db_error:
            logger.error(f"Database commit error: {db_error}")
            db.rollback()
            # Retry once with a small delay for SQLite concurrency issues
            import time
            time.sleep(0.1)
            db.commit()
            db.refresh(draft)
            draft_id = draft.id
        
        logger.info(f"Employer {current_user.id} created job draft: {draft_data.title}")
        
        # Return simple response
        return {
            'id': draft_id,
            'title': draft_data.title,
            'message': 'Draft saved successfully'
        }
    except Exception as e:
        logger.error(f"Error creating job draft: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating job draft: {str(e)}")

@employer_router.get("/job-drafts")
def get_employer_job_drafts(
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Get all job drafts created by current employer"""
    drafts = db.query(JobDraft).filter(
        JobDraft.created_by_user_id == current_user.id
    ).order_by(JobDraft.updated_at.desc()).all()
    
    # Convert to response format
    response_data = []
    for draft in drafts:
        response_data.append({
            'id': draft.id,
            'title': draft.title,
            'description': draft.description,
            'location': draft.location,
            'city': draft.city,
            'state': draft.state,
            'salary_min': draft.salary_min,
            'salary_max': draft.salary_max,
            'salary_currency': draft.salary_currency,
            'salary': draft.salary,
            'employment_type': draft.employment_type,
            'job_type': draft.job_type,
            'role_category': draft.role_category,
            'experience_level': draft.experience_level,
            'remote_option': draft.remote_option,
            'visa_sponsorship': draft.visa_sponsorship,
            'visa_types': safe_json_loads(draft.visa_types),
            'international_student_friendly': draft.international_student_friendly,
            'required_skills': json.loads(draft.required_skills) if draft.required_skills else None,
            'preferred_skills': json.loads(draft.preferred_skills) if draft.preferred_skills else None,
            'education_requirements': draft.education_requirements,
            'expires_at': draft.expires_at,
            'draft_name': draft.draft_name,
            'step': draft.step,
            'created_by_user_id': draft.created_by_user_id,
            'created_at': draft.created_at,
            'updated_at': draft.updated_at
        })
    return response_data

@employer_router.get("/job-drafts/{draft_id}")
def get_job_draft(
    draft_id: int,
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Get a specific job draft by ID"""
    draft = db.query(JobDraft).filter(
        JobDraft.id == draft_id,
        JobDraft.created_by_user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(status_code=404, detail="Job draft not found")
    
    # Convert to response format
    response_data = {
        'id': draft.id,
        'title': draft.title,
        'description': draft.description,
        'location': draft.location,
        'city': draft.city,
        'state': draft.state,
        'salary_min': draft.salary_min,
        'salary_max': draft.salary_max,
        'salary_currency': draft.salary_currency,
        'salary': draft.salary,
        'employment_type': draft.employment_type,
        'job_type': draft.job_type,
        'role_category': draft.role_category,
        'experience_level': draft.experience_level,
        'remote_option': draft.remote_option,
        'visa_sponsorship': draft.visa_sponsorship,
        'visa_types': safe_json_loads(draft.visa_types),
        'international_student_friendly': draft.international_student_friendly,
        'required_skills': safe_json_loads(draft.required_skills),
        'preferred_skills': safe_json_loads(draft.preferred_skills),
        'education_requirements': draft.education_requirements,
        'expires_at': draft.expires_at,
        'draft_name': draft.draft_name,
        'step': draft.step,
        'created_by_user_id': draft.created_by_user_id,
        'created_at': draft.created_at,
        'updated_at': draft.updated_at
    }
    return response_data

@employer_router.put("/job-drafts/{draft_id}")
def update_job_draft(
    draft_id: int,
    draft_data: JobDraftUpdate,
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Update a job draft"""
    draft = db.query(JobDraft).filter(
        JobDraft.id == draft_id,
        JobDraft.created_by_user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(status_code=404, detail="Job draft not found")
    
    # Update fields
    for field, value in draft_data.dict(exclude_unset=True).items():
        if field in ['required_skills', 'preferred_skills', 'visa_types'] and value is not None:
            setattr(draft, field, json.dumps(value))
        else:
            setattr(draft, field, value)
    
    db.commit()
    db.refresh(draft)
    
    logger.info(f"Employer {current_user.id} updated job draft {draft_id}")
    
    # Convert to response format
    response_data = {
        'id': draft.id,
        'title': draft.title,
        'description': draft.description,
        'location': draft.location,
        'city': draft.city,
        'state': draft.state,
        'salary_min': draft.salary_min,
        'salary_max': draft.salary_max,
        'salary_currency': draft.salary_currency,
        'salary': draft.salary,
        'employment_type': draft.employment_type,
        'job_type': draft.job_type,
        'role_category': draft.role_category,
        'experience_level': draft.experience_level,
        'remote_option': draft.remote_option,
        'visa_sponsorship': draft.visa_sponsorship,
        'visa_types': safe_json_loads(draft.visa_types),
        'international_student_friendly': draft.international_student_friendly,
        'required_skills': safe_json_loads(draft.required_skills),
        'preferred_skills': safe_json_loads(draft.preferred_skills),
        'education_requirements': draft.education_requirements,
        'expires_at': draft.expires_at,
        'draft_name': draft.draft_name,
        'step': draft.step,
        'created_by_user_id': draft.created_by_user_id,
        'created_at': draft.created_at,
        'updated_at': draft.updated_at
    }
    return response_data

@employer_router.delete("/job-drafts/{draft_id}")
def delete_job_draft(
    draft_id: int,
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Delete a job draft"""
    draft = db.query(JobDraft).filter(
        JobDraft.id == draft_id,
        JobDraft.created_by_user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(status_code=404, detail="Job draft not found")
    
    db.delete(draft)
    db.commit()
    
    logger.info(f"Employer {current_user.id} deleted job draft {draft_id}")
    return {"message": "Job draft deleted successfully"}

@employer_router.post("/job-drafts/{draft_id}/publish", response_model=JobSchema)
def publish_job_draft(
    draft_id: int,
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Publish a job draft as a live job posting"""
    try:
        draft = db.query(JobDraft).filter(
            JobDraft.id == draft_id,
            JobDraft.created_by_user_id == current_user.id
        ).first()
        
        if not draft:
            raise HTTPException(status_code=404, detail="Job draft not found")
        
        # Log draft data for debugging
        logger.info(f"Publishing draft {draft_id} with skills: required={draft.required_skills}, preferred={draft.preferred_skills}")
        
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
        
        # Parse skills safely with better error handling
        try:
            required_skills_parsed = safe_json_loads(draft.required_skills)
            preferred_skills_parsed = safe_json_loads(draft.preferred_skills)
            logger.info(f"Parsed skills: required={required_skills_parsed}, preferred={preferred_skills_parsed}")
        except Exception as e:
            logger.error(f"Error parsing skills: {e}")
            required_skills_parsed = []
            preferred_skills_parsed = []
        
        # Create job from draft
        job = Job(
            title=draft.title,
            description=draft.description,
            location=draft.location,
            city=draft.city,
            state=draft.state,
            salary_min=draft.salary_min,
            salary_max=draft.salary_max,
            salary_currency=draft.salary_currency,
            salary=draft.salary,
            employment_type=draft.employment_type,
            job_type=draft.job_type,
            role_category=draft.role_category,
            experience_level=draft.experience_level,
            remote_option=draft.remote_option,
            visa_sponsorship=draft.visa_sponsorship,
            visa_types=draft.visa_types,
            international_student_friendly=draft.international_student_friendly,
            source_website="joborra.com",
            source_url=f"https://joborra.com/jobs/{draft.title.lower().replace(' ', '-')}-{draft_id}-{int(time.time())}",
            required_skills=required_skills_parsed,
            preferred_skills=preferred_skills_parsed,
            education_requirements=draft.education_requirements,
            expires_at=draft.expires_at,
            company_id=company.id if company else None,
            posted_by_user_id=current_user.id,
            is_joborra_job=True,
            posted_date=datetime.now()
        )
        
        db.add(job)
        try:
            db.commit()
            db.refresh(job)
        except Exception as db_error:
            logger.error(f"Database commit error during job creation: {db_error}")
            db.rollback()
            # Retry once with a small delay for SQLite concurrency issues
            import time
            time.sleep(0.1)
            db.commit()
            db.refresh(job)
        
        # Delete the draft after successful publishing
        db.delete(draft)
        try:
            db.commit()
        except Exception as db_error:
            logger.error(f"Database commit error during draft deletion: {db_error}")
            db.rollback()
            # Retry once with a small delay for SQLite concurrency issues
            import time
            time.sleep(0.1)
            db.commit()
        
        logger.info(f"Successfully published job draft {draft_id} as job {job.id}")
        
        # Return the job object directly (FastAPI will serialize it according to JobSchema)
        return job
        
    except Exception as e:
        logger.error(f"Error publishing job draft {draft_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to publish job draft: {str(e)}")

@employer_router.get("/applications", response_model=List[EmployerApplicationWithUser])
def list_employer_applications(
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """List applications for all jobs posted by the current employer, including applicant info."""
    # Fetch applications joined with jobs owned by employer
    applications = db.query(JobApplication).join(Job, JobApplication.job_id == Job.id).filter(
        Job.posted_by_user_id == current_user.id
    ).all()

    results: List[EmployerApplicationWithUser] = []
    for app in applications:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        user = db.query(User).filter(User.id == app.user_id).first()
        if not job or not user:
            continue
        job_dict = {
            "id": job.id,
            "title": job.title,
            "location": job.location,
            "city": job.city,
            "state": job.state,
            "company": {
                "id": job.company.id if job.company else None,
                "name": job.company.name if job.company else (current_user.company_name or "Unknown"),
                "website": job.company.website if job.company else None,
            },
        }
        user_dict = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "university": user.university,
            "degree": user.degree,
            "graduation_year": user.graduation_year,
            "resume_url": resolve_storage_url(getattr(user, "resume_url", None)),
        }
        results.append(EmployerApplicationWithUser(
            id=app.id,
            job_id=app.job_id,
            status=app.status,
            applied_at=app.applied_at,
            updated_at=app.updated_at,
            cover_letter=app.cover_letter,
            resume_url=resolve_storage_url(app.resume_url),
            notes=app.notes,
            job=job_dict,
            user=user_dict,
        ))
    return results

@employer_router.put("/applications/{application_id}/status", response_model=JobApplicationResponse)
def update_application_status(
    application_id: int,
    update: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Employer updates the status (and optional notes) of an application they own."""
    # Find application joined to a job owned by employer
    app = db.query(JobApplication).join(Job, JobApplication.job_id == Job.id).filter(
        JobApplication.id == application_id,
        Job.posted_by_user_id == current_user.id
    ).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    allowed_status = {"applied", "reviewed", "interviewed", "rejected", "offered"}
    if update.status not in allowed_status:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {', '.join(sorted(allowed_status))}")

    app.status = update.status
    if update.notes is not None:
        app.notes = update.notes
    app.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(app)
    return app

# Profile Management Endpoints
@router.put("/profile/student", response_model=UserResponse)
def update_student_profile(
    profile_data: StudentProfileUpdate,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Update student profile with enhanced fields"""
    # Update user fields
    import json
    for field, value in profile_data.dict(exclude_unset=True).items():
        if not hasattr(current_user, field):
            continue
        # Normalize education/experience to JSON strings if lists/objects are sent
        if field in {"education", "experience"} and value is not None and not isinstance(value, str):
            try:
                setattr(current_user, field, json.dumps(value))
            except Exception:
                # Fallback to string cast
                setattr(current_user, field, str(value))
        else:
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
async def upload_user_resume(
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

    # Read content once
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

    # Use Supabase storage with master bucket
    if supabase_configured():
        try:
            resume_url_value = await supabase_upload_resume(current_user.id, content, file.filename)
            if not resume_url_value:
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

    # Update user profile
    try:
        current_user.resume_url = resume_url_value
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        # Attempt to add column if it doesn't exist (SQLite-friendly)
        try:
            db.execute(text("ALTER TABLE users ADD COLUMN resume_url VARCHAR(500)"))
            db.commit()
            current_user.resume_url = resume_url_value
            db.commit()
            db.refresh(current_user)
        except Exception:
            raise HTTPException(status_code=500, detail=f"Database error updating resume URL: {str(e)}")

    # For response, resolve to public/signed URL
    resolved_url = resolve_storage_url(current_user.resume_url)
    logger.info(f"User {current_user.id} uploaded resume: {resolved_url}")
    logger.info(f"Stored URL: {current_user.resume_url}")
    logger.info(f"Resolved URL: {resolved_url}")
    return {
        "resume_url": resolved_url,
        "file_name": file.filename,
        "file_size": len(content)
    }

@router.get("/resume/view")
async def view_resume(
    current_user: User = Depends(get_current_user)
):
    """Get the current user's resume URL for viewing."""
    if not current_user.resume_url:
        raise HTTPException(status_code=404, detail="No resume found")
    
    try:
        # Always resolve to master bucket
        resolved_url = resolve_storage_url(current_user.resume_url)
        logger.info(f"Resolving resume URL for user {current_user.id}: {current_user.resume_url} -> {resolved_url}")
        
        if not resolved_url:
            raise HTTPException(status_code=404, detail="Resume not accessible")
        
        return {
            "resume_url": resolved_url,
            "accessible": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get resume URL for user {current_user.id}")
        raise HTTPException(status_code=500, detail="Failed to access resume")


@employer_router.post("/company/logo")
async def upload_employer_company_logo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Upload a company logo image for the employer profile."""
    allowed_extensions = [".png", ".jpg", ".jpeg", ".webp", ".svg"]
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    # Read once
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

    # Use Supabase storage with master bucket
    if supabase_configured():
        try:
            logo_url_value = await supabase_upload_company_logo(current_user.id, content, file.filename)
            if not logo_url_value:
                raise HTTPException(status_code=500, detail="Failed to upload company logo")
        except Exception as e:
            logger.error(f"Supabase upload error: {e}")
            raise HTTPException(status_code=500, detail="Storage upload failed")
    else:
        logger.error("Supabase not configured - missing environment variables")
        raise HTTPException(
            status_code=503, 
            detail="File upload service is currently unavailable. Please contact support or try again later."
        )

    # Update user profile
    current_user.company_logo_url = logo_url_value
    db.commit()
    db.refresh(current_user)

    resolved_url = resolve_storage_url(current_user.company_logo_url)
    logger.info(f"Employer {current_user.id} uploaded company logo: {resolved_url}")
    return {
        "company_logo_url": resolved_url,
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
        if field in ['visa_types'] and value is not None:
            # Convert visa_types to JSON string (Job model uses Text column)
            setattr(job, field, json.dumps(value))
        else:
            setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    
    logger.info(f"Employer {current_user.id} updated job {job_id}")
    
    # Return properly formatted response
    return {
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "location": job.location,
        "state": job.state,
        "city": job.city,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "salary_currency": job.salary_currency,
        "salary": job.salary,
        "employment_type": job.employment_type,
        "job_type": job.job_type,
        "role_category": job.role_category,
        "experience_level": job.experience_level,
        "remote_option": job.remote_option,
        "visa_sponsorship": job.visa_sponsorship,
        "visa_sponsorship_confidence": job.visa_sponsorship_confidence,
        "international_student_friendly": job.international_student_friendly,
        "visa_types": safe_json_loads(job.visa_types),
        "source_website": job.source_website,
        "source_url": job.source_url,
        "source_job_id": job.source_job_id,
        "required_skills": job.required_skills,
        "preferred_skills": job.preferred_skills,
        "education_requirements": job.education_requirements,
        "posted_date": job.posted_date,
        "expires_at": job.expires_at,
        "job_document_url": job.job_document_url,
        "posted_by_user_id": job.posted_by_user_id,
        "is_joborra_job": job.is_joborra_job,
        "scraped_at": job.scraped_at,
        "updated_at": job.updated_at,
        "is_active": job.is_active,
        "is_duplicate": job.is_duplicate,
        "company_id": job.company_id
    }

@employer_router.delete("/jobs/{job_id}")
def delete_job_posting(
    job_id: int,
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Delete job posting"""
    try:
        logger.info(f"Attempting to delete job {job_id} for user {current_user.id}")
        
        job = db.query(Job).filter(
            Job.id == job_id,
            Job.posted_by_user_id == current_user.id
        ).first()
        
        if not job:
            logger.warning(f"Job {job_id} not found for user {current_user.id}")
            raise HTTPException(status_code=404, detail="Job not found")
        
        logger.info(f"Found job {job_id}, proceeding with deletion")
        db.delete(job)
        db.commit()
        
        logger.info(f"Employer {current_user.id} deleted job {job_id}")
        return {"message": "Job deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting job {job_id} for user {current_user.id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete job: {str(e)}")

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
    
    # Resolve media URLs for response
    try:
        if hasattr(current_user, "company_logo_url"):
            current_user.company_logo_url = resolve_storage_url(getattr(current_user, "company_logo_url", None))
    except Exception:
        logger.exception("Failed to resolve media URLs in update_employer_profile")
    logger.info(f"Employer {current_user.id} updated profile")
    return current_user

# Forgot Password endpoints
@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(
    request_data: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Request a password reset for the given email"""
    try:
        auth_service = AuthService(db)
        
        # Check if user exists and is active
        user = db.query(User).filter(
            User.email == request_data.email.lower().strip(),
            User.is_active == True
        ).first()
        
        if not user:
            # Don't reveal if email exists or not for security
            return ForgotPasswordResponse(
                message="If an account with this email exists, a password reset link has been sent.",
                email_sent=True
            )
        
        # Create password reset token
        token = auth_service.create_password_reset_token(request_data.email)
        if not token:
            raise HTTPException(status_code=500, detail="Failed to create password reset token")
        
        # Construct reset URL
        try:
            frontend_origin = os.getenv("FRONTEND_ORIGIN")
            if frontend_origin:
                base = frontend_origin.rstrip('/')
            else:
                base = str(request.base_url).rstrip('/') if request else ""
            reset_url = f"{base}/reset-password?token={token}" if base else f"/reset-password?token={token}"
        except Exception as e:
            logger.exception("Failed to construct reset_url")
            raise HTTPException(status_code=500, detail="Failed to construct reset URL")
        
        # Send password reset email
        email_sent = False
        try:
            from .email_utils import send_email
            subject = "Reset your Joborra password"
            body = (
                f"Hello {user.full_name or user.username},\n\n"
                f"You requested a password reset for your Joborra account.\n\n"
                f"Click the link below to reset your password:\n{reset_url}\n\n"
                f"This link expires in 1 hour.\n\n"
                f"If you didn't request this password reset, you can safely ignore this email.\n\n"
                f"— Joborra"
            )
            html = (
                f"<p>Hello {user.full_name or user.username},</p>"
                f"<p>You requested a password reset for your Joborra account.</p>"
                f"<p>Click the button below to reset your password:</p>"
                f"<p><a href=\"{reset_url}\" style=\"display:inline-block;padding:10px 16px;background:#dc2626;color:#ffffff;text-decoration:none;border-radius:6px\">Reset Password</a></p>"
                f"<p>Or copy and paste this link into your browser:<br><a href=\"{reset_url}\">{reset_url}</a></p>"
                f"<p>This link expires in 1 hour.</p>"
                f"<p>If you didn't request this password reset, you can safely ignore this email.</p>"
                f"<p>— Joborra</p>"
            )
            email_sent = send_email(user.email, subject, body, html)
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            # Still return success to avoid revealing if email exists
        
        return ForgotPasswordResponse(
            message="If an account with this email exists, a password reset link has been sent.",
            email_sent=email_sent
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Forgot password request failed")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/reset-password", response_model=ResetPasswordResponse)
def reset_password(
    request_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Reset password using the provided token"""
    try:
        auth_service = AuthService(db)
        
        # Reset password using token
        success = auth_service.reset_password(request_data.token, request_data.new_password)
        
        if not success:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        return ResetPasswordResponse(
            message="Password reset successful. You can now log in with your new password.",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Password reset failed")
        raise HTTPException(status_code=500, detail="Internal server error")

# Include sub-routers
router.include_router(student_router)
router.include_router(employer_router)
