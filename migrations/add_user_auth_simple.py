"""
Simple migration to add user authentication tables
"""

import sqlite3
import os
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def run_migration():
    """Create authentication tables using direct SQL"""
    db_path = "joborra.db"
    
    print("Creating authentication tables...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(100) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'student',
                is_active BOOLEAN DEFAULT 1,
                is_verified BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                
                -- Student fields
                university VARCHAR(255),
                degree VARCHAR(255),
                graduation_year INTEGER,
                visa_status VARCHAR(100),
                
                -- Employer fields
                company_name VARCHAR(255),
                company_website VARCHAR(255),
                company_size VARCHAR(100),
                industry VARCHAR(255)
            )
        """)
        
        # Create job_favorites table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (job_id) REFERENCES jobs (id),
                UNIQUE(user_id, job_id)
            )
        """)
        
        # Create job_applications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                status VARCHAR(50) DEFAULT 'applied',
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                cover_letter TEXT,
                resume_url VARCHAR(500),
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (job_id) REFERENCES jobs (id)
            )
        """)
        
        # Create user_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                expires_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                user_agent VARCHAR(500),
                ip_address VARCHAR(45),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Add new columns to jobs table for user-posted jobs
        try:
            cursor.execute("ALTER TABLE jobs ADD COLUMN posted_by_user_id INTEGER")
            cursor.execute("ALTER TABLE jobs ADD COLUMN is_joborra_job BOOLEAN DEFAULT 0")
            print("✓ Added user posting columns to jobs table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✓ User posting columns already exist in jobs table")
            else:
                raise
        
        # Create demo users
        admin_password = pwd_context.hash("admin123")
        student_password = pwd_context.hash("student123")
        employer_password = pwd_context.hash("employer123")
        
        # Insert demo users if they don't exist
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", ("admin@joborra.com",))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO users (email, username, hashed_password, full_name, role, is_verified)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("admin@joborra.com", "admin", admin_password, "Admin User", "admin", 1))
            print("✓ Created admin user (admin@joborra.com / admin123)")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", ("student@example.com",))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO users (email, username, hashed_password, full_name, role, is_verified, 
                                 university, degree, graduation_year, visa_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("student@example.com", "student_demo", student_password, "Demo Student", "student", 1,
                  "University of Sydney", "Computer Science", 2024, "student_visa"))
            print("✓ Created demo student (student@example.com / student123)")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", ("employer@example.com",))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO users (email, username, hashed_password, full_name, role, is_verified,
                                 company_name, company_website, company_size, industry)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("employer@example.com", "employer_demo", employer_password, "Demo Employer", "employer", 1,
                  "Tech Startup Pty Ltd", "https://techstartup.com.au", "small", "Technology"))
            print("✓ Created demo employer (employer@example.com / employer123)")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Migration completed successfully!")
        print("\nDemo accounts created:")
        print("  Admin: admin@joborra.com / admin123")
        print("  Student: student@example.com / student123") 
        print("  Employer: employer@example.com / employer123")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration()
