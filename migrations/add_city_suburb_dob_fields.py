#!/usr/bin/env python3
"""
Migration: Add city_suburb and date_of_birth fields to users table
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Add city_suburb and date_of_birth columns to users table"""
    
    # Get database path
    db_path = "joborra.db"
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. Skipping migration.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add city_suburb column if it doesn't exist
        if 'city_suburb' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN city_suburb VARCHAR(255)")
            print("Added city_suburb column to users table")
        else:
            print("city_suburb column already exists")
        
        # Add date_of_birth column if it doesn't exist
        if 'date_of_birth' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN date_of_birth DATETIME")
            print("Added date_of_birth column to users table")
        else:
            print("date_of_birth column already exists")
        
        conn.commit()
        print("Migration completed successfully")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
