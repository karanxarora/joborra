from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Always use SQLite for both development and production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./joborra.db")

# Force SQLite if any PostgreSQL URL is provided
if not DATABASE_URL.startswith("sqlite"):
    logger.info(f"Converting non-SQLite DATABASE_URL to SQLite for consistency")
    DATABASE_URL = "sqlite:///./joborra.db"

logger.info(f"Using SQLite database: {DATABASE_URL}")

# SQLite configuration optimized for production use
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 20,
    },
    poolclass=StaticPool,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("DEBUG", "False").lower() == "true"
)

# Configure SQLite pragmas after engine creation
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance and concurrency"""
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys=ON")
        # Use WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        # Balance between safety and performance
        cursor.execute("PRAGMA synchronous=NORMAL")
        # 64MB cache
        cursor.execute("PRAGMA cache_size=-64000")
        # Store temp tables in memory
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        try:
            db.close()
        except Exception as e:
            logger.error(f"Error closing database session: {e}")

def get_db_with_retry():
    """Get database session with retry logic for connection issues"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            # Test the connection
            db.execute("SELECT 1")
            return db
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(0.1 * (attempt + 1))  # Exponential backoff
            else:
                logger.error(f"All database connection attempts failed")
                raise
