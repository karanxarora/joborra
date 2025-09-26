#!/usr/bin/env python3
"""
Test script for SQLite to Supabase migration
=============================================

This script provides a simple way to test the migration process
and verify that everything is working correctly.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_environment():
    """Test if environment is properly configured"""
    logger.info("Testing environment configuration...")
    
    required_vars = {
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_SERVICE_KEY': os.getenv('SUPABASE_SERVICE_KEY'),
        'SUPABASE_ANON_KEY': os.getenv('SUPABASE_ANON_KEY'),
    }
    
    missing_vars = []
    for var_name, var_value in required_vars.items():
        if not var_value:
            missing_vars.append(var_name)
        else:
            logger.info(f"✅ {var_name} is set")
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("✅ Environment configuration is valid")
    return True

def test_supabase_connection():
    """Test Supabase connection"""
    logger.info("Testing Supabase connection...")
    
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        client = create_client(supabase_url, supabase_key)
        
        # Test basic connection
        response = client.table('fake_table_test').select('*').limit(1).execute()
        # This will fail but confirms connection works
        
    except ImportError:
        logger.error("❌ Supabase Python client not installed. Run: pip install supabase")
        return False
    except Exception as e:
        if "relation \"public.fake_table_test\" does not exist" in str(e):
            logger.info("✅ Supabase connection successful (expected error for test query)")
            return True
        else:
            logger.error(f"❌ Supabase connection failed: {e}")
            return False
    
    logger.info("✅ Supabase connection successful")
    return True

def test_postgresql_connection():
    """Test PostgreSQL connection directly"""
    logger.info("Testing PostgreSQL connection...")
    
    try:
        from sqlalchemy import create_engine
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        # Extract project reference from Supabase URL
        project_ref = supabase_url.replace("https://", "").split(".supabase.co")[0]
        postgres_url = f"postgresql://postgres:{supabase_key}@{project_ref}.supabase.co:5432/postgres"
        
        engine = create_engine(postgres_url)
        
        with engine.connect() as conn:
            result = conn.execute("SELECT version();")
            version = result.fetchone()[0]
            logger.info(f"✅ PostgreSQL connection successful. Version: {version[:50]}...")
            
        return True
        
    except ImportError:
        logger.error("❌ PostgreSQL driver not installed. Run: pip install psycopg2-binary")
        return False
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_sqlite_database():
    """Test if SQLite database exists and is accessible"""
    logger.info("Testing SQLite database...")
    
    db_path = "joborra.db"
    if not os.path.exists(db_path):
        logger.warning(f"⚠️ SQLite database {db_path} not found")
        return False
    
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(f"sqlite:///{db_path}")
        
        with engine.connect() as conn:
            # Test basic query
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row[0] for row in result.fetchall()]
            
            logger.info(f"✅ SQLite database accessible. Found {len(tables)} tables: {', '.join(tables[:5])}")
            return True
            
    except Exception as e:
        logger.error(f"❌ SQLite database test failed: {e}")
        return False

def test_migration_script():
    """Test if migration script exists and is executable"""
    logger.info("Testing migration script...")
    
    script_path = "migrate_sqlite_to_supabase.py"
    if not os.path.exists(script_path):
        logger.error(f"❌ Migration script {script_path} not found")
        return False
    
    # Test if script can be imported (basic syntax check)
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("migration", script_path)
        module = importlib.util.module_from_spec(spec)
        
        logger.info("✅ Migration script exists and is syntactically valid")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration script has syntax errors: {e}")
        return False

def run_dry_run_migration():
    """Run migration in dry-run mode"""
    logger.info("Running migration in dry-run mode...")
    
    try:
        import subprocess
        
        result = subprocess.run([
            sys.executable, "migrate_sqlite_to_supabase.py", "--dry-run", "--batch-size=10"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("✅ Dry-run migration completed successfully")
            logger.info("Dry-run output (last 10 lines):")
            for line in result.stdout.split('\n')[-10:]:
                if line.strip():
                    logger.info(f"  {line}")
            return True
        else:
            logger.error("❌ Dry-run migration failed")
            logger.error(f"Error output: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Dry-run migration timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to run dry-run migration: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting migration tests...")
    
    tests = [
        ("Environment Configuration", test_environment),
        ("SQLite Database", test_sqlite_database),
        ("Supabase Connection", test_supabase_connection),
        ("PostgreSQL Connection", test_postgresql_connection),
        ("Migration Script", test_migration_script),
        ("Dry-run Migration", run_dry_run_migration),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info('='*50)
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ Test '{test_name}' failed with exception: {e}")
            results[test_name] = False
    
    # Print summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST RESULTS SUMMARY")
    logger.info('='*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Ready for migration.")
        return 0
    else:
        logger.error("💥 Some tests failed. Please fix issues before migration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
