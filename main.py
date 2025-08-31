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

# Configure logging EARLY so helpers can use logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

# Supabase PostgreSQL schema compatibility: ensure new columns exist when models are updated without migrations
def ensure_schema_compatibility():
    """Ensure Supabase PostgreSQL schema compatibility"""
    try:
        with engine.begin() as conn:
            # Get current schema
            pg_schema = 'public'
            try:
                row = conn.execute(text("SELECT current_schema()"))
                schema_val = row.fetchone()
                if schema_val and schema_val[0]:
                    pg_schema = schema_val[0]
            except Exception as ce:
                logger.warning(f"Could not determine current schema, defaulting to 'public': {ce}")

            # Fetch existing columns for users table
            result = conn.execute(text(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users' AND table_schema = :schema
                """
            ), {"schema": pg_schema})
            columns = [row[0] for row in result.fetchall()]
            logger.info(f"Supabase schema: users columns found={len(columns)}")
            
            # Add missing columns for users table
            user_columns = [
                ("resume_url", "VARCHAR(500)"),
                ("contact_number", "VARCHAR(20)"),
                ("company_logo_url", "VARCHAR(500)"),
                ("oauth_provider", "VARCHAR(50)"),
                ("oauth_sub", "VARCHAR(255)"),
                ("education", "TEXT"),
                ("experience", "TEXT"),
                ("company_description", "TEXT"),
                ("company_location", "VARCHAR(255)"),
                ("hiring_manager_name", "VARCHAR(255)"),
                ("hiring_manager_title", "VARCHAR(255)"),
                ("company_benefits", "TEXT"),
                ("company_culture", "TEXT"),
                ("company_name", "VARCHAR(255)"),
                ("company_website", "VARCHAR(255)"),
                ("company_size", "VARCHAR(100)"),
                ("industry", "VARCHAR(255)")
            ]
            
            for col_name, col_type in user_columns:
                if col_name not in columns:
                    try:
                        conn.execute(text(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                        logger.info(f"Added missing column users.{col_name}")
                    except Exception as ce:
                        logger.warning(f"Could not add column users.{col_name}: {ce}")

            # Add missing columns for jobs table
            result_jobs = conn.execute(text(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'jobs' AND table_schema = :schema
                """
            ), {"schema": pg_schema})
            job_cols = [row[0] for row in result_jobs.fetchall()]
            
            job_columns = [
                ("salary", "VARCHAR(255)"),
                ("job_type", "VARCHAR(100)"),
                ("visa_type", "VARCHAR(100)"),
                ("job_document_url", "VARCHAR(500)")
            ]
            
            for col_name, col_type in job_columns:
                if col_name not in job_cols:
                    try:
                        conn.execute(text(f"ALTER TABLE jobs ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                        logger.info(f"Added missing column jobs.{col_name}")
                    except Exception as ce:
                        logger.warning(f"Could not add column jobs.{col_name}: {ce}")

            # Create helpful indexes for performance
            try:
                desired_indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_jobs_employment_type ON jobs(employment_type)",
                    "CREATE INDEX IF NOT EXISTS idx_jobs_visa_type ON jobs(visa_type)",
                    "CREATE INDEX IF NOT EXISTS idx_jobs_remote_option ON jobs(remote_option)",
                    "CREATE INDEX IF NOT EXISTS idx_jobs_visa_sponsorship ON jobs(visa_sponsorship)",
                    "CREATE INDEX IF NOT EXISTS idx_jobs_student_friendly ON jobs(international_student_friendly)",
                    "CREATE INDEX IF NOT EXISTS idx_jobs_salary_min ON jobs(salary_min)",
                    "CREATE INDEX IF NOT EXISTS idx_jobs_salary_max ON jobs(salary_max)",
                    "CREATE INDEX IF NOT EXISTS idx_jobs_company_id ON jobs(company_id)",
                    "CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry)"
                ]

                for create_sql in desired_indexes:
                    try:
                        conn.execute(text(create_sql))
                        logger.info(f"Created index: {create_sql.split('idx_')[1].split(' ')[0]}")
                    except Exception as ie:
                        logger.debug(f"Index may already exist: {ie}")
                        
            except Exception as ie:
                logger.warning(f"Index creation failed: {ie}")

    except Exception as e:
        logger.error(f"Supabase schema compatibility check failed: {e}")
        raise

ensure_schema_compatibility()

app = FastAPI(
    title="Joborra - Australian Job Scraping API",
    description="Scalable job scraping service for Australia with visa-friendly filtering",
    version="1.0.0"
)

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
