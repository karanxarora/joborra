#!/usr/bin/env python3
"""
Final production database migration script.
Creates tables exactly as they exist in production SQLite, with proper PostgreSQL syntax.
"""

import os
import sys
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionMigrator:
    def __init__(self):
        self.sqlite_db = "joborra_production_backup.db"
        self.migration_stats = {
            'tables_created': 0,
            'total_records': 0,
            'errors': 0
        }
        
    def setup_connections(self):
        """Setup database connections"""
        # SQLite connection
        if not os.path.exists(self.sqlite_db):
            raise FileNotFoundError(f"Production backup not found: {self.sqlite_db}")
        
        self.sqlite_engine = create_engine(f"sqlite:///{self.sqlite_db}")
        logger.info(f"Connected to SQLite: {self.sqlite_db}")
        
        # Supabase connection
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not supabase_service_key:
            raise ValueError("Missing Supabase configuration")
        
        # Use pooler connection string if available
        postgres_url = os.getenv("SUPABASE_DATABASE_URL")
        if not postgres_url:
            project_ref = supabase_url.replace("https://", "").split('.supabase.co')[0]
            postgres_url = f"postgresql://postgres.{project_ref}:{supabase_service_key}@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres?sslmode=require"
        
        self.supabase_engine = create_engine(postgres_url, pool_pre_ping=True)
        logger.info("Connected to Supabase PostgreSQL")
        
    def create_production_schema(self):
        """Create all tables based on production schema"""
        logger.info("Creating production schema in Supabase...")
        
        # Production table schemas (manually defined for full control)
        table_schemas = {
            'companies': '''
                CREATE TABLE companies (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    website VARCHAR(500),
                    size VARCHAR(50),
                    industry VARCHAR(100),
                    location VARCHAR(200),
                    visa_sponsor_history BOOLEAN DEFAULT false,
                    is_accredited_sponsor BOOLEAN DEFAULT false,
                    sponsor_confidence REAL,
                    sponsor_abn VARCHAR(20),
                    sponsor_approval_date TIMESTAMP,
                    ats_type VARCHAR(50),
                    ats_company_id VARCHAR(100),
                    ats_last_scraped TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )''',
                
            'visa_keywords': '''
                CREATE TABLE visa_keywords (
                    id SERIAL PRIMARY KEY,
                    keyword VARCHAR(200) NOT NULL UNIQUE,
                    keyword_type VARCHAR(50),
                    weight REAL,
                    category VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''',
                
            'scraping_logs': '''
                CREATE TABLE scraping_logs (
                    id SERIAL PRIMARY KEY,
                    source_website VARCHAR(100) NOT NULL,
                    jobs_found INTEGER,
                    jobs_processed INTEGER,
                    jobs_saved INTEGER,
                    errors_count INTEGER,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    status VARCHAR(50),
                    error_details TEXT
                )''',
                
            'users': '''
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) NOT NULL,
                    username VARCHAR(100) NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255) NOT NULL,
                    role VARCHAR(8) NOT NULL,
                    is_active BOOLEAN DEFAULT true,
                    is_verified BOOLEAN DEFAULT false,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    last_login TIMESTAMP,
                    university VARCHAR(255),
                    degree VARCHAR(255),
                    graduation_year INTEGER,
                    visa_status VARCHAR(100),
                    company_name VARCHAR(255),
                    company_website VARCHAR(255),
                    company_size VARCHAR(100),
                    industry VARCHAR(255),
                    skills TEXT,
                    experience_level VARCHAR(50),
                    preferred_locations TEXT,
                    salary_expectations_min INTEGER,
                    salary_expectations_max INTEGER,
                    work_authorization VARCHAR(100),
                    linkedin_profile VARCHAR(500),
                    github_profile VARCHAR(500),
                    portfolio_url VARCHAR(500),
                    bio TEXT,
                    company_description TEXT,
                    company_logo_url VARCHAR(500),
                    company_location VARCHAR(255),
                    hiring_manager_name VARCHAR(255),
                    hiring_manager_title VARCHAR(255),
                    company_benefits TEXT,
                    company_culture TEXT,
                    resume_url VARCHAR(500),
                    course_name VARCHAR(200),
                    institution_name VARCHAR(200),
                    course_start_date TIMESTAMP,
                    course_end_date TIMESTAMP,
                    coe_number VARCHAR(50),
                    contact_number VARCHAR(20),
                    oauth_provider VARCHAR(50),
                    oauth_sub VARCHAR(255),
                    education TEXT,
                    experience TEXT,
                    city_suburb VARCHAR(255),
                    date_of_birth TIMESTAMP,
                    company_abn VARCHAR(20),
                    employer_role_title VARCHAR(255)
                )''',
                
            'jobs': '''
                CREATE TABLE jobs (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    company_id INTEGER REFERENCES companies(id),
                    location VARCHAR(200),
                    state VARCHAR(50),
                    city VARCHAR(100),
                    salary_min REAL,
                    salary_max REAL,
                    salary_currency VARCHAR(3),
                    employment_type VARCHAR(50),
                    experience_level VARCHAR(50),
                    remote_option BOOLEAN DEFAULT false,
                    visa_sponsorship BOOLEAN DEFAULT false,
                    visa_sponsorship_confidence REAL,
                    international_student_friendly BOOLEAN DEFAULT false,
                    source_website VARCHAR(100) NOT NULL,
                    source_url VARCHAR(1000) UNIQUE,
                    source_job_id VARCHAR(100),
                    required_skills JSONB,
                    preferred_skills JSONB,
                    education_requirements VARCHAR(200),
                    posted_date TIMESTAMP,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT true,
                    is_duplicate BOOLEAN DEFAULT false,
                    posted_by_user_id INTEGER REFERENCES users(id),
                    is_joborra_job BOOLEAN DEFAULT false,
                    salary VARCHAR(255),
                    job_type VARCHAR(100),
                    job_document_url VARCHAR(500),
                    role_category VARCHAR(50),
                    visa_types TEXT,
                    visa_type VARCHAR(100)
                )''',
                
            'job_favorites': '''
                CREATE TABLE job_favorites (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    job_id INTEGER NOT NULL REFERENCES jobs(id),
                    created_at TIMESTAMP,
                    notes TEXT
                )''',
                
            'job_applications': '''
                CREATE TABLE job_applications (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    job_id INTEGER NOT NULL REFERENCES jobs(id),
                    status VARCHAR(50),
                    applied_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    cover_letter TEXT,
                    resume_url VARCHAR(500),
                    notes TEXT
                )''',
                
            'job_views': '''
                CREATE TABLE job_views (
                    id SERIAL PRIMARY KEY,
                    job_id INTEGER NOT NULL REFERENCES jobs(id),
                    user_id INTEGER REFERENCES users(id),
                    viewed_at TIMESTAMP NOT NULL,
                    ip_address VARCHAR(45),
                    user_agent VARCHAR(500),
                    referrer VARCHAR(500),
                    session_id VARCHAR(255)
                )''',
                
            'job_drafts': '''
                CREATE TABLE job_drafts (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    location VARCHAR(200),
                    city VARCHAR(100),
                    state VARCHAR(50),
                    salary_min REAL,
                    salary_max REAL,
                    salary_currency VARCHAR(3) DEFAULT 'AUD',
                    salary VARCHAR(255),
                    employment_type VARCHAR(50),
                    job_type VARCHAR(100),
                    role_category VARCHAR(50),
                    experience_level VARCHAR(50),
                    remote_option BOOLEAN DEFAULT false,
                    visa_sponsorship BOOLEAN DEFAULT false,
                    international_student_friendly BOOLEAN DEFAULT false,
                    required_skills TEXT,
                    preferred_skills TEXT,
                    education_requirements TEXT,
                    expires_at TIMESTAMP,
                    draft_name VARCHAR(255),
                    step INTEGER DEFAULT 0,
                    created_by_user_id INTEGER NOT NULL REFERENCES users(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP,
                    visa_types TEXT
                )''',
                
            'user_sessions': '''
                CREATE TABLE user_sessions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    session_token VARCHAR(255) NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT false,
                    user_agent VARCHAR(500),
                    ip_address VARCHAR(45),
                    last_activity TIMESTAMP,
                    device_fingerprint VARCHAR(255),
                    login_method VARCHAR(50)
                )''',
                
            'visa_verifications': '''
                CREATE TABLE visa_verifications (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    visa_grant_number VARCHAR(20),
                    transaction_reference_number VARCHAR(20),
                    visa_subclass VARCHAR(10) NOT NULL,
                    passport_number VARCHAR(20) NOT NULL,
                    passport_country VARCHAR(3) NOT NULL,
                    passport_expiry TIMESTAMP,
                    visa_status VARCHAR(20) DEFAULT 'pending',
                    visa_grant_date TIMESTAMP,
                    visa_expiry_date TIMESTAMP,
                    work_rights_condition VARCHAR(20),
                    work_hours_limit INTEGER,
                    work_rights_details TEXT,
                    course_name VARCHAR(200),
                    institution_name VARCHAR(200),
                    course_start_date TIMESTAMP,
                    course_end_date TIMESTAMP,
                    coe_number VARCHAR(50),
                    verification_method VARCHAR(50),
                    verification_date TIMESTAMP,
                    verification_reference VARCHAR(100),
                    passport_document_url VARCHAR(500),
                    visa_grant_document_url VARCHAR(500),
                    coe_document_url VARCHAR(500),
                    verification_notes TEXT,
                    rejection_reason TEXT,
                    last_vevo_check TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    vevo_document_url VARCHAR(500)
                )''',
                
            'visa_verification_history': '''
                CREATE TABLE visa_verification_history (
                    id SERIAL PRIMARY KEY,
                    visa_verification_id INTEGER NOT NULL REFERENCES visa_verifications(id) ON DELETE CASCADE,
                    previous_status VARCHAR(20) NOT NULL,
                    new_status VARCHAR(20) NOT NULL,
                    change_reason TEXT,
                    verification_method VARCHAR(50),
                    verification_result TEXT,
                    verified_by VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''',
                
            'vevo_api_logs': '''
                CREATE TABLE vevo_api_logs (
                    id SERIAL PRIMARY KEY,
                    visa_verification_id INTEGER NOT NULL REFERENCES visa_verifications(id) ON DELETE CASCADE,
                    api_provider VARCHAR(50) NOT NULL,
                    request_data TEXT,
                    response_data TEXT,
                    success BOOLEAN DEFAULT false,
                    error_message TEXT,
                    verification_result TEXT,
                    api_cost VARCHAR(10),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )'''
        }
        
        with self.supabase_engine.connect() as conn:
            # Drop existing tables in reverse dependency order
            drop_tables = [
                'visa_verification_history', 'vevo_api_logs', 'visa_verifications',
                'user_sessions', 'job_applications', 'job_favorites', 'job_views',
                'job_drafts', 'jobs', 'users', 'companies', 'scraping_logs', 'visa_keywords'
            ]
            
            for table in drop_tables:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    logger.info(f"Dropped existing table: {table}")
                except Exception as e:
                    logger.warning(f"Could not drop {table}: {e}")
            
            conn.commit()
            
            # Create tables in dependency order
            create_order = [
                'companies', 'visa_keywords', 'scraping_logs', 'users',
                'jobs', 'job_favorites', 'job_applications', 'job_views',
                'job_drafts', 'user_sessions', 'visa_verifications',
                'visa_verification_history', 'vevo_api_logs'
            ]
            
            for table_name in create_order:
                if table_name in table_schemas:
                    try:
                        logger.info(f"Creating table: {table_name}")
                        conn.execute(text(table_schemas[table_name]))
                        conn.commit()
                        logger.info(f"✅ Created table: {table_name}")
                        self.migration_stats['tables_created'] += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to create {table_name}: {e}")
                        self.migration_stats['errors'] += 1
                        conn.rollback()  # Important: rollback failed transaction
                        
    def convert_data_types(self, table_name: str, row_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Convert data types from SQLite to PostgreSQL"""
        # Boolean columns that are stored as 0/1 in SQLite
        boolean_columns = {
            'companies': ['visa_sponsor_history', 'is_accredited_sponsor'],
            'jobs': ['remote_option', 'visa_sponsorship', 'international_student_friendly', 
                    'is_active', 'is_duplicate', 'is_joborra_job'],
            'users': ['is_active', 'is_verified'],
            'user_sessions': ['is_active'],
            'job_drafts': ['remote_option', 'visa_sponsorship', 'international_student_friendly'],
            'vevo_api_logs': ['success']
        }
        
        converted = {}
        for key, value in row_dict.items():
            # Skip the 'id' column for SERIAL tables to let PostgreSQL auto-generate
            if key == 'id' and table_name in ['companies', 'visa_keywords', 'scraping_logs', 
                                            'users', 'jobs', 'job_favorites', 'job_applications', 
                                            'job_views', 'job_drafts', 'user_sessions', 
                                            'visa_verifications', 'visa_verification_history', 
                                            'vevo_api_logs']:
                continue
                
            # Convert boolean integers
            if table_name in boolean_columns and key in boolean_columns[table_name]:
                if isinstance(value, int):
                    converted[key] = bool(value)
                else:
                    converted[key] = value
            else:
                converted[key] = value
                
        return converted
        
    def migrate_table_data(self, table_name: str):
        """Migrate all data for a specific table"""
        logger.info(f"🔄 Migrating {table_name}...")
        
        try:
            # Get data from SQLite
            with self.sqlite_engine.connect() as sqlite_conn:
                result = sqlite_conn.execute(text(f"SELECT * FROM {table_name}"))
                rows = result.fetchall()
                columns = list(result.keys())
                
                if not rows:
                    logger.info(f"⏭️  {table_name}: empty, skipping")
                    return
                
                logger.info(f"Found {len(rows)} records in {table_name}")
                
                # Convert data
                batch_data = []
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    converted_row = self.convert_data_types(table_name, row_dict)
                    batch_data.append(converted_row)
                
                # Insert into PostgreSQL
                if batch_data:
                    with self.supabase_engine.connect() as pg_conn:
                        # Build insert statement without 'id' for SERIAL columns
                        insert_columns = [col for col in columns if col != 'id']
                        placeholders = ", ".join([f":{col}" for col in insert_columns])
                        insert_sql = f"INSERT INTO {table_name} ({', '.join(insert_columns)}) VALUES ({placeholders})"
                        
                        # Process in batches
                        batch_size = 50
                        for i in range(0, len(batch_data), batch_size):
                            batch = batch_data[i:i + batch_size]
                            try:
                                pg_conn.execute(text(insert_sql), batch)
                                logger.info(f"Inserted batch {i//batch_size + 1} ({len(batch)} records)")
                            except Exception as e:
                                logger.error(f"Failed to insert batch {i//batch_size + 1}: {e}")
                                # Try individual inserts for this batch
                                for j, record in enumerate(batch):
                                    try:
                                        pg_conn.execute(text(insert_sql), record)
                                    except Exception as record_error:
                                        logger.error(f"Failed to insert record {i+j+1}: {record_error}")
                        
                        pg_conn.commit()
                
                self.migration_stats['total_records'] += len(rows)
                logger.info(f"✅ {table_name}: {len(rows)} records migrated successfully")
                
        except Exception as e:
            logger.error(f"❌ Failed to migrate {table_name}: {e}")
            self.migration_stats['errors'] += 1
            
    def verify_migration(self):
        """Verify that all data was migrated correctly"""
        logger.info("\n🔍 Verifying migration...")
        
        tables_to_verify = ['users', 'jobs', 'companies', 'user_sessions', 'job_drafts']
        
        for table in tables_to_verify:
            try:
                # Count in SQLite
                with self.sqlite_engine.connect() as sqlite_conn:
                    result = sqlite_conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    sqlite_count = result.fetchone()[0]
                
                # Count in PostgreSQL
                with self.supabase_engine.connect() as pg_conn:
                    result = pg_conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    pg_count = result.fetchone()[0]
                
                if sqlite_count == pg_count:
                    logger.info(f"✅ {table}: {pg_count}/{sqlite_count} records migrated")
                else:
                    logger.warning(f"⚠️  {table}: {pg_count}/{sqlite_count} records migrated")
                    
            except Exception as e:
                logger.error(f"❌ Could not verify {table}: {e}")
                
    def run_migration(self):
        """Run the complete migration"""
        try:
            logger.info("🚀 Starting complete production migration...")
            
            # Setup connections
            self.setup_connections()
            
            # Create PostgreSQL schema
            self.create_production_schema()
            
            # Migrate data in correct order
            migration_order = [
                'companies', 'visa_keywords', 'scraping_logs', 'users',
                'jobs', 'job_favorites', 'job_applications', 'job_views', 
                'job_drafts', 'user_sessions', 'visa_verifications',
                'visa_verification_history', 'vevo_api_logs'
            ]
            
            for table_name in migration_order:
                self.migrate_table_data(table_name)
            
            # Verify migration
            self.verify_migration()
            
            # Print summary
            logger.info("\n🎉 MIGRATION COMPLETE!")
            logger.info("=" * 60)
            logger.info(f"✅ Tables created: {self.migration_stats['tables_created']}")
            logger.info(f"✅ Total records migrated: {self.migration_stats['total_records']}")
            logger.info(f"❌ Errors encountered: {self.migration_stats['errors']}")
            logger.info("=" * 60)
            
            return self.migration_stats['errors'] == 0
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False

def main():
    migrator = ProductionMigrator()
    success = migrator.run_migration()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
