"""
Add database constraints and defaults for user creation
"""

import sqlite3
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Add constraints and defaults to prevent user creation issues"""
    try:
        conn = sqlite3.connect('joborra.db')
        cursor = conn.cursor()
        
        # Add constraints to ensure proper defaults
        logger.info("Adding database constraints for user table...")
        
        # Check if constraints already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = {col[1]: col for col in cursor.fetchall()}
        
        # Ensure is_active defaults to 1 (True)
        if 'is_active' in columns:
            cursor.execute("UPDATE users SET is_active = 1 WHERE is_active IS NULL")
            logger.info("Set default is_active = 1 for existing users")
        
        # Ensure is_verified defaults to 0 (False) for new users, 1 for existing
        if 'is_verified' in columns:
            cursor.execute("UPDATE users SET is_verified = 1 WHERE is_verified IS NULL")
            logger.info("Set is_verified = 1 for existing users")
        
        # Ensure created_at has timestamps
        if 'created_at' in columns:
            current_time = datetime.now().isoformat()
            cursor.execute("UPDATE users SET created_at = ? WHERE created_at IS NULL", (current_time,))
            logger.info("Set created_at timestamps for existing users")
        
        # Ensure updated_at has timestamps
        if 'updated_at' in columns:
            current_time = datetime.now().isoformat()
            cursor.execute("UPDATE users SET updated_at = ? WHERE updated_at IS NULL", (current_time,))
            logger.info("Set updated_at timestamps for existing users")
        
        # Ensure role values are uppercase enum values
        cursor.execute("UPDATE users SET role = 'STUDENT' WHERE role = 'student'")
        cursor.execute("UPDATE users SET role = 'EMPLOYER' WHERE role = 'employer'")
        cursor.execute("UPDATE users SET role = 'ADMIN' WHERE role = 'admin'")
        logger.info("Normalized role values to uppercase enum format")
        
        conn.commit()
        
        # Verify all users have proper values
        cursor.execute("""
            SELECT id, email, role, is_active, is_verified, created_at, updated_at 
            FROM users
        """)
        users = cursor.fetchall()
        
        logger.info("Verified user data after migration:")
        for user in users:
            logger.info(f"  ID: {user[0]}, Email: {user[1]}, Role: {user[2]}, "
                       f"Active: {user[3]}, Verified: {user[4]}, "
                       f"Created: {user[5]}, Updated: {user[6]}")
        
        # Create a trigger to ensure future users get proper defaults
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS user_defaults_trigger
            AFTER INSERT ON users
            FOR EACH ROW
            WHEN NEW.created_at IS NULL OR NEW.updated_at IS NULL OR NEW.is_active IS NULL
            BEGIN
                UPDATE users SET 
                    created_at = COALESCE(NEW.created_at, datetime('now')),
                    updated_at = COALESCE(NEW.updated_at, datetime('now')),
                    is_active = COALESCE(NEW.is_active, 1)
                WHERE id = NEW.id;
            END;
        """)
        logger.info("Created trigger to ensure proper defaults for future users")
        
        conn.close()
        logger.info("✅ User constraints migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("✅ Migration completed successfully")
    else:
        print("❌ Migration failed")
        exit(1)
