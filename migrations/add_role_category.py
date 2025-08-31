#!/usr/bin/env python3
"""
Migration: Add role_category field to jobs table
Date: 2024-12-19
Description: Adds role_category column to jobs table for categorizing jobs as SERVICE_RETAIL_HOSPITALITY or STUDY_ALIGNED_PROFESSIONAL
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Add role_category field to the jobs table"""
    
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'joborra.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Starting migration: Add role_category field to jobs table...")
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'role_category' not in columns:
            print("Adding role_category column...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN role_category VARCHAR(50)")
            print("✅ Added role_category column")
        else:
            print("⚠️  role_category column already exists")
        
        # Commit changes
        conn.commit()
        print("✅ Migration completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
