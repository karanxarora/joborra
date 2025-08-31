#!/usr/bin/env python3
"""
Migration: Add ABN and Role/Title fields for employers
Date: 2024-12-19
Description: Adds company_abn and employer_role_title columns to users table for employer registration
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Add new employer fields to the users table"""
    
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'joborra.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Starting migration: Add employer fields...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'company_abn' not in columns:
            print("Adding company_abn column...")
            cursor.execute("ALTER TABLE users ADD COLUMN company_abn VARCHAR(20)")
            print("✅ Added company_abn column")
        else:
            print("⚠️  company_abn column already exists")
            
        if 'employer_role_title' not in columns:
            print("Adding employer_role_title column...")
            cursor.execute("ALTER TABLE users ADD COLUMN employer_role_title VARCHAR(255)")
            print("✅ Added employer_role_title column")
        else:
            print("⚠️  employer_role_title column already exists")
        
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
