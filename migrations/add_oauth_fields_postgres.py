"""
Add missing OAuth fields to users table on Postgres.

Usage:
  DATABASE_URL=postgres://... python -m migrations.add_oauth_fields_postgres

Requires that your .env (or environment) has DATABASE_URL pointing to your Postgres DB.
This script is idempotent: it uses IF NOT EXISTS to avoid errors if columns already exist.
"""
from __future__ import annotations

import os
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Ensure we import the project package database to reuse engine configuration
from app.database import engine


def ensure_columns():
    statements = [
        # oauth_provider: varchar(50)
        text("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR(50)
        """),
        # oauth_sub: provider user id (unique, indexed)
        text("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS oauth_sub VARCHAR(255)
        """),
        # Add index for oauth_sub for faster lookups; IF NOT EXISTS available in PG >= 9.5 for indexes
        text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relname = 'ix_users_oauth_sub' AND n.nspname = 'public'
            ) THEN
                CREATE INDEX ix_users_oauth_sub ON users (oauth_sub);
            END IF;
        END$$;
        """),
    ]

    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(stmt)


if __name__ == "__main__":
    try:
        ensure_columns()
        print("✓ OAuth columns ensured on users table (oauth_provider, oauth_sub)")
    except SQLAlchemyError as e:
        print(f"Failed to migrate users table: {e}")
        raise
