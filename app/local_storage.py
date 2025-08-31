"""
Local file storage utility to replace Supabase storage
Provides file upload and management for resumes, company logos, and job documents
"""

import os
import uuid
import logging
import mimetypes
from pathlib import Path
from typing import Optional, BinaryIO
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configuration
LOCAL_STORAGE_BASE_PATH = os.getenv("LOCAL_STORAGE_PATH", "./data")
LOCAL_STORAGE_URL_PREFIX = os.getenv("LOCAL_STORAGE_URL_PREFIX", "/data")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default

def ensure_storage_directory():
    """Ensure the storage directory exists"""
    Path(LOCAL_STORAGE_BASE_PATH).mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories for different file types
    subdirs = ["resumes", "company_logos", "job_docs", "visa_documents"]
    for subdir in subdirs:
        Path(LOCAL_STORAGE_BASE_PATH, subdir).mkdir(parents=True, exist_ok=True)

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower()

def validate_file_type(filename: str, allowed_types: list = None) -> bool:
    """Validate file type based on extension"""
    if not allowed_types:
        # Default allowed types
        allowed_types = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.svg']
    
    ext = get_file_extension(filename)
    return ext in allowed_types

def upload_file(
    content: bytes,
    file_path: str,
    filename: str,
    max_size: int = MAX_FILE_SIZE
) -> Optional[str]:
    """
    Upload file to local storage
    
    Args:
        content: File content as bytes
        file_path: Relative path within storage (e.g., "resumes/user_123")
        filename: Original filename
        max_size: Maximum file size in bytes
    
    Returns:
        Public URL to access the file, or None if upload failed
    """
    try:
        # Validate file size
        if len(content) > max_size:
            logger.error(f"File too large: {len(content)} bytes (max: {max_size})")
            return None
        
        # Validate file type
        if not validate_file_type(filename):
            logger.error(f"Invalid file type: {filename}")
            return None
        
        # Generate unique filename
        file_extension = get_file_extension(filename)
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Ensure directory exists
        full_dir_path = Path(LOCAL_STORAGE_BASE_PATH, file_path)
        full_dir_path.mkdir(parents=True, exist_ok=True)
        
        # Write file
        full_file_path = full_dir_path / unique_filename
        with open(full_file_path, 'wb') as f:
            f.write(content)
        
        # Return public URL
        public_url = f"{LOCAL_STORAGE_URL_PREFIX}/{file_path}/{unique_filename}"
        logger.info(f"File uploaded successfully: {public_url}")
        return public_url
        
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        return None

def upload_resume(user_id: int, content: bytes, filename: str) -> Optional[str]:
    """Upload user resume"""
    return upload_file(content, f"resumes/{user_id}", filename)

def upload_company_logo(user_id: int, content: bytes, filename: str) -> Optional[str]:
    """Upload company logo"""
    return upload_file(content, f"company_logos/{user_id}", filename)

def upload_job_document(user_id: int, job_id: int, content: bytes, filename: str) -> Optional[str]:
    """Upload job document"""
    return upload_file(content, f"job_docs/{user_id}/{job_id}", filename)

def upload_visa_document(user_id: int, document_type: str, content: bytes, filename: str) -> Optional[str]:
    """Upload visa document"""
    return upload_file(content, f"visa_documents/{user_id}/{document_type}", filename)

def delete_file(file_url: str) -> bool:
    """
    Delete file from local storage
    
    Args:
        file_url: Public URL or relative path to the file
    
    Returns:
        True if file was deleted successfully, False otherwise
    """
    try:
        # Extract relative path from URL
        if file_url.startswith(LOCAL_STORAGE_URL_PREFIX):
            relative_path = file_url[len(LOCAL_STORAGE_URL_PREFIX):].lstrip('/')
        else:
            relative_path = file_url.lstrip('/')
        
        # Full file path
        full_path = Path(LOCAL_STORAGE_BASE_PATH, relative_path)
        
        if full_path.exists() and full_path.is_file():
            full_path.unlink()
            logger.info(f"File deleted: {file_url}")
            return True
        else:
            logger.warning(f"File not found for deletion: {file_url}")
            return False
            
    except Exception as e:
        logger.error(f"File deletion failed: {e}")
        return False

def get_file_info(file_url: str) -> Optional[dict]:
    """
    Get file information
    
    Args:
        file_url: Public URL or relative path to the file
    
    Returns:
        Dictionary with file info or None if file doesn't exist
    """
    try:
        # Extract relative path from URL
        if file_url.startswith(LOCAL_STORAGE_URL_PREFIX):
            relative_path = file_url[len(LOCAL_STORAGE_URL_PREFIX):].lstrip('/')
        else:
            relative_path = file_url.lstrip('/')
        
        # Full file path
        full_path = Path(LOCAL_STORAGE_BASE_PATH, relative_path)
        
        if full_path.exists() and full_path.is_file():
            stat = full_path.stat()
            mime_type, _ = mimetypes.guess_type(str(full_path))
            
            return {
                "name": full_path.name,
                "size": stat.st_size,
                "mime_type": mime_type,
                "created_at": stat.st_ctime,
                "modified_at": stat.st_mtime,
                "path": str(relative_path)
            }
        return None
        
    except Exception as e:
        logger.error(f"Failed to get file info: {e}")
        return None

def resolve_storage_url(value: Optional[str]) -> Optional[str]:
    """
    Resolve storage URL - compatibility function for Supabase replacement
    For local storage, URLs are already in the correct format
    """
    return value

def local_storage_configured() -> bool:
    """Check if local storage is properly configured"""
    try:
        ensure_storage_directory()
        return True
    except Exception as e:
        logger.error(f"Local storage configuration failed: {e}")
        return False

# Initialize storage on import
ensure_storage_directory()
