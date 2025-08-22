"""
Migration to add visa verification tables
"""
import sqlite3
from datetime import datetime

def run_migration():
    """Add visa verification tables to the database"""
    conn = sqlite3.connect('joborra.db')
    cursor = conn.cursor()
    
    try:
        # Create visa_verifications table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS visa_verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            visa_grant_number VARCHAR(20),
            transaction_reference_number VARCHAR(20),
            visa_subclass VARCHAR(10) NOT NULL,
            passport_number VARCHAR(20) NOT NULL,
            passport_country VARCHAR(3) NOT NULL,
            passport_expiry DATETIME,
            visa_status VARCHAR(20) DEFAULT 'pending',
            visa_grant_date DATETIME,
            visa_expiry_date DATETIME,
            work_rights_condition VARCHAR(20),
            work_hours_limit INTEGER,
            work_rights_details TEXT,
            course_name VARCHAR(200),
            institution_name VARCHAR(200),
            course_start_date DATETIME,
            course_end_date DATETIME,
            coe_number VARCHAR(50),
            verification_method VARCHAR(50),
            verification_date DATETIME,
            verification_reference VARCHAR(100),
            passport_document_url VARCHAR(500),
            visa_grant_document_url VARCHAR(500),
            coe_document_url VARCHAR(500),
            verification_notes TEXT,
            rejection_reason TEXT,
            last_vevo_check DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        ''')
        
        # Create visa_verification_history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS visa_verification_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visa_verification_id INTEGER NOT NULL,
            previous_status VARCHAR(20) NOT NULL,
            new_status VARCHAR(20) NOT NULL,
            change_reason TEXT,
            verification_method VARCHAR(50),
            verification_result TEXT,
            verified_by VARCHAR(100),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (visa_verification_id) REFERENCES visa_verifications (id) ON DELETE CASCADE
        )
        ''')
        
        # Create vevo_api_logs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vevo_api_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visa_verification_id INTEGER NOT NULL,
            api_provider VARCHAR(50) NOT NULL,
            request_data TEXT,
            response_data TEXT,
            success BOOLEAN DEFAULT 0,
            error_message TEXT,
            verification_result TEXT,
            api_cost VARCHAR(10),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (visa_verification_id) REFERENCES visa_verifications (id) ON DELETE CASCADE
        )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_visa_verifications_user_id ON visa_verifications (user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_visa_verifications_status ON visa_verifications (visa_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_visa_verifications_expiry ON visa_verifications (visa_expiry_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_visa_history_verification_id ON visa_verification_history (visa_verification_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vevo_logs_verification_id ON vevo_api_logs (visa_verification_id)')
        
        # Create trigger to update updated_at timestamp
        cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_visa_verification_timestamp 
        AFTER UPDATE ON visa_verifications
        BEGIN
            UPDATE visa_verifications SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
        ''')
        
        conn.commit()
        print("✅ Visa verification tables created successfully")
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'visa_%'")
        tables = cursor.fetchall()
        print(f"Created tables: {[table[0] for table in tables]}")
        
    except Exception as e:
        print(f"❌ Error creating visa verification tables: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
