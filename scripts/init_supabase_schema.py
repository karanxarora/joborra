#!/usr/bin/env python3
"""
Initialize schema on Supabase Postgres using SQLAlchemy metadata.
Requires DATABASE_URL in environment pointing to Supabase Postgres with sslmode=require.
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Attempt to load .env from project root explicitly
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Ensure local project root is first on sys.path so `import app` resolves to our package
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("init_supabase_schema")


def main():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL not set. Create a .env with DATABASE_URL at project root and try again.")
        sys.exit(1)

    if db_url.startswith("sqlite"): 
        logger.error("DATABASE_URL points to SQLite. Please set it to Supabase Postgres.")
        sys.exit(1)

    # Import engine and Base AFTER env is set so app.database picks it up
    from app.database import engine, Base

    # Import all models to populate metadata
    import app.models  # noqa: F401
    import app.auth_models  # noqa: F401

    logger.info("Creating tables on Supabase...")
    Base.metadata.create_all(bind=engine)
    logger.info("Schema creation complete.")


if __name__ == "__main__":
    main()
