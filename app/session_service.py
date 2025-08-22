"""
Enhanced Session Management Service
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Request, HTTPException, status
import logging

from .auth_models import User, UserSession
from .database import get_db

logger = logging.getLogger(__name__)

class SessionService:
    """Enhanced session management with security features"""
    
    def __init__(self, db: Session):
        self.db = db
        self.session_timeout_minutes = 30
        self.max_sessions_per_user = 5
        self.session_cleanup_interval_hours = 24
    
    def create_session(self, user: User, request: Request) -> UserSession:
        """Create a new session with security metadata"""
        # Clean up old sessions first
        self.cleanup_expired_sessions()
        self.enforce_session_limit(user.id)
        
        # Generate secure session token
        session_token = self._generate_session_token()
        expires_at = datetime.utcnow() + timedelta(minutes=self.session_timeout_minutes)
        
        # Extract request metadata
        user_agent = request.headers.get("user-agent", "")
        ip_address = self._get_client_ip(request)
        
        session = UserSession(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
            is_active=True
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        logger.info(f"Created session for user {user.id} from IP {ip_address}")
        return session
    
    def validate_session(self, session_token: str, request: Request) -> Optional[UserSession]:
        """Validate session with security checks"""
        session = self.db.query(UserSession).filter(
            UserSession.session_token == session_token,
            UserSession.is_active == True
        ).first()
        
        if not session:
            return None
        
        # Check if session is expired
        if session.expires_at < datetime.utcnow():
            self.invalidate_session(session_token)
            return None
        
        # Security checks
        current_ip = self._get_client_ip(request)
        current_user_agent = request.headers.get("user-agent", "")
        
        # Optional: IP validation (can be disabled for mobile users)
        if self._should_validate_ip() and session.ip_address != current_ip:
            logger.warning(f"IP mismatch for session {session.id}: {session.ip_address} vs {current_ip}")
            # Could invalidate session or just log warning
        
        # Update session activity
        self.refresh_session(session)
        
        return session
    
    def refresh_session(self, session: UserSession) -> UserSession:
        """Extend session expiry time"""
        session.expires_at = datetime.utcnow() + timedelta(minutes=self.session_timeout_minutes)
        self.db.commit()
        return session
    
    def invalidate_session(self, session_token: str) -> bool:
        """Invalidate a specific session"""
        session = self.db.query(UserSession).filter(
            UserSession.session_token == session_token
        ).first()
        
        if session:
            session.is_active = False
            self.db.commit()
            logger.info(f"Invalidated session {session.id} for user {session.user_id}")
            return True
        
        return False
    
    def invalidate_all_user_sessions(self, user_id: int) -> int:
        """Invalidate all sessions for a user (logout from all devices)"""
        count = self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).update({"is_active": False})
        
        self.db.commit()
        logger.info(f"Invalidated {count} sessions for user {user_id}")
        return count
    
    def get_user_sessions(self, user_id: int) -> List[UserSession]:
        """Get all active sessions for a user"""
        return self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).order_by(UserSession.created_at.desc()).all()
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        count = self.db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        ).update({"is_active": False})
        
        # Delete very old sessions (older than 30 days)
        old_threshold = datetime.utcnow() - timedelta(days=30)
        deleted_count = self.db.query(UserSession).filter(
            UserSession.created_at < old_threshold,
            UserSession.is_active == False
        ).delete()
        
        self.db.commit()
        
        if count > 0 or deleted_count > 0:
            logger.info(f"Cleaned up {count} expired sessions, deleted {deleted_count} old sessions")
        
        return count + deleted_count
    
    def enforce_session_limit(self, user_id: int) -> int:
        """Enforce maximum sessions per user"""
        active_sessions = self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).order_by(UserSession.created_at.desc()).all()
        
        if len(active_sessions) >= self.max_sessions_per_user:
            # Invalidate oldest sessions
            sessions_to_invalidate = active_sessions[self.max_sessions_per_user-1:]
            invalidated_count = 0
            
            for session in sessions_to_invalidate:
                session.is_active = False
                invalidated_count += 1
            
            self.db.commit()
            logger.info(f"Invalidated {invalidated_count} old sessions for user {user_id}")
            return invalidated_count
        
        return 0
    
    def get_session_info(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session information for display"""
        session = self.db.query(UserSession).filter(
            UserSession.session_token == session_token,
            UserSession.is_active == True
        ).first()
        
        if not session:
            return None
        
        return {
            "id": session.id,
            "created_at": session.created_at,
            "expires_at": session.expires_at,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent,
            "is_current": True,  # This would be determined by comparing with current session
            "device_info": self._parse_user_agent(session.user_agent)
        }
    
    def _generate_session_token(self) -> str:
        """Generate cryptographically secure session token"""
        return secrets.token_urlsafe(32)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers (for reverse proxy setups)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def _should_validate_ip(self) -> bool:
        """Determine if IP validation should be enforced"""
        # Could be configurable based on security requirements
        # Might want to disable for mobile users or certain networks
        return False  # Disabled by default for better UX
    
    def _parse_user_agent(self, user_agent: str) -> Dict[str, str]:
        """Parse user agent string for device information"""
        if not user_agent:
            return {"device": "Unknown", "browser": "Unknown", "os": "Unknown"}
        
        # Simple parsing - could use a library like user-agents for better parsing
        device = "Desktop"
        browser = "Unknown"
        os = "Unknown"
        
        user_agent_lower = user_agent.lower()
        
        # Detect mobile devices
        if any(mobile in user_agent_lower for mobile in ["mobile", "android", "iphone", "ipad"]):
            device = "Mobile"
        
        # Detect browser
        if "chrome" in user_agent_lower:
            browser = "Chrome"
        elif "firefox" in user_agent_lower:
            browser = "Firefox"
        elif "safari" in user_agent_lower:
            browser = "Safari"
        elif "edge" in user_agent_lower:
            browser = "Edge"
        
        # Detect OS
        if "windows" in user_agent_lower:
            os = "Windows"
        elif "mac" in user_agent_lower:
            os = "macOS"
        elif "linux" in user_agent_lower:
            os = "Linux"
        elif "android" in user_agent_lower:
            os = "Android"
        elif "ios" in user_agent_lower:
            os = "iOS"
        
        return {
            "device": device,
            "browser": browser,
            "os": os
        }
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics for monitoring"""
        total_sessions = self.db.query(UserSession).count()
        active_sessions = self.db.query(UserSession).filter(
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).count()
        
        expired_sessions = self.db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        ).count()
        
        # Sessions created in last 24 hours
        recent_threshold = datetime.utcnow() - timedelta(hours=24)
        recent_sessions = self.db.query(UserSession).filter(
            UserSession.created_at > recent_threshold
        ).count()
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "expired_sessions": expired_sessions,
            "recent_sessions_24h": recent_sessions,
            "cleanup_needed": expired_sessions > 100
        }
