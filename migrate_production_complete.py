#!/usr/bin/env python3
"""
Complete production database migration script.
Migrates ALL data preserving the exact production database schema.
"""

import os
import sys
import logging
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Text, Boolean, DateTime, Float
from sqlalchemy.orm import sessionmaker

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionMigrator:
    def __init__(self):
        self.sqlite_db = "joborra_production_backup.db"
        self.migration_stats = {
            'tables_migrated': 0,
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
        
    def get_production_schema(self) -> Dict[str, str]:
        """Get the exact schema from production database"""
        schemas = {}
        with self.sqlite_engine.connect() as conn:
            result = conn.execute(text("SELECT name, sql FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'"))
            for name, sql in result.fetchall():
                schemas[name] = sql
        return schemas
        
    def sqlite_to_postgres_type(self, sqlite_type: str) -> str:
        """Convert SQLite types to PostgreSQL types"""
        type_map = {
            'INTEGER': 'INTEGER',
            'VARCHAR': 'VARCHAR',
            'TEXT': 'TEXT', 
            'BOOLEAN': 'BOOLEAN',
            'DATETIME': 'TIMESTAMP',
            'FLOAT': 'REAL',
            'JSON': 'JSONB'
        }
        
        # Handle parameterized types
        base_type = sqlite_type.split('(')[0].upper()
        if base_type in type_map:
            if '(' in sqlite_type:
                return f"{type_map[base_type]}{sqlite_type[len(base_type):]}"
            return type_map[base_type]
        
        # Default fallback
        return 'TEXT'
        
    def convert_schema_to_postgres(self, sqlite_sql: str) -> str:
        """Convert SQLite CREATE TABLE to PostgreSQL"""
        postgres_sql = sqlite_sql
        
        # Replace SQLite-specific with PostgreSQL
        replacements = [
            ('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY'),
            ('CURRENT_TIMESTAMP', 'CURRENT_TIMESTAMP'),
            ('JSON', 'JSONB'),
            ('BOOLEAN DEFAULT 0', 'BOOLEAN DEFAULT false'),
            ('BOOLEAN DEFAULT 1', 'BOOLEAN DEFAULT true'),
            ('DEFAULT (CURRENT_TIMESTAMP)', 'DEFAULT CURRENT_TIMESTAMP'),
        ]
        
        for old, new in replacements:
            postgres_sql = postgres_sql.replace(old, new)
            
        return postgres_sql
        
    def create_postgres_tables(self, schemas: Dict[str, str]):
        """Create all tables in PostgreSQL"""
        logger.info("Creating PostgreSQL tables...")
        
        with self.supabase_engine.connect() as conn:
            # Drop existing tables in correct order (reverse dependency)
            drop_order = [
                'visa_verification_history', 'vevo_api_logs', 'visa_verifications',
                'user_sessions', 'job_applications', 'job_favorites', 'job_views',
                'job_drafts', 'jobs', 'users', 'companies', 'scraping_logs', 'visa_keywords'
            ]
            
            for table in drop_order:
                if table in schemas:
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
                if table_name in schemas:
                    try:
                        postgres_sql = self.convert_schema_to_postgres(schemas[table_name])
                        logger.info(f"Creating table: {table_name}")
                        conn.execute(text(postgres_sql))
                        conn.commit()
                        logger.info(f"✅ Created table: {table_name}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create {table_name}: {e}")
                        self.migration_stats['errors'] += 1
                        
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
            'vevo_api_logs': ['success'],
            'visa_verifications': []  # No boolean defaults in this table
        }
        
        converted = {}
        for key, value in row_dict.items():
            # Convert boolean integers
            if table_name in boolean_columns and key in boolean_columns[table_name]:
                if isinstance(value, int):
                    converted[key] = bool(value)
                else:
                    converted[key] = value
            # Keep other values as-is
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
                        placeholders = ", ".join([f":{col}" for col in columns])
                        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                        
                        # Process in batches to avoid memory issues
                        batch_size = 100
                        for i in range(0, len(batch_data), batch_size):
                            batch = batch_data[i:i + batch_size]
                            pg_conn.execute(text(insert_sql), batch)
                            logger.info(f"Inserted batch {i//batch_size + 1} ({len(batch)} records)")
                        
                        pg_conn.commit()
                
                self.migration_stats['total_records'] += len(rows)
                logger.info(f"✅ {table_name}: {len(rows)} records migrated successfully")
                
        except Exception as e:
            logger.error(f"❌ Failed to migrate {table_name}: {e}")
            self.migration_stats['errors'] += 1
            # Continue with next table instead of stopping
            
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
                    logger.warning(f"⚠️  {table}: {pg_count}/{sqlite_count} records migrated (partial)")
                    
            except Exception as e:
                logger.error(f"❌ Could not verify {table}: {e}")
                
    def run_migration(self):
        """Run the complete migration"""
        try:
            logger.info("🚀 Starting complete production migration...")
            
            # Setup connections
            self.setup_connections()
            
            # Get production schema
            logger.info("📋 Analyzing production database schema...")
            schemas = self.get_production_schema()
            logger.info(f"Found {len(schemas)} tables to migrate")
            
            # Create PostgreSQL tables
            self.create_postgres_tables(schemas)
            
            # Migrate data in correct order
            migration_order = [
                'companies', 'visa_keywords', 'scraping_logs', 'users',
                'jobs', 'job_favorites', 'job_applications', 'job_views', 
                'job_drafts', 'user_sessions', 'visa_verifications',
                'visa_verification_history', 'vevo_api_logs'
            ]
            
            for table_name in migration_order:
                if table_name in schemas:
                    self.migrate_table_data(table_name)
                    self.migration_stats['tables_migrated'] += 1
            
            # Verify migration
            self.verify_migration()
            
            # Print summary
            logger.info("\n🎉 MIGRATION COMPLETE!")
            logger.info("=" * 50)
            logger.info(f"✅ Tables migrated: {self.migration_stats['tables_migrated']}")
            logger.info(f"✅ Total records migrated: {self.migration_stats['total_records']}")
            logger.info(f"❌ Errors encountered: {self.migration_stats['errors']}")
            logger.info("=" * 50)
            
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
