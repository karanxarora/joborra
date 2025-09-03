import os
import logging
from typing import Optional
from supabase import create_client, Client
import uuid
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Supabase configuration - load dynamically to ensure .env is loaded
def _get_supabase_url() -> Optional[str]:
    return os.getenv("SUPABASE_URL")

def _get_supabase_key() -> Optional[str]:
    return os.getenv("SUPABASE_ANON_KEY")

def _get_supabase_service_key() -> Optional[str]:
    return os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE")

def supabase_configured() -> bool:
    """Check if Supabase is properly configured."""
    return bool(_get_supabase_url() and _get_supabase_service_key())

def get_supabase_client() -> Optional[Client]:
    """Get Supabase client if configured."""
    if not supabase_configured():
        return None
    
    try:
        # Use explicit parameter names to avoid proxy argument issues
        return create_client(
            supabase_url=_get_supabase_url(),
            supabase_key=_get_supabase_service_key()
        )
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        return None

async def upload_resume(user_id: int, content: bytes, filename: str) -> Optional[str]:
    """Upload resume to Supabase storage using master bucket."""
    if not supabase_configured():
        logger.warning("Supabase not configured, cannot upload resume")
        return None
    
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        # Generate unique filename
        file_ext = filename.split('.')[-1] if '.' in filename else 'pdf'
        unique_filename = f"resumes/resume_{user_id}_{uuid.uuid4()}.{file_ext}"
        
        # Upload to master bucket with resumes/ prefix
        result = client.storage.from_("master").upload(
            unique_filename,
            content,
            file_options={"content-type": "application/pdf"}
        )
        
        # Handle the result properly
        if hasattr(result, 'error') and result.error:
            logger.error(f"Failed to upload resume: {result.error}")
            return None
        
        # Return the storage path (not the public URL)
        return f"/master/{unique_filename}"
        
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        return None

async def upload_company_logo(user_id: int, content: bytes, filename: str) -> Optional[str]:
    """Upload company logo to Supabase storage using master bucket."""
    if not supabase_configured():
        logger.warning("Supabase not configured, cannot upload company logo")
        return None
    
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        # Generate unique filename
        file_ext = filename.split('.')[-1] if '.' in filename else 'png'
        unique_filename = f"company-logos/logo_{user_id}_{uuid.uuid4()}.{file_ext}"
        
        # Upload to master bucket with company-logos/ prefix
        result = client.storage.from_("master").upload(
            unique_filename,
            content,
            file_options={"content-type": f"image/{file_ext}"}
        )
        
        # Handle the result properly
        if hasattr(result, 'error') and result.error:
            logger.error(f"Failed to upload company logo: {result.error}")
            return None
        
        # Return the storage path (not the public URL)
        return f"/master/{unique_filename}"
        
    except Exception as e:
        logger.error(f"Error uploading company logo: {e}")
        return None

async def upload_job_document(user_id: int, job_id: int, content: bytes, filename: str) -> Optional[str]:
    """Upload job document to Supabase storage using master bucket."""
    if not supabase_configured():
        logger.warning("Supabase not configured, cannot upload job document")
        return None
    
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        # Generate unique filename
        file_ext = filename.split('.')[-1] if '.' in filename else 'pdf'
        unique_filename = f"job-documents/job_{job_id}_{user_id}_{uuid.uuid4()}.{file_ext}"
        
        # Upload to master bucket with job-documents/ prefix
        result = client.storage.from_("master").upload(
            unique_filename,
            content,
            file_options={"content-type": "application/pdf"}
        )
        
        # Handle the result properly
        if hasattr(result, 'error') and result.error:
            logger.error(f"Failed to upload job document: {result.error}")
            return None
        
        # Return the storage path (not the public URL)
        return f"/master/{unique_filename}"
        
    except Exception as e:
        logger.error(f"Error uploading job document: {e}")
        return None

async def upload_visa_document(user_id: int, document_type: str, content: bytes, filename: str) -> Optional[str]:
    """Upload visa document to Supabase storage using master bucket."""
    if not supabase_configured():
        logger.warning("Supabase not configured, cannot upload visa document")
        return None
    
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        # Generate unique filename
        file_ext = filename.split('.')[-1] if '.' in filename else 'pdf'
        unique_filename = f"visa-documents/{document_type}_{user_id}_{uuid.uuid4()}.{file_ext}"
        
        # Upload to master bucket with visa-documents/ prefix
        result = client.storage.from_("master").upload(
            unique_filename,
            content,
            file_options={"content-type": "application/pdf"}
        )
        
        # Handle the result properly
        if hasattr(result, 'error') and result.error:
            logger.error(f"Failed to upload visa document: {result.error}")
            return None
        
        # Return the storage path (not the public URL)
        return f"/master/{unique_filename}"
        
    except Exception as e:
        logger.error(f"Error uploading visa document: {e}")
        return None

def resolve_storage_url(storage_path: Optional[str]) -> Optional[str]:
    """Resolves a storage path to a full URL using master bucket."""
    if not storage_path:
        return None
    
    # If it's already a full URL, return as is
    if storage_path.startswith('http'):
        return storage_path
    
    # If it's a Supabase storage path, construct the full URL from master bucket
    if supabase_configured():
        client = get_supabase_client()
        if client:
            # Extract file path from storage_path
            # Format: /master/path/to/file
            if storage_path.startswith('/master/'):
                file_path = storage_path[8:]  # Remove '/master/' prefix
                return client.storage.from_("master").get_public_url(file_path)
    
    return storage_path
