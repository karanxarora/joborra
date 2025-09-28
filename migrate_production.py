#!/usr/bin/env python3
"""
Simple production database migration script.
Uses SQLAlchemy models to ensure proper schema and data types.
"""

import os
import sys
import logging
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.orm import sessionmaker

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main migration function"""
    try:
        # Import models to register them
        from app.database import Base
        from app import models
        from app import visa_models
        
        # Setup source (SQLite - production backup)
        sqlite_db = "joborra_production_backup.db"
        if not os.path.exists(sqlite_db):
            logger.error(f"Production backup database not found: {sqlite_db}")
            return False
        
        sqlite_engine = create_engine(f"sqlite:///{sqlite_db}")
        logger.info(f"Connected to SQLite: {sqlite_db}")
        
        # Setup destination (Supabase PostgreSQL)
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY") 
        
        if not supabase_url or not supabase_service_key:
            logger.error("Missing Supabase configuration")
            return False
        
        # Use pooler connection string if available
        postgres_url = os.getenv("SUPABASE_DATABASE_URL")
        if not postgres_url:
            # Build pooler URL
            project_ref = supabase_url.replace("https://", "").split('.supabase.co')[0]
            postgres_url = f"postgresql://postgres.{project_ref}:{supabase_service_key}@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres?sslmode=require"
        
        supabase_engine = create_engine(postgres_url)
        logger.info("Connected to Supabase PostgreSQL")
        
        # Step 1: Create fresh schema in Supabase
        logger.info("Creating fresh schema in Supabase...")
        Base.metadata.drop_all(bind=supabase_engine)
        Base.metadata.create_all(bind=supabase_engine)
        logger.info("✅ Schema created successfully")
        
        # Step 2: Get table list from SQLite
        with sqlite_engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
            tables = [row[0] for row in result.fetchall()]
        
        logger.info(f"Found {len(tables)} tables to migrate")
        
        # Step 3: Migrate data for each table
        total_records = 0
        
        for table_name in tables:
            if table_name == 'sqlite_sequence':
                continue  # Skip SQLite internal table
                
            try:
                # Count records
                with sqlite_engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.fetchone()[0]
                
                if count == 0:
                    logger.info(f"⏭️  {table_name}: empty, skipping")
                    continue
                
                logger.info(f"🔄 Migrating {table_name}: {count} records")
                
                # Get all data
                with sqlite_engine.connect() as conn:
                    result = conn.execute(text(f"SELECT * FROM {table_name}"))
                    rows = result.fetchall()
                    columns = result.keys()
                
                # Prepare data with type conversion
                batch_data = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        
                        # Convert SQLite boolean integers to PostgreSQL booleans
                        boolean_columns = [
                            'is_active', 'is_verified', 'visa_sponsorship', 'remote_option',
                            'international_student_friendly', 'is_duplicate', 'is_joborra_job',
                            'visa_sponsor_history', 'is_accredited_sponsor', 'success'
                        ]
                        
                        if col in boolean_columns and isinstance(value, int):
                            row_dict[col] = bool(value)
                        else:
                            row_dict[col] = value
                    
                    batch_data.append(row_dict)
                
                # Insert data
                if batch_data:
                    with supabase_engine.connect() as conn:
                        placeholders = ", ".join([f":{col}" for col in columns])
                        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                        
                        conn.execute(text(insert_sql), batch_data)
                        conn.commit()
                
                total_records += count
                logger.info(f"✅ {table_name}: {count} records migrated")
                
            except Exception as e:
                logger.error(f"❌ Failed to migrate {table_name}: {e}")
                continue
        
        logger.info("🎉 Migration Summary:")
        logger.info(f"✅ Tables processed: {len(tables)}")
        logger.info(f"✅ Total records migrated: {total_records}")
        
        # Step 4: Verify key tables
        logger.info("\n🔍 Verifying migration:")
        key_tables = ['users', 'jobs', 'companies']
        
        for table in key_tables:
            try:
                with supabase_engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    logger.info(f"✅ {table}: {count} records in Supabase")
            except Exception as e:
                logger.error(f"❌ Failed to verify {table}: {e}")
        
        logger.info("\n🎉 Production database migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
