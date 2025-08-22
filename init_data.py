#!/usr/bin/env python3
"""
Initialize database with default visa keywords and sample data
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, VisaKeyword
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_visa_keywords(db: Session):
    """Initialize default visa keywords"""
    
    # Check if keywords already exist
    existing_count = db.query(VisaKeyword).count()
    if existing_count > 0:
        logger.info(f"Visa keywords already exist ({existing_count} found). Skipping initialization.")
        return
    
    default_keywords = [
        # Positive sponsorship indicators
        {'keyword': 'visa sponsorship', 'keyword_type': 'positive', 'weight': 3.0, 'category': 'sponsorship'},
        {'keyword': 'sponsor visa', 'keyword_type': 'positive', 'weight': 3.0, 'category': 'sponsorship'},
        {'keyword': '482 visa', 'keyword_type': 'positive', 'weight': 2.5, 'category': 'sponsorship'},
        {'keyword': '186 visa', 'keyword_type': 'positive', 'weight': 2.5, 'category': 'sponsorship'},
        {'keyword': '187 visa', 'keyword_type': 'positive', 'weight': 2.5, 'category': 'sponsorship'},
        {'keyword': 'temporary skill shortage', 'keyword_type': 'positive', 'weight': 2.5, 'category': 'sponsorship'},
        {'keyword': 'tss visa', 'keyword_type': 'positive', 'weight': 2.5, 'category': 'sponsorship'},
        {'keyword': 'employer nomination', 'keyword_type': 'positive', 'weight': 2.0, 'category': 'sponsorship'},
        {'keyword': 'skilled migration', 'keyword_type': 'positive', 'weight': 2.0, 'category': 'sponsorship'},
        {'keyword': 'work visa', 'keyword_type': 'positive', 'weight': 1.5, 'category': 'sponsorship'},
        {'keyword': 'international candidates', 'keyword_type': 'positive', 'weight': 2.0, 'category': 'sponsorship'},
        {'keyword': 'overseas applicants', 'keyword_type': 'positive', 'weight': 2.0, 'category': 'sponsorship'},
        {'keyword': 'global talent', 'keyword_type': 'positive', 'weight': 1.8, 'category': 'sponsorship'},
        {'keyword': 'relocation assistance', 'keyword_type': 'positive', 'weight': 1.5, 'category': 'sponsorship'},
        
        # Negative sponsorship indicators
        {'keyword': 'australian citizens only', 'keyword_type': 'negative', 'weight': -3.0, 'category': 'sponsorship'},
        {'keyword': 'pr holders only', 'keyword_type': 'negative', 'weight': -3.0, 'category': 'sponsorship'},
        {'keyword': 'permanent residents only', 'keyword_type': 'negative', 'weight': -3.0, 'category': 'sponsorship'},
        {'keyword': 'no visa sponsorship', 'keyword_type': 'negative', 'weight': -3.0, 'category': 'sponsorship'},
        {'keyword': 'citizenship required', 'keyword_type': 'negative', 'weight': -2.5, 'category': 'sponsorship'},
        {'keyword': 'security clearance', 'keyword_type': 'negative', 'weight': -2.0, 'category': 'sponsorship'},
        {'keyword': 'must be eligible to work', 'keyword_type': 'negative', 'weight': -1.0, 'category': 'sponsorship'},
        
        # Student-friendly indicators
        {'keyword': 'graduate program', 'keyword_type': 'positive', 'weight': 3.0, 'category': 'student_friendly'},
        {'keyword': 'graduate opportunity', 'keyword_type': 'positive', 'weight': 2.5, 'category': 'student_friendly'},
        {'keyword': 'entry level', 'keyword_type': 'positive', 'weight': 2.0, 'category': 'student_friendly'},
        {'keyword': 'junior', 'keyword_type': 'positive', 'weight': 2.0, 'category': 'student_friendly'},
        {'keyword': 'internship', 'keyword_type': 'positive', 'weight': 2.5, 'category': 'student_friendly'},
        {'keyword': 'trainee', 'keyword_type': 'positive', 'weight': 2.0, 'category': 'student_friendly'},
        {'keyword': 'recent graduate', 'keyword_type': 'positive', 'weight': 2.5, 'category': 'student_friendly'},
        {'keyword': 'new graduate', 'keyword_type': 'positive', 'weight': 2.5, 'category': 'student_friendly'},
        {'keyword': 'student', 'keyword_type': 'positive', 'weight': 1.5, 'category': 'student_friendly'},
        {'keyword': 'mentorship', 'keyword_type': 'positive', 'weight': 1.0, 'category': 'student_friendly'},
        {'keyword': 'training provided', 'keyword_type': 'positive', 'weight': 1.5, 'category': 'student_friendly'},
        
        # Experience level indicators
        {'keyword': '0-2 years', 'keyword_type': 'positive', 'weight': 2.0, 'category': 'experience'},
        {'keyword': '1-3 years', 'keyword_type': 'positive', 'weight': 1.5, 'category': 'experience'},
        {'keyword': 'no experience required', 'keyword_type': 'positive', 'weight': 2.5, 'category': 'experience'},
        {'keyword': 'fresh graduate', 'keyword_type': 'positive', 'weight': 2.0, 'category': 'experience'},
    ]
    
    # Create keyword objects
    keywords_to_add = []
    for kw_data in default_keywords:
        keyword = VisaKeyword(**kw_data)
        keywords_to_add.append(keyword)
    
    # Bulk insert
    db.add_all(keywords_to_add)
    db.commit()
    
    logger.info(f"Initialized {len(keywords_to_add)} visa keywords")

def main():
    """Initialize database with default data"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Initialize data
    db = SessionLocal()
    try:
        init_visa_keywords(db)
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
