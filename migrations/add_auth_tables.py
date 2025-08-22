"""
Database migration to add authentication and user management tables
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add the parent directory to the path so we can import our models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app.auth_models import User, JobFavorite, JobApplication, UserSession

def run_migration():
    """Create all authentication tables"""
    print("Creating authentication tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✓ Authentication tables created successfully")
        
        # Add some sample data for testing
        from sqlalchemy.orm import Session
        from app.auth_models import UserRole
        
        db = Session(bind=engine)
        
        # Check if admin user exists
        admin_user = db.query(User).filter(User.email == "admin@joborra.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@joborra.com",
                username="admin",
                hashed_password=User.hash_password("admin123"),
                full_name="Admin User",
                role=UserRole.ADMIN,
                is_verified=True
            )
            db.add(admin_user)
            print("✓ Created admin user (admin@joborra.com / admin123)")
        
        # Sample student user
        student_user = db.query(User).filter(User.email == "student@example.com").first()
        if not student_user:
            student_user = User(
                email="student@example.com",
                username="student_demo",
                hashed_password=User.hash_password("student123"),
                full_name="Demo Student",
                role=UserRole.STUDENT,
                university="University of Sydney",
                degree="Computer Science",
                graduation_year=2024,
                visa_status="student_visa",
                is_verified=True
            )
            db.add(student_user)
            print("✓ Created demo student (student@example.com / student123)")
        
        # Sample employer user
        employer_user = db.query(User).filter(User.email == "employer@example.com").first()
        if not employer_user:
            employer_user = User(
                email="employer@example.com",
                username="employer_demo",
                hashed_password=User.hash_password("employer123"),
                full_name="Demo Employer",
                role=UserRole.EMPLOYER,
                company_name="Tech Startup Pty Ltd",
                company_website="https://techstartup.com.au",
                company_size="small",
                industry="Technology",
                is_verified=True
            )
            db.add(employer_user)
            print("✓ Created demo employer (employer@example.com / employer123)")
        
        db.commit()
        db.close()
        
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
