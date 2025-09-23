from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.session_middleware import SessionMiddleware
from app.database import engine, Base
from sqlalchemy import text
import logging
import os

# Import all models to ensure they're registered with SQLAlchemy
from app.models import JobDraft  # noqa: F401

# Configure logging EARLY so helpers can use logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

# SQLite schema compatibility: ensure new columns exist when models are updated without migrations
def ensure_schema_compatibility():
    # Simplified schema compatibility for SQLite only
    try:
        with engine.begin() as conn:
            # Fetch existing columns for users table
            result = conn.execute(text("PRAGMA table_info(users);"))
            columns = [row[1] for row in result.fetchall()]  # row format: (cid, name, type, ...)
            logger.info(f"Schema compat: SQLite users columns found={len(columns)}")
            logger.info(f"Schema compat: users.education present? {'education' in columns}, users.experience present? {'experience' in columns}")
            
            # Common columns (resume + company_logo + contact_number + vevo_document)
            if 'resume_url' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN resume_url VARCHAR(500)"))
                logger.info("Added missing column users.resume_url for compatibility")
            if 'contact_number' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN contact_number VARCHAR(20)"))
                logger.info("Added missing column users.contact_number for compatibility")
            if 'company_logo_url' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN company_logo_url VARCHAR(500)"))
                logger.info("Added missing column users.company_logo_url for compatibility")
            if 'vevo_document_url' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN vevo_document_url VARCHAR(500)"))
                logger.info("Added missing column users.vevo_document_url for compatibility")
            # OAuth columns for Google Sign-In
            if 'oauth_provider' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(50)"))
                logger.info("Added missing column users.oauth_provider for compatibility")
            if 'oauth_sub' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN oauth_sub VARCHAR(255)"))
                logger.info("Added missing column users.oauth_sub for compatibility")

            # Education & Experience JSON text columns for student profiles
            if 'education' not in columns:
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN education TEXT"))
                    logger.info("Added missing column users.education for compatibility")
                except Exception as ce:
                    logger.warning(f"Could not add column users.education: {ce}")
            if 'experience' not in columns:
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN experience TEXT"))
                    logger.info("Added missing column users.experience for compatibility")
                except Exception as ce:
                    logger.warning(f"Could not add column users.experience: {ce}")

            # Ensure enhanced employer profile columns exist on users table
            employer_cols = [
                ("company_description", "TEXT"),
                ("company_location", "VARCHAR(255)"),
                ("hiring_manager_name", "VARCHAR(255)"),
                ("hiring_manager_title", "VARCHAR(255)"),
                ("company_benefits", "TEXT"),
                ("company_culture", "TEXT"),
                # Basic employer fields (in case older schemas missed them)
                ("company_name", "VARCHAR(255)"),
                ("company_website", "VARCHAR(255)"),
                ("company_size", "VARCHAR(100)"),
                ("industry", "VARCHAR(255)")
            ]
            for col_name, col_type in employer_cols:
                if col_name not in columns:
                    try:
                        conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                        logger.info(f"Added missing column users.{col_name} for compatibility")
                    except Exception as ce:
                        logger.warning(f"Could not add column users.{col_name}: {ce}")

            # Ensure new employer posting fields on jobs table
            result_jobs = conn.execute(text("PRAGMA table_info(jobs);"))
            job_cols = [row[1] for row in result_jobs.fetchall()]
            to_add = []
            if 'salary' not in job_cols:
                to_add.append("ADD COLUMN salary VARCHAR(255)")
            if 'job_type' not in job_cols:
                to_add.append("ADD COLUMN job_type VARCHAR(100)")
            # Correct column name is visa_types (TEXT JSON), not visa_type
            if 'visa_types' not in job_cols:
                to_add.append("ADD COLUMN visa_types TEXT")
            if 'job_document_url' not in job_cols:
                to_add.append("ADD COLUMN job_document_url VARCHAR(500)")
            for clause in to_add:
                conn.execute(text(f"ALTER TABLE jobs {clause}"))
                logger.info(f"Added missing column on jobs: {clause}")

            # Create helpful indexes for filtering/search
            try:
                result_idx = conn.execute(text("PRAGMA index_list('jobs');"))
                existing_indexes = {row[1] for row in result_idx.fetchall()}  # row: (seq, name, unique, origin, partial)

                desired_indexes = {
                    "idx_jobs_employment_type": "CREATE INDEX IF NOT EXISTS idx_jobs_employment_type ON jobs(employment_type)",
                    "idx_jobs_visa_type": "CREATE INDEX IF NOT EXISTS idx_jobs_visa_type ON jobs(visa_type)",
                    "idx_jobs_remote_option": "CREATE INDEX IF NOT EXISTS idx_jobs_remote_option ON jobs(remote_option)",
                    "idx_jobs_visa_sponsorship": "CREATE INDEX IF NOT EXISTS idx_jobs_visa_sponsorship ON jobs(visa_sponsorship)",
                    "idx_jobs_student_friendly": "CREATE INDEX IF NOT EXISTS idx_jobs_student_friendly ON jobs(international_student_friendly)",
                    "idx_jobs_salary_min": "CREATE INDEX IF NOT EXISTS idx_jobs_salary_min ON jobs(salary_min)",
                    "idx_jobs_salary_max": "CREATE INDEX IF NOT EXISTS idx_jobs_salary_max ON jobs(salary_max)",
                    "idx_jobs_company_id": "CREATE INDEX IF NOT EXISTS idx_jobs_company_id ON jobs(company_id)",
                }

                for idx_name, create_sql in desired_indexes.items():
                    if idx_name not in existing_indexes:
                        conn.execute(text(create_sql))
                        logger.info(f"Created index {idx_name}")

                # Company table indexes
                result_idx_comp = conn.execute(text("PRAGMA index_list('companies');"))
                existing_comp_indexes = {row[1] for row in result_idx_comp.fetchall()}
                if 'idx_companies_industry' not in existing_comp_indexes:
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry)"))
                    logger.info("Created index idx_companies_industry")
            except Exception as ie:
                logger.warning(f"Index creation skipped or failed: {ie}")

    except Exception as e:
        logger.warning(f"Schema compatibility check failed: {e}")

ensure_schema_compatibility()

app = FastAPI(
    title="Joborra - Australian Job Scraping API",
    description="Scalable job scraping service for Australia with visa-friendly filtering",
    version="1.0.0"
)

# Global exception handler for database and other errors
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {exc}")
    # Don't let database errors cause 500s that might log out users
    if "sqlite3" in str(exc) or "database" in str(exc).lower():
        logger.warning(f"Database error handled gracefully: {exc}")
        return {"detail": "Service temporarily unavailable, please try again"}
    # For other errors, let them be handled normally
    raise exc

# Add CORS middleware FIRST so it wraps all responses (including errors and preflight)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        # Render deployed frontend
        "https://joborra-frontend.onrender.com",
        # Production frontend
        "https://joborra.com",
    ],  # React/Vite dev and backend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session management middleware AFTER CORS
app.add_middleware(SessionMiddleware, cleanup_interval_hours=24)

# Include routers
from app.auth_api import router as auth_router
from app.api import router as api_router
from app.visa_api import router as visa_router
from app.ai_api import router as ai_router
from app.session_api import router as session_router

app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(visa_router, prefix="/api/auth")
app.include_router(session_router, prefix="/api/auth")
app.include_router(ai_router, prefix="/api")

# Backward-compatible mounts to support clients calling /auth/* directly
app.include_router(auth_router, prefix="/auth")
app.include_router(visa_router, prefix="/auth")
app.include_router(session_router, prefix="/auth")

# Serve uploaded files
os.makedirs("data", exist_ok=True)
app.mount("/data", StaticFiles(directory="data"), name="data")

# FastAPI backend only - React runs on separate port 3000
@app.get("/")
async def read_root():
    return {"message": "Joborra API Server", "status": "running", "frontend_url": "https://joborra.com"}

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
