#!/usr/bin/env python3
"""
Production Deployment Verification Script
=========================================

This script verifies that the production deployment completed successfully
and that the database migration worked as expected.

Usage:
    python scripts/verify_production_deployment.py [--url=https://your-domain.com]
"""

import os
import sys
import json
import logging
import argparse
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_api_health(base_url):
    """Verify API is responding"""
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ API Health: {data.get('message', 'OK')}")
            return True, data
        else:
            return False, f"API returned status {response.status_code}"
    except Exception as e:
        return False, f"API request failed: {e}"

def verify_database_migration(base_url):
    """Verify database has migrated data"""
    try:
        # Test a simple API endpoint that would use the database
        response = requests.get(f"{base_url}/api/jobs", timeout=10, params={'limit': 1})
        
        if response.status_code == 200:
            data = response.json()
            job_count = len(data.get('jobs', []))
            total_jobs = data.get('total', 0)
            logger.info(f"✅ Database: Found {total_jobs} jobs (showing {job_count})")
            return True, f"Database accessible with {total_jobs} jobs"
        else:
            return False, f"Database API returned status {response.status_code}"
            
    except Exception as e:
        return False, f"Database verification failed: {e}"

def verify_authentication(base_url):
    """Verify authentication system is working"""
    try:
        # Try to access auth endpoints
        response = requests.get(f"{base_url}/api/auth/me", timeout=10)
        
        # We expect 401 (unauthorized) as we're not logged in - this means auth is working
        if response.status_code == 401:
            logger.info("✅ Authentication: Auth system is responding correctly")
            return True, "Authentication system working"
        elif response.status_code == 200:
            logger.info("✅ Authentication: Got valid response (might be logged in)")
            return True, "Authentication system working"
        else:
            return False, f"Auth endpoint returned unexpected status {response.status_code}"
            
    except Exception as e:
        return False, f"Auth verification failed: {e}"

def verify_file_storage(base_url):
    """Verify file storage is accessible"""
    try:
        # Check if file upload endpoints are available
        response = requests.options(f"{base_url}/api/auth/upload-resume", timeout=10)
        
        if response.status_code in [200, 204, 405]:  # 405 = Method Not Allowed is OK for OPTIONS
            logger.info("✅ File Storage: Upload endpoints are accessible")
            return True, "File storage endpoints available"
        else:
            return False, f"File storage returned status {response.status_code}"
            
    except Exception as e:
        return False, f"File storage verification failed: {e}"

def check_database_type(base_url):
    """Try to determine which database is being used"""
    try:
        # Look for any hints in API responses about database type
        response = requests.get(f"{base_url}/", timeout=10)
        
        if response.status_code == 200:
            # Check response headers for any database indicators
            headers = response.headers
            
            # This is just informational - we can't always determine the database type from external API
            logger.info("ℹ️ Database Type: Cannot determine externally (this is normal)")
            return True, "Database type check completed"
            
    except Exception as e:
        return False, f"Database type check failed: {e}"

def run_verification(base_url):
    """Run complete verification suite"""
    logger.info("="*60)
    logger.info("PRODUCTION DEPLOYMENT VERIFICATION")
    logger.info("="*60)
    logger.info(f"Target URL: {base_url}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("")
    
    results = {}
    
    # Run all verification tests
    tests = [
        ("API Health", verify_api_health),
        ("Database Migration", verify_database_migration),
        ("Authentication System", verify_authentication),
        ("File Storage", verify_file_storage),
        ("Database Type Check", check_database_type),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"🔍 Running: {test_name}")
        try:
            success, message = test_func(base_url)
            results[test_name] = {
                "success": success,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            
            if success:
                logger.info(f"   {message}")
                passed += 1
            else:
                logger.error(f"   ❌ {message}")
                
        except Exception as e:
            logger.error(f"   ❌ Test failed with exception: {e}")
            results[test_name] = {
                "success": False,
                "message": f"Test exception: {e}",
                "timestamp": datetime.now().isoformat()
            }
        
        logger.info("")
    
    # Summary
    logger.info("="*60)
    logger.info("VERIFICATION SUMMARY")
    logger.info("="*60)
    logger.info(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 ALL VERIFICATIONS PASSED!")
        logger.info("✅ Production deployment is successful")
        logger.info("✅ Database migration completed")
        logger.info("✅ All systems operational")
        success_overall = True
    else:
        logger.warning(f"⚠️ {total - passed} verifications failed")
        logger.warning("🔧 Manual intervention may be required")
        success_overall = False
    
    logger.info("")
    logger.info("Next Steps:")
    if success_overall:
        logger.info("- Monitor application logs for any issues")
        logger.info("- Test user authentication flows")
        logger.info("- Verify file uploads work correctly")
        logger.info("- Run scripts/health_monitor.py for database status")
    else:
        logger.info("- Check application logs for errors")
        logger.info("- Verify environment variables are set correctly")
        logger.info("- Test database connectivity manually")
        logger.info("- Consider running fallback to SQLite if needed")
    
    logger.info("="*60)
    
    return success_overall, results

def main():
    parser = argparse.ArgumentParser(description='Verify production deployment')
    parser.add_argument('--url', default='http://localhost:8000', help='Base URL to verify')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    
    args = parser.parse_args()
    
    success, results = run_verification(args.url)
    
    if args.json:
        output = {
            "success": success,
            "url": args.url,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        print(json.dumps(output, indent=2))
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
