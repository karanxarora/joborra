"""
Add missing user profile fields to users table on Postgres.

Usage:
  DATABASE_URL=postgres://... python -m migrations.add_user_profile_fields_postgres

This script is idempotent: it uses IF NOT EXISTS and checks for index existence.
"""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine

# Columns derived from app/auth_models.py User model
# Types chosen to match SQLAlchemy declarations reasonably in Postgres
STATEMENTS = [
    # Student-specific and study details
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS course_name VARCHAR(200)"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS institution_name VARCHAR(200)"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS course_start_date TIMESTAMP NULL"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS course_end_date TIMESTAMP NULL"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS coe_number VARCHAR(50)"""),

    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS skills TEXT"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS experience_level VARCHAR(50)"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS preferred_locations TEXT"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS salary_expectations_min INTEGER"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS salary_expectations_max INTEGER"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS work_authorization VARCHAR(100)"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS linkedin_profile VARCHAR(500)"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS github_profile VARCHAR(500)"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS portfolio_url VARCHAR(500)"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS resume_url VARCHAR(500)"""),

    # Employer-specific fields
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS company_name VARCHAR(255)"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS company_website VARCHAR(255)"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS company_size VARCHAR(100)"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS industry VARCHAR(255)"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS company_description TEXT"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS company_logo_url VARCHAR(500)"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS company_location VARCHAR(255)"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS hiring_manager_name VARCHAR(255)"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS hiring_manager_title VARCHAR(255)"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS company_benefits TEXT"""),
    text("""ALTER TABLE users ADD COLUMN IF NOT EXISTS company_culture TEXT"""),
]


def migrate():
    with engine.begin() as conn:
        for stmt in STATEMENTS:
            conn.execute(stmt)


if __name__ == "__main__":
    try:
        migrate()
        print("✓ User profile columns ensured on users table")
    except SQLAlchemyError as e:
        print(f"Failed to migrate users table profile fields: {e}")
        raise
