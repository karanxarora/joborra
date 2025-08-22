"""
Add enhanced profile fields and job view tracking
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Add enhanced profile fields and job view tracking tables"""
    try:
        conn = sqlite3.connect('joborra.db')
        cursor = conn.cursor()
        
        logger.info("Adding enhanced profile fields to users table...")
        
        # Enhanced student profile fields
        student_fields = [
            "ALTER TABLE users ADD COLUMN skills TEXT",
            "ALTER TABLE users ADD COLUMN experience_level VARCHAR(50)",
            "ALTER TABLE users ADD COLUMN preferred_locations TEXT",
            "ALTER TABLE users ADD COLUMN salary_expectations_min INTEGER",
            "ALTER TABLE users ADD COLUMN salary_expectations_max INTEGER", 
            "ALTER TABLE users ADD COLUMN work_authorization VARCHAR(100)",
            "ALTER TABLE users ADD COLUMN linkedin_profile VARCHAR(500)",
            "ALTER TABLE users ADD COLUMN github_profile VARCHAR(500)",
            "ALTER TABLE users ADD COLUMN portfolio_url VARCHAR(500)",
            "ALTER TABLE users ADD COLUMN bio TEXT"
        ]
        
        # Enhanced employer profile fields
        employer_fields = [
            "ALTER TABLE users ADD COLUMN company_description TEXT",
            "ALTER TABLE users ADD COLUMN company_logo_url VARCHAR(500)",
            "ALTER TABLE users ADD COLUMN company_location VARCHAR(255)",
            "ALTER TABLE users ADD COLUMN hiring_manager_name VARCHAR(255)",
            "ALTER TABLE users ADD COLUMN hiring_manager_title VARCHAR(255)",
            "ALTER TABLE users ADD COLUMN company_benefits TEXT",
            "ALTER TABLE users ADD COLUMN company_culture TEXT"
        ]
        
        # Add all new fields
        for field_sql in student_fields + employer_fields:
            try:
                cursor.execute(field_sql)
                logger.info(f"Added field: {field_sql.split()[-2]}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    logger.info(f"Field already exists: {field_sql.split()[-2]}")
                else:
                    raise e
        
        # Create job_views table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                user_id INTEGER,
                viewed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                user_agent VARCHAR(500),
                referrer VARCHAR(500),
                session_id VARCHAR(255),
                FOREIGN KEY (job_id) REFERENCES jobs (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        logger.info("Created job_views table")
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_views_job_id ON job_views(job_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_views_user_id ON job_views(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_views_viewed_at ON job_views(viewed_at)")
        logger.info("Created indexes for job_views table")
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Profile fields migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("✅ Migration completed successfully")
    else:
        print("❌ Migration failed")
        exit(1)
