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

# SQLite compatibility: ensure new columns exist when models are updated without migrations
def ensure_schema_compatibility():
    try:
        with engine.connect() as conn:
            # Check if resume_url exists on users table
            result = conn.execute(text("PRAGMA table_info(users);"))
            columns = [row[1] for row in result.fetchall()]  # row format: (cid, name, type, ...)
            if 'resume_url' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN resume_url VARCHAR(500)"))
                logger.info("Added missing column users.resume_url for compatibility")
            # Check if company_logo_url exists on users table
            if 'company_logo_url' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN company_logo_url VARCHAR(500)"))
                logger.info("Added missing column users.company_logo_url for compatibility")

            # Ensure new employer posting fields on jobs table
            result_jobs = conn.execute(text("PRAGMA table_info(jobs);"))
            job_cols = [row[1] for row in result_jobs.fetchall()]
            to_add = []
            if 'salary' not in job_cols:
                to_add.append("ADD COLUMN salary VARCHAR(255)")
            if 'job_type' not in job_cols:
                to_add.append("ADD COLUMN job_type VARCHAR(100)")
            if 'visa_type' not in job_cols:
                to_add.append("ADD COLUMN visa_type VARCHAR(100)")
            if 'job_document_url' not in job_cols:
                to_add.append("ADD COLUMN job_document_url VARCHAR(500)")
            for clause in to_add:
                conn.execute(text(f"ALTER TABLE jobs {clause}"))
                logger.info(f"Added missing column on jobs: {clause}")

            # Create helpful indexes for filtering/search (SQLite safe)
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
from app.session_api import router as session_router

app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(visa_router, prefix="/api/auth")
app.include_router(session_router, prefix="/api/auth")

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
    return {"message": "Joborra API Server", "status": "running", "frontend_url": "https://joborra-frontend.onrender.com"}

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
