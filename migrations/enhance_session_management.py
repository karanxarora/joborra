"""
Migration to enhance session management with additional security fields
"""
import sqlite3
from datetime import datetime

def run_migration():
    """Add enhanced session management fields to user_sessions table"""
    conn = sqlite3.connect('joborra.db')
    cursor = conn.cursor()
    
    try:
        # Check if user_sessions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_sessions'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Creating user_sessions table...")
            cursor.execute('''
            CREATE TABLE user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                expires_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                user_agent VARCHAR(500),
                ip_address VARCHAR(45),
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                device_fingerprint VARCHAR(255),
                login_method VARCHAR(50) DEFAULT 'password',
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            ''')
            print("✅ Created user_sessions table")
        else:
            print("Enhancing existing user_sessions table...")
            
            # Get current columns
            cursor.execute('PRAGMA table_info(user_sessions)')
            existing_columns = [col[1] for col in cursor.fetchall()]
            print(f"Existing columns: {existing_columns}")
            
            # Add new columns if they don't exist
            if 'updated_at' not in existing_columns:
                cursor.execute('ALTER TABLE user_sessions ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP')
                print("✅ Added updated_at column")
            
            if 'last_activity' not in existing_columns:
                cursor.execute('ALTER TABLE user_sessions ADD COLUMN last_activity DATETIME DEFAULT CURRENT_TIMESTAMP')
                print("✅ Added last_activity column")
            
            if 'device_fingerprint' not in existing_columns:
                cursor.execute('ALTER TABLE user_sessions ADD COLUMN device_fingerprint VARCHAR(255)')
                print("✅ Added device_fingerprint column")
            
            if 'login_method' not in existing_columns:
                cursor.execute('ALTER TABLE user_sessions ADD COLUMN login_method VARCHAR(50) DEFAULT "password"')
                print("✅ Added login_method column")
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions (user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions (session_token)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions (is_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions (expires_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_sessions_activity ON user_sessions (last_activity)')
        
        # Create trigger to update updated_at timestamp
        cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_session_timestamp 
        AFTER UPDATE ON user_sessions
        BEGIN
            UPDATE user_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
        ''')
        
        # Create trigger to update last_activity on session validation
        cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_session_activity 
        AFTER UPDATE OF expires_at ON user_sessions
        BEGIN
            UPDATE user_sessions SET last_activity = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
        ''')
        
        conn.commit()
        print("✅ Session management enhancement completed successfully")
        
        # Verify the table structure
        cursor.execute("PRAGMA table_info(user_sessions)")
        columns = cursor.fetchall()
        print(f"Session table columns: {[col[1] for col in columns]}")
        
    except Exception as e:
        print(f"❌ Error enhancing session management: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
