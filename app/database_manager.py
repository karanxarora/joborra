"""
Database Manager with Automatic Fallback
=========================================

This module provides a robust database connection manager that:
1. Primarily uses Supabase when configured
2. Only falls back to SQLite on actual connection failures
3. Provides transparent switching between databases
4. Maintains connection health monitoring
"""

import os
import logging
import time
from typing import Optional, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, DatabaseError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections with automatic fallback"""
    
    def __init__(self):
        self.primary_engine = None
        self.fallback_engine = None
        self.primary_session_maker = None
        self.fallback_session_maker = None
        self.using_fallback = False
        self.last_fallback_time = 0
        self.fallback_retry_interval = 300  # 5 minutes
        
        self._setup_engines()
    
    def _setup_engines(self):
        """Setup both primary and fallback database engines"""
        use_supabase = os.getenv("USE_SUPABASE", "false").lower() == "true"
        
        if use_supabase:
            self._setup_supabase_primary()
            self._setup_sqlite_fallback()
        else:
            self._setup_sqlite_primary()
    
    def _setup_supabase_primary(self):
        """Setup Supabase as primary database"""
        try:
            from .database import get_database_config
            
            # Force Supabase configuration
            os.environ["USE_SUPABASE"] = "true"
            config = get_database_config()
            
            if config["type"] == "postgresql":
                self.primary_engine = create_engine(config["url"], **config["engine_config"])
                self.primary_session_maker = sessionmaker(bind=self.primary_engine)
                logger.info("🔵 Primary database: Supabase PostgreSQL")
            else:
                raise ValueError("Expected PostgreSQL configuration for Supabase")
                
        except Exception as e:
            logger.error(f"Failed to setup Supabase primary: {e}")
            self._setup_sqlite_primary()
    
    def _setup_sqlite_fallback(self):
        """Setup SQLite as fallback database"""
        try:
            sqlite_url = "sqlite:///./joborra.db"
            
            if os.path.exists("./joborra.db"):
                self.fallback_engine = create_engine(
                    sqlite_url,
                    connect_args={"check_same_thread": False, "timeout": 20},
                    pool_pre_ping=True,
                    echo=False
                )
                self.fallback_session_maker = sessionmaker(bind=self.fallback_engine)
                logger.info("🟡 Fallback database: SQLite (preserved)")
            else:
                logger.warning("⚠️ SQLite database not found - no fallback available")
                
        except Exception as e:
            logger.error(f"Failed to setup SQLite fallback: {e}")
    
    def _setup_sqlite_primary(self):
        """Setup SQLite as primary database"""
        try:
            from .database import get_database_config
            
            # Force SQLite configuration
            os.environ["USE_SUPABASE"] = "false"
            config = get_database_config()
            
            self.primary_engine = create_engine(config["url"], **config["engine_config"])
            self.primary_session_maker = sessionmaker(bind=self.primary_engine)
            logger.info("🟢 Primary database: SQLite")
            
        except Exception as e:
            logger.error(f"Failed to setup SQLite primary: {e}")
            raise
    
    def _test_connection(self, engine) -> bool:
        """Test if a database connection is working"""
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    
    def _should_retry_primary(self) -> bool:
        """Check if we should retry the primary database"""
        if not self.using_fallback:
            return False
        
        current_time = time.time()
        return (current_time - self.last_fallback_time) > self.fallback_retry_interval
    
    def get_session_maker(self):
        """Get appropriate session maker with automatic fallback logic"""
        # If using fallback, check if we should retry primary
        if self.using_fallback and self._should_retry_primary():
            if self.primary_engine and self._test_connection(self.primary_engine):
                logger.info("✅ Primary database recovered, switching back")
                self.using_fallback = False
                return self.primary_session_maker
        
        # Try primary first
        if not self.using_fallback and self.primary_engine:
            if self._test_connection(self.primary_engine):
                return self.primary_session_maker
            else:
                # Primary failed, switch to fallback
                logger.warning("⚠️ Primary database failed, switching to fallback")
                self.using_fallback = True
                self.last_fallback_time = time.time()
        
        # Use fallback if available
        if self.fallback_engine and self._test_connection(self.fallback_engine):
            if not self.using_fallback:
                logger.info("🔄 Using fallback database")
            return self.fallback_session_maker
        
        # If we get here, both databases are down
        logger.error("❌ Both primary and fallback databases are unavailable")
        raise DatabaseError("No available database connections")
    
    @contextmanager
    def get_session(self):
        """Get database session with automatic fallback"""
        session_maker = self.get_session_maker()
        session = session_maker()
        
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            
            # If this was a connection error and we have a fallback, try it
            if isinstance(e, (OperationalError, DatabaseError)) and not self.using_fallback:
                logger.warning(f"Database error: {e}, attempting fallback")
                session.close()
                
                # Try fallback
                try:
                    self.using_fallback = True
                    self.last_fallback_time = time.time()
                    fallback_session_maker = self.get_session_maker()
                    session = fallback_session_maker()
                    yield session
                    session.commit()
                except Exception as fallback_error:
                    session.rollback()
                    logger.error(f"Fallback also failed: {fallback_error}")
                    raise fallback_error
            else:
                raise e
        finally:
            session.close()
    
    def get_current_database_info(self) -> dict:
        """Get information about the current database configuration"""
        return {
            "using_fallback": self.using_fallback,
            "primary_available": self.primary_engine is not None and self._test_connection(self.primary_engine),
            "fallback_available": self.fallback_engine is not None and self._test_connection(self.fallback_engine),
            "primary_type": "Supabase" if os.getenv("USE_SUPABASE", "false").lower() == "true" else "SQLite",
            "fallback_type": "SQLite" if self.fallback_engine else None
        }

# Global database manager instance
db_manager = DatabaseManager()

# Convenience function for getting sessions
def get_managed_db():
    """Get managed database session"""
    return db_manager.get_session()

# Backward compatibility
def get_db():
    """Backward compatible database session getter"""
    with get_managed_db() as session:
        yield session
