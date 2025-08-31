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

from .database import get_db
from .auth import AuthService, get_current_user, get_current_student, get_current_employer
from .auth_models import User, JobFavorite, JobApplication, JobView
from .auth_schemas import (
    UserCreate, UserLogin, TokenResponse, UserResponse, 
    JobFavoriteCreate, JobFavoriteResponse, JobFavoriteWithJob, JobApplicationCreate, JobApplicationResponse,
    StudentProfileUpdate, EmployerProfileUpdate, JobViewCreate, JobViewResponse, JobAnalytics, 
    EmployerJobCreate, EmployerJobUpdate, JobApplicationWithJob, EmployerApplicationWithUser, ApplicationStatusUpdate
)
from .models import Job, Company
from .schemas import Job as JobSchema
from .session_service import SessionService
import logging
import uuid
from pathlib import Path
from sqlalchemy import text
from .supabase_utils import (
    upload_public_object,
    SUPABASE_STORAGE_BUCKET,
    supabase_configured,
    resolve_storage_url,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["authentication"])

# Simple in-memory rate limiting and token invalidation for verification
from typing import Dict
VERIFICATION_STATE: Dict[int, dict] = {}
RATE_LIMIT_SECONDS = 60  # min interval between requests per user

@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (Student or Employer)"""
    try:
        logger.info(f"Registration attempt for email: {user_data.email}, role: {user_data.role}")
        
        # Test database connection first
        try:
            db.execute(text("SELECT 1"))
            logger.info("Database connection verified for registration")
        except Exception as db_error:
            logger.error(f"Database connection failed during registration: {db_error}")
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        auth_service = AuthService(db)
        
        # Prevent registering a password account if email belongs to an OAuth account
        existing = db.query(User).filter(User.email == user_data.email.lower().strip()).first()
        if existing and existing.oauth_sub:
            logger.warning(f"Registration blocked - email {user_data.email} already registered with Google")
            raise HTTPException(status_code=409, detail="This email is registered with Google. Use Google Sign-In.")
        
        logger.info(f"Creating user account for: {user_data.email}")
        user = auth_service.create_user(user_data)
        logger.info(f"User registered successfully: {user.email} (ID: {user.id}, Role: {user.role})")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed for {user_data.email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.get("/debug/registration")
def debug_registration(db: Session = Depends(get_db)):
    """Debug registration system"""
    try:
        # Test database connection
        result = db.execute(text("SELECT 1 as test"))
        test_result = result.scalar()
        
        # Check users table structure
        columns_result = db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position
        """))
        columns = [{"name": row[0], "type": row[1]} for row in columns_result.fetchall()]
        
        # Check if we can create a test user (without actually creating it)
        test_email = "test@example.com"
        existing = db.query(User).filter(User.email == test_email).first()
        
        return {
            "database_connection": "success",
            "test_query": test_result,
            "users_table_columns": columns,
            "can_query_users": existing is not None or True,  # True if query worked
            "auth_service_available": "AuthService imported successfully"
        }
    except Exception as e:
        return {
            "database_connection": "failed",
            "error": str(e),
            "auth_service_available": "Unknown"
        }

# Email verification endpoints
@router.post("/verify/request")
def request_email_verification(
    current_user: User = Depends(get_current_user),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Issue an email verification token for the current user.
    For now, we return the token and a frontend URL for manual testing.
    """
    try:
        if current_user.is_verified:
            return {"message": "Email already verified"}

        # Rate limit per user
        state = VERIFICATION_STATE.get(current_user.id)
        now = datetime.utcnow()
        if state:
            last = state.get("issued_at")
            if last and (now - last).total_seconds() < RATE_LIMIT_SECONDS:
                raise HTTPException(status_code=429, detail="Please wait before requesting another verification email")

        auth_service = AuthService(db)
        # Create a short-lived token specifically for email verification
        from jose import jwt
        from .auth import SECRET_KEY, ALGORITHM

        import uuid
        token_id = uuid.uuid4().hex
        payload = {
            "sub": str(current_user.id),
            "type": "email_verify",
            "email": current_user.email,
            "jti": token_id,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow(),
        }
        try:
            token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        except Exception as e:
            logger.exception("Failed to create verification token")
            raise HTTPException(status_code=500, detail=f"Failed to create verification token: {str(e)}")

        # Construct a frontend URL using FRONTEND_ORIGIN if provided, else request.base_url
        try:
            frontend_origin = os.getenv("FRONTEND_ORIGIN")
            if frontend_origin:
                base = frontend_origin.rstrip('/')
            else:
                base = str(request.base_url).rstrip('/') if request else ""
            verify_url = f"{base}/verify-email?token={token}" if base else f"/verify-email?token={token}"
        except Exception as e:
            logger.exception("Failed to construct verify_url")
            raise HTTPException(status_code=500, detail=f"Failed to construct verify_url: {str(e)}")

        # Save state for invalidation and rate limiting
        VERIFICATION_STATE[current_user.id] = {"issued_at": now, "token_id": token_id}

        # Attempt to send email if SMTP configured
        try:
            from .email_utils import send_email
            subject = "Verify your Joborra email"
            body = (
                f"Hello {current_user.full_name},\n\n"
                f"Please verify your email by clicking the link below:\n{verify_url}\n\n"
                f"This link expires in 24 hours.\n\nIf you didn't request this, you can ignore this email.\n\n— Joborra"
            )
            html = (
                f"<p>Hello {current_user.full_name},</p>"
                f"<p>Please verify your email by clicking the button below:</p>"
                f"<p><a href=\"{verify_url}\" style=\"display:inline-block;padding:10px 16px;background:#2563eb;color:#ffffff;text-decoration:none;border-radius:6px\">Verify Email</a></p>"
                f"<p>Or copy and paste this link into your browser:<br><a href=\"{verify_url}\">{verify_url}</a></p>"
                f"<p>This link expires in 24 hours.</p>"
                f"<p>If you didn't request this, you can ignore this email.</p>"
                f"<p>— Joborra</p>"
            )
            sent = send_email(current_user.email, subject, body, html)
        except Exception:
            sent = False

        return {
            "message": "Verification email (token) issued",
            "verification_token": token,
            "verify_url": verify_url,
            "email_sent": sent,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("/auth/verify/request failed unexpectedly")
        raise HTTPException(status_code=500, detail=f"Unexpected error in verify/request: {str(e)}")

@router.get("/verify/confirm", response_model=UserResponse)
def confirm_email_verification(token: str, db: Session = Depends(get_db)):
    """Confirm user email via verification token and set is_verified=True."""
    from jose import jwt
    from .auth import SECRET_KEY, ALGORITHM

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "email_verify":
            raise HTTPException(status_code=400, detail="Invalid verification token type")
        user_id = int(payload.get("sub"))
        token_id = payload.get("jti")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Verification token has expired")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check invalidation state
    state = VERIFICATION_STATE.get(user.id)
    if state and state.get("token_id") and token_id != state.get("token_id"):
        raise HTTPException(status_code=400, detail="This verification link has been superseded. Please request a new one.")

    if user.is_verified:
        return user

    user.is_verified = True
    db.commit()
    db.refresh(user)
    return user

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
    email_verified = info.get("email_verified") in (True, "true", "1", 1)
    name = info.get("name") or email.split('@')[0]

    if not sub or not email:
        raise HTTPException(status_code=400, detail="Google token missing subject or email")

    # Upsert/link user according to rules
    auth_service = AuthService(db)
    user_by_sub = db.query(User).filter(User.oauth_sub == sub).first()
    if user_by_sub:
        user = user_by_sub
    else:
        user_by_email = db.query(User).filter(User.email == email).first()
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
                is_verified=bool(email_verified),
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
    email_verified = info.get("email_verified") in (True, "true", "1", 1)
    name = info.get("name") or email.split('@')[0]
    if not sub or not email:
        raise HTTPException(status_code=400, detail="Google token missing subject or email")

    auth_service = AuthService(db)
    user = db.query(User).filter(User.oauth_sub == sub).first()
    if not user:
        user_by_email = db.query(User).filter(User.email == email).first()
        if user_by_email and not user_by_email.oauth_sub:
            raise HTTPException(status_code=409, detail="link_required")
        if not user_by_email:
            from app.auth_models import UserRole
            random_password = secrets.token_urlsafe(24)
            user = User(
                email=email,
                username=email.split('@')[0],
                hashed_password=User.hash_password(random_password),
                full_name=name,
                role=UserRole.STUDENT,
                is_active=True,
                is_verified=bool(email_verified),
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
        experience_level=job_data.experience_level,
        remote_option=job_data.remote_option,
        visa_sponsorship=job_data.visa_sponsorship,
        visa_type=job_data.visa_type,
        international_student_friendly=job_data.international_student_friendly,
        source_website="joborra.com",
        source_url=f"https://joborra.com/jobs/{job_data.title.lower().replace(' ', '-')}",
        required_skills=job_data.required_skills,
        preferred_skills=job_data.preferred_skills,
        education_requirements=job_data.education_requirements,
        expires_at=job_data.expires_at,
        company_id=company.id if company else None,
        posted_by_user_id=current_user.id,
        is_joborra_job=True
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    logger.info(f"Employer {current_user.id} created job posting: {job.title}")
    return job

@employer_router.post("/jobs/{job_id}/document")
async def upload_job_document(
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

    # Try Supabase first
    doc_url_value = None
    if supabase_configured():
        try:
            object_path = f"job_docs/{current_user.id}/{job_id}/doc_{uuid.uuid4()}{ext}"
            uploaded = upload_public_object(
                bucket=SUPABASE_STORAGE_BUCKET,
                object_path=object_path,
                data=content,
                content_type="application/octet-stream",
            )
            if uploaded:
                doc_url_value = uploaded
        except Exception:
            logger.exception("Supabase job document upload failed; will fallback to local storage")

    # Fallback to local
    if not doc_url_value:
        upload_dir = Path("data/job_docs") / str(current_user.id) / str(job_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        unique_name = f"doc_{uuid.uuid4()}{ext}"
        file_path = upload_dir / unique_name
        try:
            with open(file_path, "wb") as f:
                f.write(content)
            doc_url_value = f"/data/job_docs/{current_user.id}/{job_id}/{unique_name}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

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
    
    return jobs

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
async def upload_resume(
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

    # Try Supabase Storage first (public bucket)
    resume_url_value = None
    if supabase_configured():
        try:
            object_path = f"resumes/{current_user.id}/resume_{uuid.uuid4()}{ext}"
            uploaded = upload_public_object(
                bucket=SUPABASE_STORAGE_BUCKET,
                object_path=object_path,
                data=content,
                content_type="application/pdf",
            )
            if uploaded:
                resume_url_value = uploaded
        except Exception:
            logger.exception("Supabase resume upload failed; will fallback to local storage")

    # Fallback to local filesystem if Supabase not configured or failed
    if not resume_url_value:
        upload_dir = Path("data/resumes") / str(current_user.id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        unique_name = f"resume_{uuid.uuid4()}{ext}"
        file_path = upload_dir / unique_name
        try:
            with open(file_path, "wb") as f:
                f.write(content)
            resume_url_value = f"/data/resumes/{current_user.id}/{unique_name}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

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
    return {
        "resume_url": resolved_url,
        "file_name": file.filename,
        "file_size": len(content)
    }

@employer_router.post("/company/logo")
async def upload_company_logo(
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

    # Try Supabase first
    logo_url_value = None
    if supabase_configured():
        try:
            object_path = f"company_logos/{current_user.id}/logo_{uuid.uuid4()}{ext}"
            uploaded = upload_public_object(
                bucket=SUPABASE_STORAGE_BUCKET,
                object_path=object_path,
                data=content,
                content_type={
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".webp": "image/webp",
                    ".svg": "image/svg+xml",
                }.get(ext, "application/octet-stream"),
            )
            if uploaded:
                logo_url_value = uploaded
        except Exception:
            logger.exception("Supabase logo upload failed; will fallback to local storage")

    # Fallback to local storage
    if not logo_url_value:
        upload_dir = Path("data/company_logos") / str(current_user.id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        unique_name = f"logo_{uuid.uuid4()}{ext}"
        file_path = upload_dir / unique_name
        try:
            with open(file_path, "wb") as f:
                f.write(content)
            logo_url_value = f"/data/company_logos/{current_user.id}/{unique_name}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

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
        setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    
    logger.info(f"Employer {current_user.id} updated job {job_id}")
    return job

@employer_router.delete("/jobs/{job_id}")
def delete_job_posting(
    job_id: int,
    current_user: User = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Delete job posting"""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.posted_by_user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    
    logger.info(f"Employer {current_user.id} deleted job {job_id}")
    return {"message": "Job deleted successfully"}

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

# Include sub-routers
router.include_router(student_router)
router.include_router(employer_router)
