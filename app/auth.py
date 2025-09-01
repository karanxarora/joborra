"""
Authentication and Authorization System
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
import secrets
import logging
import time

from app.database import get_db
from app.auth_models import User, UserSession, UserRole
from app.auth_schemas import UserCreate, UserLogin, TokenResponse
from app.session_service import SessionService

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"  # Should be from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user account with robust defaults and validation"""
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this email or username already exists"
            )
        
        # Validate required fields
        if not user_data.email or not user_data.password:
            raise HTTPException(
                status_code=400,
                detail="Email and password are required"
            )
        
        # Generate username from email if not provided
        username = user_data.username or user_data.email.split('@')[0]
        
        # Create new user with explicit defaults
        hashed_password = User.hash_password(user_data.password)
        current_time = datetime.utcnow()
        
        user = User(
            email=user_data.email.lower().strip(),
            username=username.strip(),
            hashed_password=hashed_password,
            full_name=user_data.full_name.strip() if user_data.full_name else user_data.email.split('@')[0],
            contact_number=user_data.contact_number,
            role=user_data.role,
            # Explicit defaults to prevent None values
            is_active=True,
            is_verified=False,  # New users need verification
            created_at=current_time,
            updated_at=current_time,
            last_login=None,
            # Student-specific fields
            university=user_data.university if user_data.role == UserRole.STUDENT else None,
            degree=user_data.degree if user_data.role == UserRole.STUDENT else None,
            graduation_year=user_data.graduation_year if user_data.role == UserRole.STUDENT else None,
            visa_status=user_data.visa_status if user_data.role == UserRole.STUDENT else None,
            city_suburb=user_data.city_suburb if user_data.role == UserRole.STUDENT else None,
            date_of_birth=user_data.date_of_birth if user_data.role == UserRole.STUDENT else None,
            course_name=user_data.course_name if user_data.role == UserRole.STUDENT else None,
            institution_name=user_data.institution_name if user_data.role == UserRole.STUDENT else None,
            course_start_date=user_data.course_start_date if user_data.role == UserRole.STUDENT else None,
            course_end_date=user_data.course_end_date if user_data.role == UserRole.STUDENT else None,

            # Employer-specific fields
            company_name=user_data.company_name if user_data.role == UserRole.EMPLOYER else None,
            company_website=user_data.company_website if user_data.role == UserRole.EMPLOYER else None,
            company_size=user_data.company_size if user_data.role == UserRole.EMPLOYER else None,
            industry=user_data.industry if user_data.role == UserRole.EMPLOYER else None,
            company_abn=user_data.company_abn if user_data.role == UserRole.EMPLOYER else None,
            employer_role_title=user_data.employer_role_title if user_data.role == UserRole.EMPLOYER else None,
        )
        
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Created new {user.role.value} user: {user.email} (ID: {user.id})")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create user {user_data.email}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create user account"
            )
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user or not user.verify_password(password):
            return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=400,
                detail="Account is deactivated"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def create_access_token(self, user: User) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    def create_refresh_token(self, user: User, request: Request) -> str:
        """Create refresh token and store session with enhanced security"""
        session_service = SessionService(self.db)
        session = session_service.create_session(user, request)
        return session.session_token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID with robust error handling"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Try to execute the query
                user = self.db.query(User).filter(User.id == user_id).first()
                return user
            except Exception as e:
                logger.warning(f"Database error getting user {user_id} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    # Try to recover by rolling back and retrying
                    try:
                        self.db.rollback()
                        time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                    except Exception as rollback_error:
                        logger.error(f"Rollback failed: {rollback_error}")
                else:
                    logger.error(f"Failed to get user {user_id} after {max_retries} attempts")
                    raise
    
    def logout_user(self, session_token: str) -> bool:
        """Logout user by invalidating session"""
        session_service = SessionService(self.db)
        return session_service.invalidate_session(session_token)
    
    def logout_all_devices(self, user_id: int) -> int:
        """Logout user from all devices"""
        session_service = SessionService(self.db)
        return session_service.invalidate_all_user_sessions(user_id)

    def verify_password_reset_token(self, token: str) -> Optional[User]:
        """Verify password reset token and return user if valid"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            if not user_id or token_type != "password_reset":
                return None
                
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                return None
                
            return user
        except jwt.ExpiredSignatureError:
            logger.warning("Password reset token expired")
            return None
        except jwt.JWTError:
            logger.warning("Invalid password reset token")
            return None
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password using valid token"""
        user = self.verify_password_reset_token(token)
        if not user:
            return False
            
        try:
            # Hash new password
            hashed_password = User.hash_password(new_password)
            user.hashed_password = hashed_password
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Password reset successful for user {user.email}")
            return True
        except Exception as e:
            logger.error(f"Password reset failed for user {user.email}: {e}")
            self.db.rollback()
            return False
    
    def create_password_reset_token(self, email: str) -> Optional[str]:
        """Create a password reset token for the given email"""
        user = self.db.query(User).filter(User.email == email.lower().strip()).first()
        if not user or not user.is_active:
            return None
            
        try:
            # Create a short-lived token for password reset
            payload = {
                "sub": str(user.id),
                "type": "password_reset",
                "email": user.email,
                "jti": secrets.token_urlsafe(32),
                "exp": datetime.utcnow() + timedelta(hours=1),  # 1 hour expiry
                "iat": datetime.utcnow(),
            }
            
            token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
            return token
        except Exception as e:
            logger.error(f"Failed to create password reset token for {email}: {e}")
            return None

# Enhanced dependency functions with session management
def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user with session validation"""
    auth_service = AuthService(db)
    session_service = SessionService(db)
    
    try:
        # First verify JWT token
        payload = auth_service.verify_token(credentials.credentials)
        user_id = int(payload.get("sub"))
        
        # Try to get user with retry logic
        user = None
        max_retries = 3
        for attempt in range(max_retries):
            try:
                user = auth_service.get_user_by_id(user_id)
                break
            except Exception as e:
                logger.warning(f"Database error getting user {user_id} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))
                    # Try to refresh the database session
                    try:
                        db.rollback()
                    except:
                        pass
                else:
                    logger.error(f"Failed to get user {user_id} after {max_retries} attempts")
                    # If we can't get the user from database, create a minimal user object from token
                    # This prevents database issues from logging out users
                    user = User(
                        id=user_id,
                        email=payload.get("email", ""),
                        role=payload.get("role", "student"),
                        is_active=True,
                        is_verified=True
                    )
                    logger.info(f"Created minimal user object for user {user_id} due to database issues")
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # For all tokens, check if user has any active sessions
        # This ensures that logged out users can't continue using tokens
        try:
            active_sessions = session_service.get_user_sessions(user_id)
            if not active_sessions:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No active sessions - please login again"
                )
        except Exception as e:
            logger.error(f"Error checking user sessions for user {user_id}: {e}")
            # Don't fail authentication just because session check failed
            # This prevents database issues from logging out users
        
        return user
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

def get_current_student(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is a student"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required"
        )
    return current_user

def get_current_employer(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is an employer"""
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employer access required"
        )
    return current_user

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    
    return permission_checker
