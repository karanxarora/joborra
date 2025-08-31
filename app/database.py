from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Use SQLite for development if PostgreSQL not available
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./joborra.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=os.getenv("DEBUG", "False").lower() == "true"
    )
else:
    # For Postgres (e.g., Supabase), use default pooling and require SSL
    # Ensure your DATABASE_URL includes credentials and host, optionally with `?sslmode=require`.
    # We also pass sslmode via connect_args for safety.
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20,
        connect_args={"sslmode": "require"},
        echo=os.getenv("DEBUG", "False").lower() == "true"
    )

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
