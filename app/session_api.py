"""
Session Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from .database import get_db
from .auth import get_current_user
from .auth_models import User
from .session_service import SessionService

router = APIRouter(prefix="/session", tags=["session"])

@router.get("/current", response_model=Dict[str, Any])
async def get_current_session_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current session information for the authenticated user"""
    session_service = SessionService(db)
    
    # Get the most recent active session for this user
    sessions = session_service.get_user_sessions(current_user.id)
    if not sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active sessions found"
        )
    
    # Return the most recent session
    latest_session = sessions[0]  # Sessions are ordered by created_at desc
    return {
        "id": latest_session.id,
        "created_at": latest_session.created_at,
        "expires_at": latest_session.expires_at,
        "ip_address": latest_session.ip_address,
        "user_agent": latest_session.user_agent,
        "device_info": session_service._parse_user_agent(latest_session.user_agent),
        "last_activity": latest_session.last_activity
    }

@router.get("/all", response_model=List[Dict[str, Any]])
async def get_all_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active sessions for current user"""
    session_service = SessionService(db)
    sessions = session_service.get_user_sessions(current_user.id)
    
    return [
        {
            "id": session.id,
            "created_at": session.created_at,
            "expires_at": session.expires_at,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent,
            "device_info": session_service._parse_user_agent(session.user_agent)
        }
        for session in sessions
    ]

@router.post("/logout")
async def logout_current_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout from all sessions (single logout invalidates all sessions for security)"""
    session_service = SessionService(db)
    
    # For security, invalidate ALL user sessions on logout
    # This prevents token reuse and ensures complete logout
    count = session_service.invalidate_all_user_sessions(current_user.id)
    
    return {
        "success": count > 0,
        "message": f"Logged out successfully from {count} sessions" if count > 0 else "No active sessions found"
    }

@router.post("/logout-all")
async def logout_all_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout from all devices/sessions"""
    session_service = SessionService(db)
    count = session_service.invalidate_all_user_sessions(current_user.id)
    
    return {
        "success": True,
        "message": f"Logged out from {count} sessions",
        "sessions_invalidated": count
    }

@router.delete("/session/{session_id}")
async def invalidate_specific_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invalidate a specific session by ID"""
    session_service = SessionService(db)
    
    # Verify the session belongs to the current user
    sessions = session_service.get_user_sessions(current_user.id)
    target_session = next((s for s in sessions if s.id == session_id), None)
    
    if not target_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or doesn't belong to you"
        )
    
    success = session_service.invalidate_session(target_session.session_token)
    
    return {
        "success": success,
        "message": "Session invalidated successfully" if success else "Failed to invalidate session"
    }

@router.post("/cleanup")
async def cleanup_expired_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cleanup expired sessions (admin or self-service)"""
    if current_user.role.value != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    session_service = SessionService(db)
    cleaned_count = session_service.cleanup_expired_sessions()
    
    return {
        "success": True,
        "message": f"Cleaned up {cleaned_count} expired sessions",
        "sessions_cleaned": cleaned_count
    }

@router.get("/statistics", response_model=Dict[str, Any])
async def get_session_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get session statistics (admin only)"""
    if current_user.role.value != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    session_service = SessionService(db)
    stats = session_service.get_session_statistics()
    
    return stats
