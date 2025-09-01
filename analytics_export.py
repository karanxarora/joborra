#!/usr/bin/env python3
"""
Analytics Export System - Export user data and analytics from SQLite to documents.
"""

import os
import sys
import json
import csv
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from supabase import create_client
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Set environment variables
os.environ["SUPABASE_URL"] = "https://noupavjvuhezvzpqcbqg.supabase.co"
os.environ["SUPABASE_SERVICE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5vdXBhdmp2dWhlenZ6cHFjYnFnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjA0MzU5NywiZXhwIjoyMDcxNjE5NTk3fQ.Qe1YV0aVr-aNdUsP1SlN8qqVpR8ofIBX0d10lT2sS2o"

def get_database_connection():
    """Get database connection."""
    try:
        # Use the same database URL as the main app
        database_url = "sqlite:///./joborra.db"
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal()
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def export_user_analytics(db_session):
    """Export comprehensive user analytics."""
    print("👥 Exporting User Analytics...")
    
    try:
        # Get comprehensive user statistics
        user_stats_query = """
        SELECT 
            role,
            COUNT(*) as total_users,
            COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_users,
            COUNT(CASE WHEN is_verified = 1 THEN 1 END) as verified_users,
            COUNT(CASE WHEN created_at >= date('now', '-30 days') THEN 1 END) as new_users_30d,
            COUNT(CASE WHEN created_at >= date('now', '-7 days') THEN 1 END) as new_users_7d,
            COUNT(CASE WHEN resume_url IS NOT NULL THEN 1 END) as users_with_resume,
            COUNT(CASE WHEN linkedin_profile IS NOT NULL THEN 1 END) as users_with_linkedin,
            COUNT(CASE WHEN github_profile IS NOT NULL THEN 1 END) as users_with_github,
            COUNT(CASE WHEN portfolio_url IS NOT NULL THEN 1 END) as users_with_portfolio,
            COUNT(CASE WHEN contact_number IS NOT NULL THEN 1 END) as users_with_phone,
            COUNT(CASE WHEN university IS NOT NULL THEN 1 END) as users_with_university,
            COUNT(CASE WHEN company_name IS NOT NULL THEN 1 END) as users_with_company,
            AVG(salary_expectations_min) as avg_salary_min,
            AVG(salary_expectations_max) as avg_salary_max
        FROM users 
        GROUP BY role
        """
        
        user_stats = db_session.execute(text(user_stats_query)).fetchall()
        
        # Get user registration trends
        registration_trends_query = """
        SELECT 
            DATE(created_at) as date,
            role,
            COUNT(*) as registrations
        FROM users 
        WHERE created_at >= date('now', '-90 days')
        GROUP BY DATE(created_at), role
        ORDER BY date DESC
        """
        
        registration_trends = db_session.execute(text(registration_trends_query)).fetchall()
        
        # Get comprehensive user details
        user_details_query = """
        SELECT 
            id,
            email,
            username,
            full_name,
            role,
            is_active,
            is_verified,
            created_at,
            updated_at,
            last_login,
            university,
            degree,
            graduation_year,
            visa_status,
            company_name,
            company_website,
            company_size,
            industry,
            skills,
            experience_level,
            preferred_locations,
            salary_expectations_min,
            salary_expectations_max,
            work_authorization,
            linkedin_profile,
            github_profile,
            portfolio_url,
            bio,
            company_description,
            company_logo_url,
            company_location,
            hiring_manager_name,
            hiring_manager_title,
            company_benefits,
            company_culture,
            resume_url,
            course_name,
            institution_name,
            course_start_date,
            course_end_date,
            coe_number,
            contact_number,
            oauth_provider,
            oauth_sub,
            education,
            experience,
            city_suburb,
            date_of_birth,
            company_abn,
            employer_role_title,
            CASE 
                WHEN resume_url IS NOT NULL THEN 1 
                ELSE 0 
            END as has_resume,
            CASE 
                WHEN company_logo_url IS NOT NULL THEN 1 
                ELSE 0 
            END as has_company_logo,
            CASE 
                WHEN linkedin_profile IS NOT NULL THEN 1 
                ELSE 0 
            END as has_linkedin,
            CASE 
                WHEN github_profile IS NOT NULL THEN 1 
                ELSE 0 
            END as has_github,
            CASE 
                WHEN portfolio_url IS NOT NULL THEN 1 
                ELSE 0 
            END as has_portfolio
        FROM users
        ORDER BY created_at DESC
        """
        
        user_details = db_session.execute(text(user_details_query)).fetchall()
        
        # Get university/education statistics
        education_stats_query = """
        SELECT 
            university,
            COUNT(*) as student_count
        FROM users 
        WHERE university IS NOT NULL AND role = 'STUDENT'
        GROUP BY university
        ORDER BY student_count DESC
        LIMIT 20
        """
        
        education_stats = db_session.execute(text(education_stats_query)).fetchall()
        
        # Get skills analysis
        skills_stats_query = """
        SELECT 
            skills,
            COUNT(*) as user_count
        FROM users 
        WHERE skills IS NOT NULL AND skills != ''
        GROUP BY skills
        ORDER BY user_count DESC
        LIMIT 20
        """
        
        skills_stats = db_session.execute(text(skills_stats_query)).fetchall()
        
        # Get location analysis
        location_stats_query = """
        SELECT 
            city_suburb,
            COUNT(*) as user_count
        FROM users 
        WHERE city_suburb IS NOT NULL AND city_suburb != ''
        GROUP BY city_suburb
        ORDER BY user_count DESC
        LIMIT 20
        """
        
        location_stats = db_session.execute(text(location_stats_query)).fetchall()
        
        # Get company analysis
        company_stats_query = """
        SELECT 
            company_name,
            industry,
            company_size,
            COUNT(*) as employee_count
        FROM users 
        WHERE company_name IS NOT NULL AND company_name != '' AND role = 'EMPLOYER'
        GROUP BY company_name, industry, company_size
        ORDER BY employee_count DESC
        LIMIT 20
        """
        
        company_stats = db_session.execute(text(company_stats_query)).fetchall()
        
        return {
            'user_stats': [dict(row._mapping) for row in user_stats],
            'registration_trends': [dict(row._mapping) for row in registration_trends],
            'user_details': [dict(row._mapping) for row in user_details],
            'education_stats': [dict(row._mapping) for row in education_stats],
            'skills_stats': [dict(row._mapping) for row in skills_stats],
            'location_stats': [dict(row._mapping) for row in location_stats],
            'company_stats': [dict(row._mapping) for row in company_stats]
        }
        
    except Exception as e:
        print(f"❌ Error exporting user analytics: {e}")
        return None

def export_job_analytics(db_session):
    """Export job-related analytics."""
    print("💼 Exporting Job Analytics...")
    
    try:
        # Get job statistics
        job_stats_query = """
        SELECT 
            COUNT(*) as total_jobs,
            COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_jobs,
            COUNT(CASE WHEN posted_date >= date('now', '-30 days') THEN 1 END) as new_jobs_30d,
            COUNT(CASE WHEN posted_date >= date('now', '-7 days') THEN 1 END) as new_jobs_7d,
            AVG(salary_min) as avg_salary_min,
            AVG(salary_max) as avg_salary_max,
            COUNT(CASE WHEN job_document_url IS NOT NULL THEN 1 END) as jobs_with_documents
        FROM jobs
        """
        
        job_stats = db_session.execute(text(job_stats_query)).fetchone()
        
        # Get job categories
        job_categories_query = """
        SELECT 
            role_category,
            COUNT(*) as count
        FROM jobs 
        WHERE role_category IS NOT NULL
        GROUP BY role_category
        ORDER BY count DESC
        """
        
        job_categories = db_session.execute(text(job_categories_query)).fetchall()
        
        # Get job locations
        job_locations_query = """
        SELECT 
            state,
            city,
            COUNT(*) as count
        FROM jobs 
        WHERE state IS NOT NULL
        GROUP BY state, city
        ORDER BY count DESC
        LIMIT 20
        """
        
        job_locations = db_session.execute(text(job_locations_query)).fetchall()
        
        return {
            'job_stats': dict(job_stats._mapping) if job_stats else {},
            'job_categories': [dict(row._mapping) for row in job_categories],
            'job_locations': [dict(row._mapping) for row in job_locations]
        }
        
    except Exception as e:
        print(f"❌ Error exporting job analytics: {e}")
        return None

def export_application_analytics(db_session):
    """Export job application analytics."""
    print("📝 Exporting Application Analytics...")
    
    try:
        # Get application statistics
        app_stats_query = """
        SELECT 
            COUNT(*) as total_applications,
            COUNT(CASE WHEN applied_at >= date('now', '-30 days') THEN 1 END) as applications_30d,
            COUNT(CASE WHEN applied_at >= date('now', '-7 days') THEN 1 END) as applications_7d
        FROM job_applications
        """
        
        app_stats = db_session.execute(text(app_stats_query)).fetchone()
        
        # Get application trends
        app_trends_query = """
        SELECT 
            DATE(applied_at) as date,
            COUNT(*) as applications
        FROM job_applications 
        WHERE applied_at >= date('now', '-90 days')
        GROUP BY DATE(applied_at)
        ORDER BY date DESC
        """
        
        app_trends = db_session.execute(text(app_trends_query)).fetchall()
        
        return {
            'application_stats': dict(app_stats._mapping) if app_stats else {},
            'application_trends': [dict(row._mapping) for row in app_trends]
        }
        
    except Exception as e:
        print(f"❌ Error exporting application analytics: {e}")
        return None

def create_analytics_report(user_data, job_data, app_data):
    """Create a comprehensive analytics report."""
    print("📊 Creating Analytics Report...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create summary report
    summary = {
        'export_timestamp': datetime.now().isoformat(),
        'summary': {
            'total_users': sum(role['total_users'] for role in user_data['user_stats']),
            'active_users': sum(role['active_users'] for role in user_data['user_stats']),
            'total_jobs': job_data['job_stats'].get('total_jobs', 0),
            'active_jobs': job_data['job_stats'].get('active_jobs', 0),
            'total_applications': app_data['application_stats'].get('total_applications', 0)
        },
        'user_breakdown': user_data['user_stats'],
        'job_breakdown': job_data['job_categories'],
        'recent_activity': {
            'new_users_7d': sum(role['new_users_7d'] for role in user_data['user_stats']),
            'new_jobs_7d': job_data['job_stats'].get('new_jobs_7d', 0),
            'applications_7d': app_data['application_stats'].get('applications_7d', 0)
        }
    }
    
    return summary, timestamp

def upload_to_supabase(data, filename, timestamp):
    """Upload analytics data to Supabase."""
    print(f"☁️ Uploading {filename} to Supabase...")
    
    try:
        client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        # Convert data to JSON
        json_data = json.dumps(data, indent=2, default=str)
        
        # Upload to analytics bucket
        upload_path = f"analytics_{timestamp}/{filename}"
        result = client.storage.from_("analytics-exports").upload(
            upload_path,
            json_data.encode('utf-8'),
            file_options={"content-type": "application/json"}
        )
        
        if hasattr(result, 'error') and result.error:
            print(f"  ❌ Upload failed: {result.error}")
            return None
        else:
            # Get public URL
            public_url = client.storage.from_("analytics-exports").get_public_url(upload_path)
            print(f"  ✅ Uploaded successfully: {public_url}")
            return public_url
            
    except Exception as e:
        print(f"  ❌ Error uploading to Supabase: {e}")
        return None

def create_csv_export(data, filename, timestamp):
    """Create CSV export for spreadsheet analysis."""
    print(f"📈 Creating CSV export: {filename}")
    
    try:
        # Create temporary directory
        temp_dir = Path("temp_analytics")
        temp_dir.mkdir(exist_ok=True)
        
        csv_path = temp_dir / f"{filename}_{timestamp}.csv"
        
        if 'user_details' in data:
            # Export user details to CSV
            df = pd.DataFrame(data['user_details'])
            df.to_csv(csv_path, index=False)
        elif 'registration_trends' in data:
            # Export registration trends to CSV
            df = pd.DataFrame(data['registration_trends'])
            df.to_csv(csv_path, index=False)
        elif 'application_trends' in data:
            # Export application trends to CSV
            df = pd.DataFrame(data['application_trends'])
            df.to_csv(csv_path, index=False)
        
        return csv_path
        
    except Exception as e:
        print(f"  ❌ Error creating CSV: {e}")
        return None

def main():
    """Main analytics export function."""
    print("📊 Joborra Analytics Export System")
    print("=" * 50)
    
    # Get database connection
    db_session = get_database_connection()
    if not db_session:
        return 1
    
    try:
        # Export all analytics
        user_data = export_user_analytics(db_session)
        job_data = export_job_analytics(db_session)
        app_data = export_application_analytics(db_session)
        
        if not all([user_data, job_data, app_data]):
            print("❌ Failed to export some analytics data")
            return 1
        
        # Create comprehensive report
        summary, timestamp = create_analytics_report(user_data, job_data, app_data)
        
        # Upload reports to Supabase
        uploads = []
        
        # Upload summary report
        summary_url = upload_to_supabase(summary, "analytics_summary.json", timestamp)
        if summary_url:
            uploads.append(("Summary Report", summary_url))
        
        # Upload detailed data
        user_url = upload_to_supabase(user_data, "user_analytics.json", timestamp)
        if user_url:
            uploads.append(("User Analytics", user_url))
        
        job_url = upload_to_supabase(job_data, "job_analytics.json", timestamp)
        if job_url:
            uploads.append(("Job Analytics", job_url))
        
        app_url = upload_to_supabase(app_data, "application_analytics.json", timestamp)
        if app_url:
            uploads.append(("Application Analytics", app_url))
        
        # Create and upload CSV exports
        csv_files = []
        
        # User details CSV
        user_csv = create_csv_export(user_data, "user_details", timestamp)
        if user_csv:
            csv_files.append(user_csv)
        
        # Registration trends CSV
        reg_csv = create_csv_export(user_data, "registration_trends", timestamp)
        if reg_csv:
            csv_files.append(reg_csv)
        
        # Upload CSV files
        for csv_file in csv_files:
            try:
                with open(csv_file, 'rb') as f:
                    csv_data = f.read()
                
                filename = Path(csv_file).name
                upload_path = f"analytics_{timestamp}/{filename}"
                
                client = create_client(
                    os.getenv("SUPABASE_URL"),
                    os.getenv("SUPABASE_SERVICE_KEY")
                )
                
                result = client.storage.from_("analytics-exports").upload(
                    upload_path,
                    csv_data,
                    file_options={"content-type": "text/csv"}
                )
                
                if not (hasattr(result, 'error') and result.error):
                    public_url = client.storage.from_("analytics-exports").get_public_url(upload_path)
                    uploads.append((f"CSV Export: {filename}", public_url))
                    print(f"  ✅ Uploaded CSV: {filename}")
                
            except Exception as e:
                print(f"  ❌ Error uploading CSV {csv_file}: {e}")
        
        # Print results
        print(f"\n{'='*50}")
        print("📊 Analytics Export Complete!")
        print(f"📅 Export Timestamp: {timestamp}")
        print(f"📁 Files Uploaded: {len(uploads)}")
        
        if uploads:
            print("\n🔗 Uploaded Files:")
            for name, url in uploads:
                print(f"  📄 {name}: {url}")
        
        # Clean up temporary files
        temp_dir = Path("temp_analytics")
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
            print(f"\n🧹 Cleaned up temporary files")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error in analytics export: {e}")
        return 1
    finally:
        db_session.close()

if __name__ == "__main__":
    exit(main())
