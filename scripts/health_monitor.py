#!/usr/bin/env python3
"""
Database Health Monitor
=======================

This script monitors the health of both SQLite and Supabase databases
and can automatically switch between them if needed.

Usage:
    python scripts/health_monitor.py [--switch-to-sqlite] [--switch-to-supabase]
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sqlite_health():
    """Test SQLite database health"""
    try:
        import sqlite3
        
        db_path = "joborra.db"
        if not os.path.exists(db_path):
            return False, "SQLite database file not found"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM companies")
        company_count = cursor.fetchone()[0]
        conn.close()
        
        return True, f"SQLite healthy: {user_count} users, {company_count} companies"
        
    except Exception as e:
        return False, f"SQLite error: {e}"

def test_supabase_health():
    """Test Supabase database health"""
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not supabase_url or not supabase_service_key:
            return False, "Supabase credentials not configured"
        
        client = create_client(supabase_url, supabase_service_key)
        
        # Test basic connectivity
        users_result = client.table('users').select('id').limit(1).execute()
        companies_result = client.table('companies').select('id').limit(1).execute()
        
        # Get counts
        users_count_result = client.table('users').select('id', count='exact').execute()
        companies_count_result = client.table('companies').select('id', count='exact').execute()
        
        user_count = users_count_result.count
        company_count = companies_count_result.count
        
        return True, f"Supabase healthy: {user_count} users, {company_count} companies"
        
    except Exception as e:
        return False, f"Supabase error: {e}"

def get_current_database():
    """Get currently configured database"""
    use_supabase = os.getenv("USE_SUPABASE", "false").lower() == "true"
    return "Supabase" if use_supabase else "SQLite"

def switch_database(target):
    """Switch to specified database"""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        logger.error(f"Environment file {env_file} not found")
        return False
    
    try:
        # Read current env file
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update USE_SUPABASE setting
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith('USE_SUPABASE='):
                if target.lower() == 'supabase':
                    lines[i] = 'USE_SUPABASE=true\n'
                else:
                    lines[i] = 'USE_SUPABASE=false\n'
                updated = True
                break
        
        # Add USE_SUPABASE if not found
        if not updated:
            if target.lower() == 'supabase':
                lines.append('USE_SUPABASE=true\n')
            else:
                lines.append('USE_SUPABASE=false\n')
        
        # Write updated env file
        with open(env_file, 'w') as f:
            f.writelines(lines)
        
        logger.info(f"✅ Database switched to {target}")
        logger.info("⚠️ Restart the application for changes to take effect")
        return True
        
    except Exception as e:
        logger.error(f"Failed to switch database: {e}")
        return False

def generate_health_report():
    """Generate comprehensive health report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'current_database': get_current_database(),
        'sqlite': {'healthy': False, 'message': ''},
        'supabase': {'healthy': False, 'message': ''}
    }
    
    # Test SQLite
    sqlite_healthy, sqlite_msg = test_sqlite_health()
    report['sqlite']['healthy'] = sqlite_healthy
    report['sqlite']['message'] = sqlite_msg
    
    # Test Supabase
    supabase_healthy, supabase_msg = test_supabase_health()
    report['supabase']['healthy'] = supabase_healthy
    report['supabase']['message'] = supabase_msg
    
    return report

def main():
    parser = argparse.ArgumentParser(description='Monitor database health and switch between SQLite and Supabase')
    parser.add_argument('--switch-to-sqlite', action='store_true', help='Switch to SQLite database')
    parser.add_argument('--switch-to-supabase', action='store_true', help='Switch to Supabase database')
    parser.add_argument('--report', action='store_true', help='Generate health report only')
    parser.add_argument('--json', action='store_true', help='Output report in JSON format')
    
    args = parser.parse_args()
    
    # Generate health report
    report = generate_health_report()
    
    if args.json:
        import json
        print(json.dumps(report, indent=2))
        return
    
    # Display health status
    logger.info("="*50)
    logger.info("DATABASE HEALTH REPORT")
    logger.info("="*50)
    logger.info(f"Current Database: {report['current_database']}")
    logger.info(f"Timestamp: {report['timestamp']}")
    logger.info("")
    
    # SQLite status
    sqlite_status = "✅" if report['sqlite']['healthy'] else "❌"
    logger.info(f"{sqlite_status} SQLite: {report['sqlite']['message']}")
    
    # Supabase status
    supabase_status = "✅" if report['supabase']['healthy'] else "❌"
    logger.info(f"{supabase_status} Supabase: {report['supabase']['message']}")
    
    logger.info("")
    
    # Handle database switching
    if args.switch_to_sqlite:
        if report['sqlite']['healthy']:
            switch_database('SQLite')
        else:
            logger.error("❌ Cannot switch to SQLite: database is unhealthy")
            sys.exit(1)
    
    elif args.switch_to_supabase:
        if report['supabase']['healthy']:
            switch_database('Supabase')
        else:
            logger.error("❌ Cannot switch to Supabase: database is unhealthy")
            sys.exit(1)
    
    else:
        # Provide recommendations
        current_db = report['current_database'].lower()
        current_healthy = report[current_db.replace('sqlite', 'sqlite')]['healthy']
        
        if not current_healthy:
            logger.warning(f"⚠️ Current database ({report['current_database']}) is unhealthy!")
            
            # Suggest fallback
            fallback_db = 'sqlite' if current_db == 'supabase' else 'supabase'
            fallback_healthy = report[fallback_db]['healthy']
            
            if fallback_healthy:
                logger.info(f"💡 Consider switching to {fallback_db.title()}: python scripts/health_monitor.py --switch-to-{fallback_db}")
            else:
                logger.error("❌ Both databases are unhealthy! Manual intervention required.")
        else:
            logger.info(f"✅ Current database ({report['current_database']}) is healthy")
    
    logger.info("="*50)

if __name__ == "__main__":
    main()
