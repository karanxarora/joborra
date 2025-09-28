#!/usr/bin/env python3
"""
SQLite to Supabase Migration Script
==================================

This script migrates data from SQLite database to Supabase (PostgreSQL) while maintaining
compatibility with existing users and preserving authentication data.

Works for both:
- Local development environments 
- Production environments during CI/CD deployment

Usage:
    python migrate_sqlite_to_supabase.py [--dry-run] [--force] [--batch-size=1000]
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
import sqlite3
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.orm import sessionmaker
from supabase import create_client, Client
from dotenv import load_dotenv
import hashlib

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SQLiteToSupabaseMigration:
    def __init__(self, dry_run=False, force=False, batch_size=1000):
        self.dry_run = dry_run
        self.force = force
        self.batch_size = batch_size
        self.migration_stats = {
            'tables_migrated': 0,
            'records_migrated': 0,
            'files_migrated': 0,
            'errors': 0,
            'start_time': datetime.now(),
            'warnings': []
        }
        
        # Initialize connections
        self.sqlite_engine = None
        self.supabase_engine = None
        self.supabase_client = None
        
        self._setup_connections()
    
    def _setup_connections(self):
        """Setup SQLite and Supabase connections"""
        try:
            # SQLite connection
            sqlite_path = os.getenv("DATABASE_URL", "sqlite:///./joborra.db")
            if sqlite_path.startswith("sqlite:///"):
                sqlite_path = sqlite_path.replace("sqlite:///", "")
            elif sqlite_path.startswith("sqlite://"):
                sqlite_path = sqlite_path.replace("sqlite://", "")
            else:
                sqlite_path = "./joborra.db"
            
            if not os.path.exists(sqlite_path):
                raise FileNotFoundError(f"SQLite database not found: {sqlite_path}")
                
            self.sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
            logger.info(f"Connected to SQLite: {sqlite_path}")
            
            # Supabase connection
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
            
            if not supabase_url or not supabase_service_key:
                raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
            
            # Create Supabase client
            self.supabase_client = create_client(supabase_url, supabase_service_key)
            
            # Use direct PostgreSQL connection string if available, otherwise build one
            postgres_url = os.getenv("SUPABASE_DATABASE_URL")
            
            if not postgres_url:
                # Fallback to building URL (might not work due to IPv4 issues)
                project_ref = supabase_url.replace("https://", "").split('.supabase.co')[0]
                postgres_url = f"postgresql://postgres.{project_ref}:{supabase_service_key}@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres?sslmode=require"
            
            self.supabase_engine = create_engine(postgres_url)
            logger.info("Connected to Supabase PostgreSQL")
            
        except Exception as e:
            logger.error(f"Failed to setup connections: {e}")
            sys.exit(1)
    
    def _get_table_schemas(self) -> Dict[str, List[Dict]]:
        """Get schema information for all tables from SQLite"""
        schemas = {}
        
        with self.sqlite_engine.connect() as conn:
            # Get all table names
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            
            for table_name in tables:
                # Get column information
                result = conn.execute(text(f"PRAGMA table_info({table_name})"))
                columns = []
                for row in result.fetchall():
                    columns.append({
                        'name': row[1],
                        'type': row[2],
                        'nullable': not row[3],
                        'default': row[4],
                        'primary_key': bool(row[5])
                    })
                schemas[table_name] = columns
                
        return schemas
    
    def _sqlite_to_postgres_type(self, sqlite_type: str) -> str:
        """Convert SQLite types to PostgreSQL types"""
        type_mapping = {
            'INTEGER': 'INTEGER',
            'TEXT': 'TEXT',
            'REAL': 'REAL',
            'BLOB': 'BYTEA',
            'NUMERIC': 'NUMERIC',
            'VARCHAR': 'VARCHAR',
            'BOOLEAN': 'BOOLEAN',
            'DATETIME': 'TIMESTAMP',
            'JSON': 'JSONB'
        }
        
        # Handle parameterized types like VARCHAR(255)
        base_type = sqlite_type.split('(')[0].upper()
        if base_type in type_mapping:
            if '(' in sqlite_type:
                return f"{type_mapping[base_type]}{sqlite_type[len(base_type):]}"
            else:
                return type_mapping[base_type]
        
        # Default to TEXT for unknown types
        logger.warning(f"Unknown SQLite type: {sqlite_type}, defaulting to TEXT")
        return 'TEXT'
    
    def _create_supabase_tables(self, schemas: Dict[str, List[Dict]]):
        """Create tables in Supabase if they don't exist"""
        
        for table_name, columns in schemas.items():
            if self.dry_run:
                logger.info(f"[DRY RUN] Would create table: {table_name}")
                continue
            
            try:
                # Check if table exists
                with self.supabase_engine.connect() as conn:
                    result = conn.execute(text(
                        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table_name)"
                    ), {"table_name": table_name})
                    
                    table_exists = result.fetchone()[0]
                    
                    if table_exists and not self.force:
                        logger.info(f"Table {table_name} already exists, skipping creation")
                        continue
                    elif table_exists and self.force:
                        logger.warning(f"Dropping existing table {table_name}")
                        conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
                        conn.commit()
                    
                    # Build CREATE TABLE statement
                    column_defs = []
                    for col in columns:
                        col_def = f"{col['name']} {self._sqlite_to_postgres_type(col['type'])}"
                        
                        if col['primary_key']:
                            col_def += " PRIMARY KEY"
                        elif not col['nullable']:
                            col_def += " NOT NULL"
                            
                        if col['default'] and col['default'] != 'NULL':
                            default_val = col['default']
                            # Convert boolean defaults from SQLite integers to PostgreSQL booleans
                            if self._sqlite_to_postgres_type(col['type']) == 'BOOLEAN' and str(default_val) in ['0', '1']:
                                default_val = 'true' if str(default_val) == '1' else 'false'
                            col_def += f" DEFAULT {default_val}"
                            
                        column_defs.append(col_def)
                    
                    create_sql = f"CREATE TABLE {table_name} ({', '.join(column_defs)})"
                    
                    logger.info(f"Creating table: {table_name}")
                    logger.debug(f"SQL: {create_sql}")
                    
                    conn.execute(text(create_sql))
                    conn.commit()
                    
                    self.migration_stats['tables_migrated'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to create table {table_name}: {e}")
                self.migration_stats['errors'] += 1
    
    def _migrate_table_data(self, table_name: str):
        """Migrate data from SQLite table to Supabase"""
        try:
            # Get all data from SQLite
            with self.sqlite_engine.connect() as sqlite_conn:
                result = sqlite_conn.execute(text(f"SELECT * FROM {table_name}"))
                rows = result.fetchall()
                columns = result.keys()
                
                if not rows:
                    logger.info(f"Table {table_name} is empty, skipping")
                    return
                
                logger.info(f"Migrating {len(rows)} records from {table_name}")
                
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would migrate {len(rows)} records to {table_name}")
                    return
                
                # Process in batches
                for i in range(0, len(rows), self.batch_size):
                    batch = rows[i:i + self.batch_size]
                    
                    # Prepare batch insert
                    with self.supabase_engine.connect() as supabase_conn:
                        # Clear existing data if force flag is set
                        if i == 0 and self.force:
                            logger.warning(f"Clearing existing data in {table_name}")
                            supabase_conn.execute(text(f"DELETE FROM {table_name}"))
                        
                        # Build parameterized insert statement
                        placeholders = ", ".join([f":{col}" for col in columns])
                        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                        
                        # Convert rows to dictionaries with data type conversion
                        batch_data = []
                        for row in batch:
                            row_dict = {}
                            for j, col in enumerate(columns):
                                value = row[j]
                                
                                # Convert SQLite boolean integers to PostgreSQL booleans
                                boolean_columns = [
                                    'is_active', 'is_verified', 'visa_sponsorship', 'remote_option',
                                    'international_student_friendly', 'is_duplicate', 'is_joborra_job',
                                    'visa_sponsor_history', 'is_accredited_sponsor'
                                ]
                                
                                if col in boolean_columns and isinstance(value, int):
                                    row_dict[col] = bool(value)
                                elif isinstance(value, str) and col in ['skills', 'education', 'experience', 'required_skills', 'preferred_skills', 'visa_types']:
                                    # Handle JSON fields
                                    try:
                                        json.loads(value)  # Validate JSON
                                        row_dict[col] = value
                                    except:
                                        row_dict[col] = value
                                else:
                                    row_dict[col] = value
                            batch_data.append(row_dict)
                        
                        # Execute batch insert
                        supabase_conn.execute(text(insert_sql), batch_data)
                        supabase_conn.commit()
                        
                        logger.info(f"Migrated batch {i//self.batch_size + 1} ({len(batch)} records) for {table_name}")
                        self.migration_stats['records_migrated'] += len(batch)
                        
        except Exception as e:
            logger.error(f"Failed to migrate data for table {table_name}: {e}")
            self.migration_stats['errors'] += 1
    
    def _migrate_files(self):
        """Migrate local files to Supabase Storage (if any exist)"""
        data_dir = "./data"
        
        if not os.path.exists(data_dir):
            logger.info("No local data directory found, skipping file migration")
            return
        
        try:
            # Create storage buckets
            buckets = ['resumes', 'company-logos', 'job-documents', 'visa-documents']
            
            for bucket_name in buckets:
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would create/verify bucket: {bucket_name}")
                    continue
                
                try:
                    # Try to create bucket (will fail if already exists, which is fine)
                    self.supabase_client.storage.create_bucket(bucket_name)
                    logger.info(f"Created storage bucket: {bucket_name}")
                except Exception as e:
                    if "already exists" in str(e):
                        logger.info(f"Bucket {bucket_name} already exists")
                    else:
                        logger.warning(f"Failed to create bucket {bucket_name}: {e}")
            
            # Migrate files from each directory
            file_mapping = {
                'resumes': 'resumes',
                'company_logos': 'company-logos',
                'job_docs': 'job-documents',
                'visa_documents': 'visa-documents'
            }
            
            for local_dir, bucket_name in file_mapping.items():
                local_path = os.path.join(data_dir, local_dir)
                if os.path.exists(local_path):
                    self._migrate_directory_to_bucket(local_path, bucket_name)
                    
        except Exception as e:
            logger.error(f"Failed to migrate files: {e}")
            self.migration_stats['errors'] += 1
    
    def _migrate_directory_to_bucket(self, local_path: str, bucket_name: str):
        """Migrate files from local directory to Supabase bucket"""
        for root, dirs, files in os.walk(local_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, local_path)
                
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would upload {relative_path} to {bucket_name}")
                    continue
                
                try:
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    
                    # Upload to Supabase Storage
                    result = self.supabase_client.storage.from_(bucket_name).upload(
                        relative_path, file_data
                    )
                    
                    if result:
                        logger.info(f"Uploaded {relative_path} to {bucket_name}")
                        self.migration_stats['files_migrated'] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to upload {file_path}: {e}")
                    self.migration_stats['errors'] += 1
    
    def _update_file_urls(self):
        """Update file URLs in database to point to Supabase Storage"""
        if self.dry_run:
            logger.info("[DRY RUN] Would update file URLs to Supabase Storage URLs")
            return
        
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            
            url_updates = [
                # Users table updates
                {
                    'table': 'users',
                    'columns': ['resume_url', 'company_logo_url', 'vevo_document_url'],
                    'bucket_mapping': {
                        'resume_url': 'resumes',
                        'company_logo_url': 'company-logos', 
                        'vevo_document_url': 'visa-documents'
                    }
                },
                # Jobs table updates
                {
                    'table': 'jobs',
                    'columns': ['job_document_url'],
                    'bucket_mapping': {
                        'job_document_url': 'job-documents'
                    }
                },
                # Visa verifications table updates
                {
                    'table': 'visa_verifications',
                    'columns': ['passport_document_url', 'visa_grant_document_url', 'coe_document_url', 'vevo_document_url'],
                    'bucket_mapping': {
                        'passport_document_url': 'visa-documents',
                        'visa_grant_document_url': 'visa-documents',
                        'coe_document_url': 'visa-documents',
                        'vevo_document_url': 'visa-documents'
                    }
                }
            ]
            
            with self.supabase_engine.connect() as conn:
                for update_config in url_updates:
                    table = update_config['table']
                    
                    for column in update_config['columns']:
                        bucket = update_config['bucket_mapping'][column]
                        
                        # Update local file paths to Supabase URLs
                        update_sql = f"""
                        UPDATE {table} 
                        SET {column} = CASE 
                            WHEN {column} LIKE '/data/%' THEN 
                                '{supabase_url}/storage/v1/object/public/{bucket}/' || 
                                SUBSTRING({column} FROM '/data/{bucket.replace('-', '_')}/(.*)$')
                            WHEN {column} LIKE 'data/%' THEN 
                                '{supabase_url}/storage/v1/object/public/{bucket}/' || 
                                SUBSTRING({column} FROM 'data/{bucket.replace('-', '_')}/(.*)$')
                            ELSE {column}
                        END
                        WHERE {column} IS NOT NULL 
                        AND ({column} LIKE '/data/%' OR {column} LIKE 'data/%')
                        """
                        
                        result = conn.execute(text(update_sql))
                        updated_rows = result.rowcount
                        conn.commit()
                        
                        if updated_rows > 0:
                            logger.info(f"Updated {updated_rows} {column} URLs in {table}")
                        
        except Exception as e:
            logger.error(f"Failed to update file URLs: {e}")
            self.migration_stats['errors'] += 1
    
    def _verify_migration(self):
        """Verify that migration was successful"""
        logger.info("Verifying migration...")
        
        try:
            with self.sqlite_engine.connect() as sqlite_conn:
                with self.supabase_engine.connect() as supabase_conn:
                    
                    # Get list of tables
                    sqlite_tables = sqlite_conn.execute(
                        text("SELECT name FROM sqlite_master WHERE type='table'")
                    ).fetchall()
                    
                    for table_row in sqlite_tables:
                        table_name = table_row[0]
                        
                        # Count records in both databases
                        sqlite_count = sqlite_conn.execute(
                            text(f"SELECT COUNT(*) FROM {table_name}")
                        ).fetchone()[0]
                        
                        try:
                            supabase_count = supabase_conn.execute(
                                text(f"SELECT COUNT(*) FROM {table_name}")
                            ).fetchone()[0]
                        except:
                            logger.warning(f"Table {table_name} not found in Supabase")
                            continue
                        
                        if sqlite_count == supabase_count:
                            logger.info(f"✅ {table_name}: {sqlite_count} records migrated successfully")
                        else:
                            logger.error(f"❌ {table_name}: SQLite({sqlite_count}) != Supabase({supabase_count})")
                            self.migration_stats['errors'] += 1
                            
        except Exception as e:
            logger.error(f"Failed to verify migration: {e}")
            self.migration_stats['errors'] += 1
    
    def _create_migration_backup(self):
        """Create a backup of the SQLite database before migration"""
        if self.dry_run:
            logger.info("[DRY RUN] Would create backup of SQLite database")
            return
        
        try:
            import shutil
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"joborra_backup_{timestamp}.db"
            
            shutil.copy2("./joborra.db", backup_name)
            logger.info(f"Created backup: {backup_name}")
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
    
    def run_migration(self):
        """Execute the complete migration process"""
        logger.info("Starting SQLite to Supabase migration...")
        logger.info(f"Dry run: {self.dry_run}, Force: {self.force}, Batch size: {self.batch_size}")
        
        try:
            # Step 1: Create backup
            self._create_migration_backup()
            
            # Step 2: Get table schemas
            logger.info("Analyzing SQLite database structure...")
            schemas = self._get_table_schemas()
            logger.info(f"Found {len(schemas)} tables to migrate")
            
            # Step 3: Create tables in Supabase
            logger.info("Creating tables in Supabase...")
            self._create_supabase_tables(schemas)
            
            # Step 4: Migrate data
            logger.info("Migrating table data...")
            for table_name in schemas.keys():
                self._migrate_table_data(table_name)
            
            # Step 5: Migrate files
            logger.info("Migrating files to Supabase Storage...")
            self._migrate_files()
            
            # Step 6: Update file URLs
            logger.info("Updating file URLs...")
            self._update_file_urls()
            
            # Step 7: Verify migration
            if not self.dry_run:
                self._verify_migration()
            
            # Step 8: Print summary
            self._print_migration_summary()
            
            return self.migration_stats['errors'] == 0
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def _print_migration_summary(self):
        """Print migration summary"""
        duration = datetime.now() - self.migration_stats['start_time']
        
        logger.info("\n" + "="*50)
        logger.info("MIGRATION SUMMARY")
        logger.info("="*50)
        logger.info(f"Duration: {duration}")
        logger.info(f"Tables migrated: {self.migration_stats['tables_migrated']}")
        logger.info(f"Records migrated: {self.migration_stats['records_migrated']}")
        logger.info(f"Files migrated: {self.migration_stats['files_migrated']}")
        logger.info(f"Errors: {self.migration_stats['errors']}")
        
        if self.migration_stats['warnings']:
            logger.info(f"Warnings: {len(self.migration_stats['warnings'])}")
            for warning in self.migration_stats['warnings']:
                logger.warning(f"  - {warning}")
        
        if self.migration_stats['errors'] == 0:
            logger.info("✅ Migration completed successfully!")
        else:
            logger.error("❌ Migration completed with errors!")
        
        logger.info("="*50)


def main():
    parser = argparse.ArgumentParser(description='Migrate SQLite database to Supabase')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Run migration simulation without making changes')
    parser.add_argument('--force', action='store_true',
                       help='Force overwrite existing tables and data')
    parser.add_argument('--batch-size', type=int, default=1000,
                       help='Number of records to process in each batch')
    
    args = parser.parse_args()
    
    migration = SQLiteToSupabaseMigration(
        dry_run=args.dry_run,
        force=args.force,
        batch_size=args.batch_size
    )
    
    success = migration.run_migration()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
