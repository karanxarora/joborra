from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool, QueuePool
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def get_database_config():
    """Get database configuration based on environment variables with automatic fallback"""
    
    # Check if we should use Supabase
    use_supabase = os.getenv("USE_SUPABASE", "false").lower() == "true"
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
    migration_mode = os.getenv("MIGRATION_MODE", "false").lower() == "true"
    
    # Use Supabase if explicitly enabled and properly configured
    if use_supabase and supabase_url and supabase_service_key:
        # Use direct PostgreSQL connection string if available, otherwise build one
        postgres_url = os.getenv("SUPABASE_DATABASE_URL")
        
        if not postgres_url:
            # Extract project reference from Supabase URL
            project_ref = supabase_url.replace("https://", "").split(".supabase.co")[0]
            
            # Build PostgreSQL connection URL using pooler for IPv4 compatibility
            postgres_url = f"postgresql://postgres.{project_ref}:{supabase_service_key}@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres?sslmode=require"
        
        logger.info("Using Supabase PostgreSQL database")
        config = {
            "url": postgres_url,
            "engine_config": {
                "poolclass": QueuePool,
                "pool_size": 10,
                "max_overflow": 20,
                "pool_pre_ping": True,
                "pool_recycle": 3600,
                "echo": os.getenv("DEBUG", "False").lower() == "true"
            },
            "type": "postgresql"
        }
        
        # Always return Supabase config when properly configured
        # Fallback will be handled by SQLAlchemy's built-in retry logic
        logger.info("✅ Using Supabase PostgreSQL database (with SQLite fallback on failure)")
        return config
    else:
        # Default to SQLite
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./joborra.db")
        
        # Force SQLite if any PostgreSQL URL is provided but Supabase not enabled
        if not DATABASE_URL.startswith("sqlite"):
            logger.info(f"Converting non-SQLite DATABASE_URL to SQLite for consistency")
            DATABASE_URL = "sqlite:///./joborra.db"
        
        logger.info(f"Using SQLite database: {DATABASE_URL}")
        return {
            "url": DATABASE_URL,
            "engine_config": {
                "connect_args": {
                    "check_same_thread": False,
                    "timeout": 20,
                },
                "poolclass": StaticPool,
                "pool_pre_ping": True,
                "pool_recycle": 300,
                "echo": os.getenv("DEBUG", "False").lower() == "true"
            },
            "type": "sqlite"
        }

# Get database configuration
db_config = get_database_config()
DATABASE_URL = db_config["url"]
DATABASE_TYPE = db_config["type"]

# Create engine with appropriate configuration
engine = create_engine(DATABASE_URL, **db_config["engine_config"])

# Configure SQLite pragmas after engine creation (only for SQLite)
if DATABASE_TYPE == "sqlite":
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Set SQLite pragmas for better performance and concurrency"""
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
    """Get database session - Supabase only, no fallbacks"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
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
