"""
Add study-related fields to users table (moved from visa verification)
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """Add study fields to users table: course_name, institution_name, course_start_date, course_end_date, coe_number"""
    try:
        conn = sqlite3.connect('joborra.db')
        cursor = conn.cursor()

        logger.info("Adding study fields to users table...")
        fields_sql = [
            "ALTER TABLE users ADD COLUMN course_name VARCHAR(200)",
            "ALTER TABLE users ADD COLUMN institution_name VARCHAR(200)",
            "ALTER TABLE users ADD COLUMN course_start_date DATETIME",
            "ALTER TABLE users ADD COLUMN course_end_date DATETIME",
            "ALTER TABLE users ADD COLUMN coe_number VARCHAR(50)",
        ]

        for field_sql in fields_sql:
            try:
                cursor.execute(field_sql)
                logger.info(f"Added field: {field_sql.split()[-2]}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    logger.info(f"Field already exists: {field_sql.split()[-2]}")
                else:
                    raise e

        conn.commit()
        conn.close()
        logger.info("✅ Study fields migration completed successfully")
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
