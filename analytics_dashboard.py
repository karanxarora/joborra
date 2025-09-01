#!/usr/bin/env python3
"""
Analytics Dashboard - View and analyze exported analytics data.
"""

import os
import sys
import json
import requests
from datetime import datetime
from supabase import create_client

# Set environment variables
os.environ["SUPABASE_URL"] = "https://noupavjvuhezvzpqcbqg.supabase.co"
os.environ["SUPABASE_SERVICE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5vdXBhdmp2dWhlenZ6cHFjYnFnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjA0MzU5NywiZXhwIjoyMDcxNjE5NTk3fQ.Qe1YV0aVr-aNdUsP1SlN8qqVpR8ofIBX0d10lT2sS2o"

def get_analytics_files():
    """Get list of analytics files from Supabase."""
    print("📁 Fetching Analytics Files...")
    
    try:
        client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        # List files in analytics bucket
        files_result = client.storage.from_("analytics-exports").list()
        
        if hasattr(files_result, 'error') and files_result.error:
            print(f"❌ Error listing files: {files_result.error}")
            return []
        
        # Group files by timestamp
        analytics_folders = {}
        for file_info in files_result:
            name = file_info.get('name', '')
            # Check if it's a folder (analytics_YYYYMMDD_HHMMSS)
            if name.startswith('analytics_') and '/' not in name:
                timestamp = name.replace('analytics_', '')
                # List files in this folder
                try:
                    folder_files = client.storage.from_("analytics-exports").list(name)
                    if not (hasattr(folder_files, 'error') and folder_files.error):
                        analytics_folders[timestamp] = [f.get('name', '') for f in folder_files]
                except Exception as e:
                    print(f"Warning: Could not list files in {name}: {e}")
                    analytics_folders[timestamp] = []
        
        return analytics_folders
        
    except Exception as e:
        print(f"❌ Error fetching analytics files: {e}")
        return {}

def download_analytics_file(filename):
    """Download analytics file from Supabase."""
    try:
        client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        # Download file
        file_data = client.storage.from_("analytics-exports").download(filename)
        
        if hasattr(file_data, 'error') and file_data.error:
            print(f"❌ Error downloading file: {file_data.error}")
            return None
        
        return file_data
        
    except Exception as e:
        print(f"❌ Error downloading file: {e}")
        return None

def display_summary(data):
    """Display analytics summary."""
    print("\n📊 Analytics Summary")
    print("=" * 50)
    
    if 'summary' in data:
        summary = data['summary']
        print(f"👥 Total Users: {summary.get('total_users', 0)}")
        print(f"✅ Active Users: {summary.get('active_users', 0)}")
        print(f"💼 Total Jobs: {summary.get('total_jobs', 0)}")
        print(f"✅ Active Jobs: {summary.get('active_jobs', 0)}")
        print(f"📝 Total Applications: {summary.get('total_applications', 0)}")
        
        if 'recent_activity' in data:
            recent = data['recent_activity']
            print(f"\n📈 Recent Activity (7 days):")
            print(f"  👥 New Users: {recent.get('new_users_7d', 0)}")
            print(f"  💼 New Jobs: {recent.get('new_jobs_7d', 0)}")
            print(f"  📝 Applications: {recent.get('applications_7d', 0)}")
    
    if 'user_breakdown' in data:
        print(f"\n👥 User Breakdown by Role:")
        for role_data in data['user_breakdown']:
            role = role_data.get('role', 'Unknown')
            total = role_data.get('total_users', 0)
            active = role_data.get('active_users', 0)
            verified = role_data.get('verified_users', 0)
            with_resume = role_data.get('users_with_resume', 0)
            with_phone = role_data.get('users_with_phone', 0)
            print(f"  {role}: {total} total, {active} active, {verified} verified")
            print(f"    📄 With Resume: {with_resume}, 📞 With Phone: {with_phone}")
    
    if 'job_breakdown' in data:
        print(f"\n💼 Top Job Categories:")
        for i, category in enumerate(data['job_breakdown'][:5], 1):
            name = category.get('role_category', 'Unknown')
            count = category.get('count', 0)
            print(f"  {i}. {name}: {count} jobs")

def display_detailed_analytics(data, data_type):
    """Display detailed analytics data."""
    print(f"\n📊 Detailed {data_type}")
    print("=" * 50)
    
    if data_type == "User Analytics":
        if 'user_stats' in data:
            print("👥 User Statistics by Role:")
            for role_data in data['user_stats']:
                role = role_data.get('role', 'Unknown')
                print(f"\n  {role}:")
                print(f"    Total Users: {role_data.get('total_users', 0)}")
                print(f"    Active Users: {role_data.get('active_users', 0)}")
                print(f"    Verified Users: {role_data.get('verified_users', 0)}")
                print(f"    New (30d): {role_data.get('new_users_30d', 0)}")
                print(f"    New (7d): {role_data.get('new_users_7d', 0)}")
        
        if 'registration_trends' in data:
            print(f"\n📈 Registration Trends (Last 10 days):")
            for trend in data['registration_trends'][:10]:
                date = trend.get('date', 'Unknown')
                role = trend.get('role', 'Unknown')
                count = trend.get('registrations', 0)
                print(f"  {date} - {role}: {count}")
        
        if 'education_stats' in data:
            print(f"\n🎓 Top Universities:")
            for i, uni in enumerate(data['education_stats'][:10], 1):
                name = uni.get('university', 'Unknown')
                count = uni.get('student_count', 0)
                print(f"  {i}. {name}: {count} students")
        
        if 'skills_stats' in data:
            print(f"\n🛠️ Top Skills:")
            for i, skill in enumerate(data['skills_stats'][:10], 1):
                name = skill.get('skills', 'Unknown')
                count = skill.get('user_count', 0)
                print(f"  {i}. {name}: {count} users")
        
        if 'location_stats' in data:
            print(f"\n📍 Top Locations:")
            for i, location in enumerate(data['location_stats'][:10], 1):
                name = location.get('city_suburb', 'Unknown')
                count = location.get('user_count', 0)
                print(f"  {i}. {name}: {count} users")
        
        if 'company_stats' in data:
            print(f"\n🏢 Top Companies:")
            for i, company in enumerate(data['company_stats'][:10], 1):
                name = company.get('company_name', 'Unknown')
                industry = company.get('industry', 'Unknown')
                count = company.get('employee_count', 0)
                print(f"  {i}. {name} ({industry}): {count} employees")
    
    elif data_type == "Job Analytics":
        if 'job_stats' in data:
            stats = data['job_stats']
            print("💼 Job Statistics:")
            print(f"  Total Jobs: {stats.get('total_jobs', 0)}")
            print(f"  Active Jobs: {stats.get('active_jobs', 0)}")
            print(f"  New (30d): {stats.get('new_jobs_30d', 0)}")
            print(f"  New (7d): {stats.get('new_jobs_7d', 0)}")
            print(f"  Avg Salary Min: ${stats.get('avg_salary_min', 0):,.0f}")
            print(f"  Avg Salary Max: ${stats.get('avg_salary_max', 0):,.0f}")
            print(f"  Jobs with Documents: {stats.get('jobs_with_documents', 0)}")
        
        if 'job_categories' in data:
            print(f"\n📊 Job Categories:")
            for i, category in enumerate(data['job_categories'][:10], 1):
                name = category.get('role_category', 'Unknown')
                count = category.get('count', 0)
                print(f"  {i}. {name}: {count}")
        
        if 'job_locations' in data:
            print(f"\n📍 Top Job Locations:")
            for i, location in enumerate(data['job_locations'][:10], 1):
                state = location.get('state', 'Unknown')
                city = location.get('city', 'Unknown')
                count = location.get('count', 0)
                print(f"  {i}. {city}, {state}: {count}")
    
    elif data_type == "Application Analytics":
        if 'application_stats' in data:
            stats = data['application_stats']
            print("📝 Application Statistics:")
            print(f"  Total Applications: {stats.get('total_applications', 0)}")
            print(f"  Applications (30d): {stats.get('applications_30d', 0)}")
            print(f"  Applications (7d): {stats.get('applications_7d', 0)}")
        
        if 'application_trends' in data:
            print(f"\n📈 Application Trends (Last 10 days):")
            for trend in data['application_trends'][:10]:
                date = trend.get('date', 'Unknown')
                count = trend.get('applications', 0)
                print(f"  {date}: {count}")

def main():
    """Main dashboard function."""
    print("📊 Joborra Analytics Dashboard")
    print("=" * 50)
    
    # Get available analytics files
    analytics_folders = get_analytics_files()
    
    if not analytics_folders:
        print("❌ No analytics files found")
        return 1
    
    # Show available exports
    print(f"\n📁 Available Analytics Exports:")
    timestamps = sorted(analytics_folders.keys(), reverse=True)
    
    for i, timestamp in enumerate(timestamps[:5], 1):  # Show last 5 exports
        try:
            dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            file_count = len(analytics_folders[timestamp])
            print(f"  {i}. {formatted_time} ({file_count} files)")
        except:
            print(f"  {i}. {timestamp} ({len(analytics_folders[timestamp])} files)")
    
    # Use the most recent export
    if timestamps:
        latest_timestamp = timestamps[0]
        print(f"\n📊 Using latest export: {latest_timestamp}")
        
        # Download and display summary
        summary_file = f"analytics_{latest_timestamp}/analytics_summary.json"
        summary_data = download_analytics_file(summary_file)
        
        if summary_data:
            try:
                summary_json = json.loads(summary_data)
                display_summary(summary_json)
            except Exception as e:
                print(f"❌ Error parsing summary data: {e}")
        
        # Download and display detailed analytics
        detailed_files = [
            ("analytics_summary.json", "Summary"),
            ("user_analytics.json", "User Analytics"),
            ("job_analytics.json", "Job Analytics"),
            ("application_analytics.json", "Application Analytics")
        ]
        
        for filename, display_name in detailed_files:
            file_path = f"analytics_{latest_timestamp}/{filename}"
            data = download_analytics_file(file_path)
            
            if data:
                try:
                    json_data = json.loads(data)
                    display_detailed_analytics(json_data, display_name)
                except Exception as e:
                    print(f"❌ Error parsing {filename}: {e}")
        
        print(f"\n✅ Analytics dashboard complete!")
        print(f"📅 Data from: {latest_timestamp}")
        
    else:
        print("❌ No valid analytics exports found")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
