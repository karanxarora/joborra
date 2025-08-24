from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for development if PostgreSQL not available
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./joborra.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=os.getenv("DEBUG", "False").lower() == "true"
    )
else:
    # For Postgres (e.g., Supabase), use default pooling and require SSL
    # Ensure your DATABASE_URL includes credentials and host, optionally with `?sslmode=require`.
    # We also pass sslmode via connect_args for safety.
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        connect_args={"sslmode": "require"},
        echo=os.getenv("DEBUG", "False").lower() == "true"
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
