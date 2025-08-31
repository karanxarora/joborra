import os
import logging
from typing import Optional
from supabase import create_client, Client
import uuid

logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def supabase_configured() -> bool:
    """Check if Supabase is properly configured."""
    return bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)

def get_supabase_client() -> Optional[Client]:
    """Get Supabase client if configured."""
    if not supabase_configured():
        return None
    
    try:
        return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        return None

def upload_resume(user_id: int, content: bytes, filename: str) -> Optional[str]:
    """Upload resume to Supabase storage."""
    if not supabase_configured():
        logger.warning("Supabase not configured, cannot upload resume")
        return None
    
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        # Generate unique filename
        file_ext = filename.split('.')[-1] if '.' in filename else 'pdf'
        unique_filename = f"resume_{user_id}_{uuid.uuid4()}.{file_ext}"
        
        # Upload to Supabase storage
        result = client.storage.from_("resumes").upload(
            unique_filename,
            content,
            file_options={"content-type": "application/pdf"}
        )
        
        if result.get("error"):
            logger.error(f"Failed to upload resume: {result['error']}")
            return None
        
        # Return public URL
        return client.storage.from_("resumes").get_public_url(unique_filename)
        
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        return None

def upload_company_logo(user_id: int, content: bytes, filename: str) -> Optional[str]:
    """Upload company logo to Supabase storage."""
    if not supabase_configured():
        logger.warning("Supabase not configured, cannot upload company logo")
        return None
    
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        # Generate unique filename
        file_ext = filename.split('.')[-1] if '.' in filename else 'png'
        unique_filename = f"logo_{user_id}_{uuid.uuid4()}.{file_ext}"
        
        # Upload to Supabase storage
        result = client.storage.from_("company-logos").upload(
            unique_filename,
            content,
            file_options={"content-type": f"image/{file_ext}"}
        )
        
        if result.get("error"):
            logger.error(f"Failed to upload company logo: {result['error']}")
            return None
        
        # Return public URL
        return client.storage.from_("company-logos").get_public_url(unique_filename)
        
    except Exception as e:
        logger.error(f"Error uploading company logo: {e}")
        return None

def upload_job_document(user_id: int, job_id: int, content: bytes, filename: str) -> Optional[str]:
    """Upload job document to Supabase storage."""
    if not supabase_configured():
        logger.warning("Supabase not configured, cannot upload job document")
        return None
    
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        # Generate unique filename
        file_ext = filename.split('.')[-1] if '.' in filename else 'pdf'
        unique_filename = f"job_{job_id}_{user_id}_{uuid.uuid4()}.{file_ext}"
        
        # Upload to Supabase storage
        result = client.storage.from_("job-documents").upload(
            unique_filename,
            content,
            file_options={"content-type": "application/pdf"}
        )
        
        if result.get("error"):
            logger.error(f"Failed to upload job document: {result['error']}")
            return None
        
        # Return public URL
        return client.storage.from_("job-documents").get_public_url(unique_filename)
        
    except Exception as e:
        logger.error(f"Error uploading job document: {e}")
        return None

def upload_visa_document(user_id: int, document_type: str, content: bytes, filename: str) -> Optional[str]:
    """Upload visa document to Supabase storage."""
    if not supabase_configured():
        logger.warning("Supabase not configured, cannot upload visa document")
        return None
    
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        # Generate unique filename
        file_ext = filename.split('.')[-1] if '.' in filename else 'pdf'
        unique_filename = f"{document_type}_{user_id}_{uuid.uuid4()}.{file_ext}"
        
        # Upload to Supabase storage
        result = client.storage.from_("visa-documents").upload(
            unique_filename,
            content,
            file_options={"content-type": "application/pdf"}
        )
        
        if result.get("error"):
            logger.error(f"Failed to upload visa document: {result['error']}")
            return None
        
        # Return public URL
        return client.storage.from_("visa-documents").get_public_url(unique_filename)
        
    except Exception as e:
        logger.error(f"Error uploading visa document: {e}")
        return None

def resolve_storage_url(storage_path: Optional[str]) -> Optional[str]:
    """Resolves a storage path to a full URL."""
    if not storage_path:
        return None
    
    # If it's already a full URL, return as is
    if storage_path.startswith('http'):
        return storage_path
    
    # If it's a Supabase storage path, construct the full URL
    if supabase_configured():
        client = get_supabase_client()
        if client:
            # Extract bucket and file path from storage_path
            # Format: /bucket/path/to/file
            parts = storage_path.strip('/').split('/', 1)
            if len(parts) == 2:
                bucket, file_path = parts
                return client.storage.from_(bucket).get_public_url(file_path)
    
    return storage_path
