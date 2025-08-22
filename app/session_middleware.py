"""
Session management middleware for automatic cleanup and security
"""
import asyncio
from datetime import datetime, timedelta
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
import logging

from .database import get_db
from .session_service import SessionService

logger = logging.getLogger(__name__)

class SessionMiddleware(BaseHTTPMiddleware):
    """Middleware for session management and automatic cleanup"""
    
    def __init__(self, app, cleanup_interval_hours: int = 24):
        super().__init__(app)
        self.cleanup_interval_hours = cleanup_interval_hours
        self.last_cleanup = datetime.utcnow()
    
    async def dispatch(self, request: Request, call_next):
        # Check if cleanup is needed
        if self._should_run_cleanup():
            await self._run_background_cleanup()
        
        # Process the request
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(response)
        
        return response
    
    def _should_run_cleanup(self) -> bool:
        """Check if session cleanup should be run"""
        time_since_cleanup = datetime.utcnow() - self.last_cleanup
        return time_since_cleanup.total_seconds() > (self.cleanup_interval_hours * 3600)
    
    async def _run_background_cleanup(self):
        """Run session cleanup in background"""
        try:
            # Create a new database session for cleanup
            db = next(get_db())
            session_service = SessionService(db)
            
            # Run cleanup
            cleaned_count = session_service.cleanup_expired_sessions()
            
            if cleaned_count > 0:
                logger.info(f"Background cleanup: removed {cleaned_count} expired sessions")
            
            self.last_cleanup = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error during background session cleanup: {e}")
        finally:
            if 'db' in locals():
                db.close()
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy (basic)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self';"
        )

class SessionCleanupService:
    """Service for scheduled session cleanup"""
    
    def __init__(self):
        self.cleanup_interval = 3600  # 1 hour in seconds
        self.running = False
    
    async def start_cleanup_scheduler(self):
        """Start the background cleanup scheduler"""
        if self.running:
            return
        
        self.running = True
        logger.info("Starting session cleanup scheduler")
        
        while self.running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._perform_cleanup()
            except Exception as e:
                logger.error(f"Error in cleanup scheduler: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def stop_cleanup_scheduler(self):
        """Stop the background cleanup scheduler"""
        self.running = False
        logger.info("Stopped session cleanup scheduler")
    
    async def _perform_cleanup(self):
        """Perform the actual cleanup"""
        try:
            db = next(get_db())
            session_service = SessionService(db)
            
            # Cleanup expired sessions
            cleaned_count = session_service.cleanup_expired_sessions()
            
            # Get statistics
            stats = session_service.get_session_statistics()
            
            if cleaned_count > 0:
                logger.info(
                    f"Scheduled cleanup completed: "
                    f"removed {cleaned_count} expired sessions, "
                    f"active sessions: {stats['active_sessions']}"
                )
            
        except Exception as e:
            logger.error(f"Error during scheduled cleanup: {e}")
        finally:
            if 'db' in locals():
                db.close()

# Global cleanup service instance
cleanup_service = SessionCleanupService()
