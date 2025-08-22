#!/usr/bin/env python3
"""
Reset database and apply new ATS schema
"""

import os
import logging
from sqlalchemy import create_engine, text
from app.database import Base, get_db
from app.models import Company, Job, VisaKeyword, ScrapingLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_database():
    """Reset database and recreate with new schema"""
    
    # Remove existing database file
    db_file = "joborra.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        logger.info(f"Removed existing database: {db_file}")
    
    # Create new database with updated schema
    engine = create_engine('sqlite:///./joborra.db')
    Base.metadata.create_all(bind=engine)
    logger.info("Created new database with updated schema")
    
    # Initialize with visa keywords
    db = next(get_db())
    try:
        # Add positive visa keywords
        positive_keywords = [
            ('international students', 'positive', 2.0, 'visa_types'),
            ('student visa', 'positive', 2.0, 'visa_types'),
            ('graduate visa', 'positive', 2.0, 'visa_types'),
            ('485 visa', 'positive', 2.0, 'visa_types'),
            ('500 visa', 'positive', 2.0, 'visa_types'),
            ('subclass 485', 'positive', 2.0, 'visa_types'),
            ('subclass 500', 'positive', 2.0, 'visa_types'),
            ('subclass 482', 'positive', 2.0, 'visa_types'),
            ('482 visa', 'positive', 2.0, 'visa_types'),
            ('TSS visa', 'positive', 2.0, 'visa_types'),
            ('sponsorship', 'positive', 2.0, 'visa_types'),
            ('visa sponsorship', 'positive', 2.0, 'visa_types'),
            ('employer sponsorship', 'positive', 2.0, 'visa_types'),
            ('work rights', 'positive', 1.5, 'visa_types'),
            ('full working rights', 'positive', 1.5, 'visa_types'),
            ('valid visa', 'positive', 1.5, 'visa_types'),
            ('eligible to work in Australia', 'positive', 1.8, 'openness'),
            ('work permit', 'positive', 1.5, 'visa_types'),
            ('internship', 'positive', 1.5, 'programs'),
            ('graduate program', 'positive', 1.5, 'programs'),
            ('graduate role', 'positive', 1.5, 'programs'),
            ('trainee program', 'positive', 1.5, 'programs'),
            ('cadetship', 'positive', 1.5, 'programs'),
            ('welcome international', 'positive', 1.8, 'openness'),
            ('open to candidates requiring sponsorship', 'positive', 1.8, 'openness'),
            ('overseas applicants welcome', 'positive', 1.8, 'openness'),
            ('visa support', 'positive', 1.8, 'openness'),
            ('support for relocation', 'positive', 1.8, 'openness')
        ]
        
        # Add negative keywords
        negative_keywords = [
            ('Australian citizen only', 'negative', 3.0, 'citizenship'),
            ('must be an Australian citizen', 'negative', 3.0, 'citizenship'),
            ('Australian citizenship required', 'negative', 3.0, 'citizenship'),
            ('must be PR', 'negative', 3.0, 'citizenship'),
            ('permanent resident only', 'negative', 3.0, 'citizenship'),
            ('security clearance required', 'negative', 2.5, 'clearance'),
            ('baseline clearance', 'negative', 2.5, 'clearance'),
            ('NV1 clearance', 'negative', 2.5, 'clearance'),
            ('NV2 clearance', 'negative', 2.5, 'clearance')
        ]
        
        # Insert keywords
        for keyword, ktype, weight, category in positive_keywords + negative_keywords:
            visa_keyword = VisaKeyword(
                keyword=keyword,
                keyword_type=ktype,
                weight=weight,
                category=category
            )
            db.add(visa_keyword)
        
        db.commit()
        logger.info(f"Added {len(positive_keywords + negative_keywords)} visa keywords")
        
    except Exception as e:
        logger.error(f"Error initializing keywords: {e}")
        db.rollback()
    finally:
        db.close()
    
    logger.info("Database reset completed successfully")

if __name__ == "__main__":
    reset_database()
