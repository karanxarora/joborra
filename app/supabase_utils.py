import os
import logging
from typing import Optional
import requests

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE", "")
SUPABASE_STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "resumes")
SUPABASE_STORAGE_PRIVATE = os.getenv("SUPABASE_STORAGE_PRIVATE", "false").lower() in {"1", "true", "yes"}
SUPABASE_SIGNED_URL_TTL = int(os.getenv("SUPABASE_SIGNED_URL_TTL", "604800"))  # 7 days default


def supabase_configured() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE)


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE}",
        "apikey": SUPABASE_SERVICE_ROLE,
    }


def ensure_bucket(bucket: str) -> None:
    """Ensure a storage bucket exists. If it already exists, ignore errors.
    Requires service role key.
    """
    try:
        # Check buckets
        r = requests.get(f"{SUPABASE_URL}/storage/v1/bucket", headers=_headers(), timeout=10)
        if r.status_code == 200 and any((b.get("name") == bucket) for b in (r.json() or [])):
            return
        # Try to create
        create = requests.post(
            f"{SUPABASE_URL}/storage/v1/bucket",
            headers={**_headers(), "Content-Type": "application/json"},
            json={"name": bucket, "public": not SUPABASE_STORAGE_PRIVATE},
            timeout=10,
        )
        if create.status_code not in (200, 201):
            logger.warning("Supabase: failed to create bucket %s: %s %s", bucket, create.status_code, create.text)
    except Exception as e:
        logger.warning("Supabase: ensure_bucket error: %s", e)


def _sign_url(bucket: str, object_path: str, expires_in: int) -> Optional[str]:
    try:
        r = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/sign/{bucket}/{object_path}",
            headers={**_headers(), "Content-Type": "application/json"},
            json={"expiresIn": expires_in},
            timeout=10,
        )
        if r.status_code in (200, 201):
            signed_path = (r.json() or {}).get("signedURL")
            if signed_path:
                return f"{SUPABASE_URL}{signed_path}"
        logger.error("Supabase sign URL failed: %s %s", r.status_code, r.text)
        return None
    except Exception as e:
        logger.exception("Supabase sign URL error: %s", e)
        return None


def upload_public_object(bucket: str, object_path: str, data: bytes, content_type: str) -> Optional[str]:
    """Upload bytes to Supabase Storage using service role key.
    Returns URL on success (public URL if bucket is public, signed URL if private), else None.
    """
    if not supabase_configured():
        return None
    try:
        ensure_bucket(bucket)
        # Use upsert via x-upsert header
        headers = {**_headers(), "Content-Type": content_type, "x-upsert": "true"}
        url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{object_path}"
        r = requests.put(url, headers=headers, data=data, timeout=30)
        if r.status_code not in (200, 201):
            logger.error("Supabase upload failed: %s %s", r.status_code, r.text)
            return None
        # Determine URL type
        if SUPABASE_STORAGE_PRIVATE:
            # In private mode, return a storage URI so callers can persist it,
            # and use resolver helpers to produce signed URLs for responses.
            return f"storage://{bucket}/{object_path}"
        else:
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{object_path}"
            return public_url
    except Exception as e:
        logger.exception("Supabase upload error: %s", e)
        return None


def resolve_storage_url(value: Optional[str]) -> Optional[str]:
    """If value is a storage:// URI, return a public or signed URL accordingly."""
    if not value:
        return value
    if value.startswith("storage://"):
        try:
            # strip scheme
            path = value[len("storage://"):]
            bucket, object_path = path.split("/", 1)
            if SUPABASE_STORAGE_PRIVATE:
                return _sign_url(bucket, object_path, SUPABASE_SIGNED_URL_TTL)
            else:
                return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{object_path}"
        except Exception:
            logger.exception("Failed to resolve storage URL: %s", value)
            return None
    return value
