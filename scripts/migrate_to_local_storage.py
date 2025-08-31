#!/usr/bin/env python3
"""
Migration script to move files from any existing remote storage to local storage
This is useful when migrating from Supabase to local file storage
"""

import os
import sys
import logging
import requests
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

from app.database import SessionLocal
from app.models import User, Job
from app.local_storage import ensure_storage_directory, upload_resume, upload_company_logo, upload_job_document

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("migrate_to_local_storage")


def download_file(url: str) -> Optional[bytes]:
    """Download file from URL and return content as bytes"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return None


def migrate_user_files():
    """Migrate user resumes and company logos from remote URLs to local storage"""
    db = SessionLocal()
    migrated_count = 0
    error_count = 0
    
    try:
        # Migrate user resumes
        users_with_resumes = db.query(User).filter(
            User.resume_url.isnot(None),
            User.resume_url.like('http%')  # Only migrate remote URLs
        ).all()
        
        logger.info(f"Found {len(users_with_resumes)} users with remote resume URLs")
        
        for user in users_with_resumes:
            logger.info(f"Migrating resume for user {user.id}: {user.resume_url}")
            
            # Download the file
            content = download_file(user.resume_url)
            if not content:
                error_count += 1
                continue
            
            # Generate a filename
            filename = f"resume_{user.id}.pdf"
            
            # Upload to local storage
            local_url = upload_resume(user.id, content, filename)
            if local_url:
                user.resume_url = local_url
                migrated_count += 1
                logger.info(f"Migrated resume to: {local_url}")
            else:
                error_count += 1
                logger.error(f"Failed to upload resume for user {user.id}")
        
        # Migrate company logos
        users_with_logos = db.query(User).filter(
            User.company_logo_url.isnot(None),
            User.company_logo_url.like('http%')  # Only migrate remote URLs
        ).all()
        
        logger.info(f"Found {len(users_with_logos)} users with remote logo URLs")
        
        for user in users_with_logos:
            logger.info(f"Migrating logo for user {user.id}: {user.company_logo_url}")
            
            # Download the file
            content = download_file(user.company_logo_url)
            if not content:
                error_count += 1
                continue
            
            # Determine file extension from URL
            url_path = user.company_logo_url.split('?')[0]  # Remove query params
            ext = Path(url_path).suffix or '.png'
            filename = f"logo_{user.id}{ext}"
            
            # Upload to local storage
            local_url = upload_company_logo(user.id, content, filename)
            if local_url:
                user.company_logo_url = local_url
                migrated_count += 1
                logger.info(f"Migrated logo to: {local_url}")
            else:
                error_count += 1
                logger.error(f"Failed to upload logo for user {user.id}")
        
        # Migrate job documents
        jobs_with_docs = db.query(Job).filter(
            Job.job_document_url.isnot(None),
            Job.job_document_url.like('http%')  # Only migrate remote URLs
        ).all()
        
        logger.info(f"Found {len(jobs_with_docs)} jobs with remote document URLs")
        
        for job in jobs_with_docs:
            logger.info(f"Migrating document for job {job.id}: {job.job_document_url}")
            
            # Download the file
            content = download_file(job.job_document_url)
            if not content:
                error_count += 1
                continue
            
            # Determine file extension from URL
            url_path = job.job_document_url.split('?')[0]  # Remove query params
            ext = Path(url_path).suffix or '.pdf'
            filename = f"job_doc_{job.id}{ext}"
            
            # Upload to local storage
            local_url = upload_job_document(job.posted_by_user_id or 0, job.id, content, filename)
            if local_url:
                job.job_document_url = local_url
                migrated_count += 1
                logger.info(f"Migrated job document to: {local_url}")
            else:
                error_count += 1
                logger.error(f"Failed to upload document for job {job.id}")
        
        # Commit all changes
        db.commit()
        
        logger.info(f"Migration completed: {migrated_count} files migrated, {error_count} errors")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main migration function"""
    logger.info("Starting migration to local storage...")
    
    # Ensure local storage is set up
    ensure_storage_directory()
    
    # Migrate files
    migrate_user_files()
    
    logger.info("Migration to local storage completed!")


if __name__ == "__main__":
    main()
