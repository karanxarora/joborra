"""
Add contact_number field to users table
"""

from sqlalchemy import text

def upgrade(connection):
    """Add contact_number column to users table"""
    # Check if column already exists
    result = connection.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'contact_number'
    """))
    
    if not result.fetchone():
        connection.execute(text("""
            ALTER TABLE users ADD COLUMN contact_number VARCHAR(20)
        """))
        print("Added contact_number column to users table")
    else:
        print("contact_number column already exists in users table")

def downgrade(connection):
    """Remove contact_number column from users table"""
    connection.execute(text("""
        ALTER TABLE users DROP COLUMN IF EXISTS contact_number
    """))
    print("Removed contact_number column from users table")
