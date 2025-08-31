from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Require Supabase PostgreSQL connection
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Please set it to your Supabase PostgreSQL connection string. "
        "Example: postgresql://postgres:[password]@[host]:5432/postgres?sslmode=require"
    )

if not DATABASE_URL.startswith("postgresql://"):
    raise ValueError(
        "DATABASE_URL must be a PostgreSQL connection string for Supabase. "
        f"Current value: {DATABASE_URL[:20]}..."
    )

# Create Supabase PostgreSQL engine with SSL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"},
    echo=os.getenv("DEBUG", "False").lower() == "true",
    pool_size=10,
    max_overflow=20
)

logger.info("Connected to Supabase PostgreSQL database")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
