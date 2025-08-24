#!/usr/bin/env python3
"""
Migrate data from local SQLite (joborra.db) to Supabase Postgres.
- Requires DATABASE_URL env pointing to Supabase Postgres (with sslmode=require).
- Reads from ./joborra.db using SQLite.
- Inserts explicit IDs to preserve relationships.
- Resets Postgres sequences after inserts.
Run:
  python scripts/init_supabase_schema.py
  python scripts/migrate_sqlite_to_supabase.py
"""
import os
import sys
import logging
from typing import Type, Iterable
from datetime import datetime

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load .env explicitly from project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Ensure local project root is first on sys.path so `import app` targets our package
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Probe file at import time to confirm script starts
try:
    with open("migration_probe.txt", "a", encoding="utf-8") as pf:
        pf.write(f"[IMPORT] {datetime.utcnow().isoformat()}Z Script import start\n")
except Exception:
    pass

# Force logging configuration even if another module configured it
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s", force=True)
logger = logging.getLogger("migrate_sqlite_to_supabase")
# Also log to a file to capture output even if stdout/stderr is suppressed
try:
    fh = logging.FileHandler("migration_debug.log", mode="a", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(fh)
except Exception:
    pass


def _sanitize_value(col, value):
    from sqlalchemy import String
    import json
    # Normalize JSON-like strings
    if getattr(col.type, "__class__", None).__name__ == "JSON":
        if isinstance(value, str):
            if value.strip().lower() in {"null", "none", ""}:
                return None
            try:
                return json.loads(value)
            except Exception:
                # Keep as original string if it's valid JSON-friendly text
                return value
        return value
    # Truncate strings to column length
    if isinstance(col.type, String) and isinstance(value, str):
        length = getattr(col.type, "length", None)
        if length and len(value) > length:
            return value[:length]
    return value


def copy_table(src_sess, dst_sess, Model: Type, batch_size: int = 1000):
    total = src_sess.query(Model).count()
    logger.info(f"Migrating {Model.__tablename__}: {total} rows")
    offset = 0
    while offset < total:
        rows: Iterable = (
            src_sess.query(Model)
            .order_by(Model.id)
            .limit(batch_size)
            .offset(offset)
            .all()
        )
        for row in rows:
            # Create a new instance for destination with same PK, sanitized per column
            data = {}
            for c in Model.__table__.columns:
                raw = getattr(row, c.name)
                data[c.name] = _sanitize_value(c, raw)
            obj = Model(**data)
            try:
                dst_sess.merge(obj)  # merge preserves PK and upserts by PK
            except Exception as e:
                logger.exception(f"Failed to merge {Model.__tablename__} id={getattr(row, 'id', None)}: {e}")
                raise
        dst_sess.commit()
        offset += batch_size
        logger.info(f"  -> {min(offset, total)}/{total}")


def reset_sequence(dst_sess, table_name: str, pk: str = "id"):
    import re
    # Validate identifiers to avoid SQL injection via identifiers
    ident = r"[A-Za-z_][A-Za-z0-9_]*"
    if not re.fullmatch(ident, table_name) or not re.fullmatch(ident, pk):
        logger.warning(f"Invalid identifier for reset_sequence: {table_name}.{pk}")
        return
    try:
        # Use parameters for pg_get_serial_sequence arguments, but embed identifiers in MAX() query
        sql = text(
            f"SELECT setval(pg_get_serial_sequence(:table, :pk), "
            f"COALESCE((SELECT MAX(\"{pk}\") FROM \"{table_name}\"), 0))"
        )
        dst_sess.execute(sql, {"table": table_name, "pk": pk})
        dst_sess.commit()
        logger.info(f"Reset sequence for {table_name}({pk})")
    except Exception as e:
        logger.warning(f"Could not reset sequence for {table_name}: {e}")
        dst_sess.rollback()


def main():
    # Probe at main start
    try:
        with open("migration_probe.txt", "a", encoding="utf-8") as pf:
            pf.write(f"[MAIN] {datetime.utcnow().isoformat()}Z Enter main()\n")
    except Exception:
        pass
    db_url = os.getenv("DATABASE_URL")
    if not db_url or db_url.startswith("sqlite"):
        logger.error("DATABASE_URL must point to Supabase Postgres. Set it in .env")
        sys.exit(1)
    # Mask password for logging
    try:
        masked = db_url
        if "@" in db_url and "://" in db_url:
            prefix, rest = db_url.split("://", 1)
            cred, host = rest.split("@", 1)
            if ":" in cred:
                user, _pwd = cred.split(":", 1)
                masked = f"{prefix}://{user}:***@{host}"
        logger.info(f"Using DATABASE_URL: {masked}")
    except Exception:
        pass

    logger.info("Checking for SQLite source ./joborra.db ...")
    if not os.path.exists("joborra.db"):
        logger.error("Source SQLite file joborra.db not found in project root.")
        sys.exit(1)

    # Engines and sessions
    logger.info("Connecting to SQLite source ...")
    src_engine = create_engine("sqlite:///./joborra.db", connect_args={"check_same_thread": False})
    SrcSession = sessionmaker(bind=src_engine)
    src_sess = SrcSession()

    # Destination uses app.database for SSL + pooling
    logger.info("Importing destination engine and models ...")
    try:
        from app.database import engine as dst_engine
        from app import models as app_models
        from app import auth_models as auth_models
        # Ensure visa models (e.g., VisaVerification) are registered
        from app import visa_models as visa_models  # noqa: F401
    except Exception as e:
        logger.exception(f"Failed importing app modules: {e}")
        raise

    logger.info("Connecting to Supabase destination ...")
    DstSession = sessionmaker(bind=dst_engine)
    dst_sess = DstSession()
    # Explicit connectivity check
    try:
        with dst_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Supabase connectivity check passed (SELECT 1).")
    except Exception as e:
        logger.exception(f"Supabase connectivity check failed: {e}")
        raise

    try:
        # Order matters due to FKs
        logger.info("Starting table copies ...")
        copy_table(src_sess, dst_sess, app_models.Company)
        copy_table(src_sess, dst_sess, auth_models.User)
        copy_table(src_sess, dst_sess, app_models.Job)
        copy_table(src_sess, dst_sess, auth_models.JobFavorite)
        copy_table(src_sess, dst_sess, auth_models.JobApplication)
        copy_table(src_sess, dst_sess, auth_models.JobView)
        copy_table(src_sess, dst_sess, app_models.VisaKeyword)
        copy_table(src_sess, dst_sess, app_models.ScrapingLog)

        # Reset sequences
        logger.info("Resetting sequences ...")
        reset_sequence(dst_sess, "companies")
        reset_sequence(dst_sess, "users")
        reset_sequence(dst_sess, "jobs")
        reset_sequence(dst_sess, "job_favorites")
        reset_sequence(dst_sess, "job_applications")
        reset_sequence(dst_sess, "job_views")
        reset_sequence(dst_sess, "visa_keywords")
        reset_sequence(dst_sess, "scraping_logs")

        logger.info("\nMigration completed successfully.")
    except Exception as e:
        logger.exception(f"Migration failed: {e}")
        # Emergency error file
        try:
            import traceback
            with open("migration_error.txt", "a", encoding="utf-8") as ef:
                ef.write(f"[ERROR] {datetime.utcnow().isoformat()}Z {e}\n")
                ef.write(traceback.format_exc() + "\n")
        except Exception:
            pass
        dst_sess.rollback()
        sys.exit(1)
    finally:
        src_sess.close()
        dst_sess.close()


if __name__ == "__main__":
    main()
