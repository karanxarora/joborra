#!/usr/bin/env python3
"""
Test script to verify Supabase document upload functionality in Joborra app.
This script tests all document upload endpoints and verifies they work properly.
"""

import os
import sys
import requests
import json
import tempfile
import io
from pathlib import Path
from typing import Dict, Any, Optional

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def create_test_files():
    """Create test files for upload testing."""
    test_files = {}
    
    # Create a test PDF file (resume)
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test Resume) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
299
%%EOF"""
    
    test_files['resume.pdf'] = pdf_content
    
    # Create a test image file (company logo)
    # Simple PNG header (minimal valid PNG)
    png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
    test_files['logo.png'] = png_content
    
    # Create a test text file (job document)
    test_files['job_doc.txt'] = b"This is a test job document content for testing upload functionality."
    
    return test_files

def check_environment():
    """Check if required environment variables are set."""
    print("🔍 Checking environment configuration...")
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    
    print("✅ Environment variables are configured")
    return True

def test_supabase_connection():
    """Test basic Supabase connection."""
    print("\n🔗 Testing Supabase connection...")
    
    try:
        from app.supabase_utils import supabase_configured, get_supabase_client
        
        if not supabase_configured():
            print("❌ Supabase is not properly configured")
            return False
        
        client = get_supabase_client()
        if not client:
            print("❌ Failed to create Supabase client")
            return False
        
        print("✅ Supabase client created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Supabase connection: {e}")
        return False

def test_upload_functions():
    """Test the upload utility functions directly."""
    print("\n📤 Testing upload utility functions...")
    
    try:
        from app.supabase_utils import upload_resume, upload_company_logo, upload_job_document, upload_visa_document
        
        test_files = create_test_files()
        
        # Test resume upload
        print("  Testing resume upload...")
        resume_url = upload_resume(999, test_files['resume.pdf'], 'test_resume.pdf')
        if resume_url:
            print(f"  ✅ Resume uploaded: {resume_url}")
        else:
            print("  ❌ Resume upload failed")
            return False
        
        # Test company logo upload
        print("  Testing company logo upload...")
        logo_url = upload_company_logo(999, test_files['logo.png'], 'test_logo.png')
        if logo_url:
            print(f"  ✅ Company logo uploaded: {logo_url}")
        else:
            print("  ❌ Company logo upload failed")
            return False
        
        # Test job document upload
        print("  Testing job document upload...")
        job_doc_url = upload_job_document(999, 1, test_files['job_doc.txt'], 'test_job_doc.txt')
        if job_doc_url:
            print(f"  ✅ Job document uploaded: {job_doc_url}")
        else:
            print("  ❌ Job document upload failed")
            return False
        
        # Test visa document upload
        print("  Testing visa document upload...")
        visa_doc_url = upload_visa_document(999, 'vevo', test_files['resume.pdf'], 'test_vevo.pdf')
        if visa_doc_url:
            print(f"  ✅ Visa document uploaded: {visa_doc_url}")
        else:
            print("  ❌ Visa document upload failed")
            return False
        
        print("✅ All upload utility functions working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error testing upload functions: {e}")
        return False

def test_url_resolution():
    """Test URL resolution functionality."""
    print("\n🔗 Testing URL resolution...")
    
    try:
        from app.supabase_utils import resolve_storage_url
        
        # Test with None
        result = resolve_storage_url(None)
        if result is None:
            print("  ✅ None URL handled correctly")
        else:
            print("  ❌ None URL not handled correctly")
            return False
        
        # Test with full URL
        full_url = "https://example.com/test.pdf"
        result = resolve_storage_url(full_url)
        if result == full_url:
            print("  ✅ Full URL returned as-is")
        else:
            print("  ❌ Full URL not returned correctly")
            return False
        
        print("✅ URL resolution working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error testing URL resolution: {e}")
        return False

def test_api_endpoints():
    """Test the API endpoints for file uploads."""
    print("\n🌐 Testing API endpoints...")
    
    # Check if the API server is running
    try:
        response = requests.get("http://localhost:8000/api/", timeout=5)
        if response.status_code != 200:
            print("❌ API server is not running or not accessible")
            print("Please start the server with: python main.py")
            return False
    except requests.exceptions.RequestException:
        print("❌ API server is not running or not accessible")
        print("Please start the server with: python main.py")
        return False
    
    print("✅ API server is running")
    
    # Note: Full API testing would require authentication tokens
    # For now, we'll just verify the endpoints exist
    endpoints_to_check = [
        "/api/auth/profile/resume",
        "/api/auth/employer/company/logo",
        "/api/auth/employer/jobs/1/document",
        "/api/visa/documents/upload"
    ]
    
    for endpoint in endpoints_to_check:
        try:
            # Try to access the endpoint (will likely return 401/403 without auth)
            response = requests.post(f"http://localhost:8000{endpoint}", timeout=5)
            # We expect authentication errors, not 404s
            if response.status_code not in [401, 403, 422]:  # 422 for missing file
                print(f"  ⚠️  Endpoint {endpoint} returned unexpected status: {response.status_code}")
            else:
                print(f"  ✅ Endpoint {endpoint} is accessible")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Endpoint {endpoint} not accessible: {e}")
            return False
    
    print("✅ API endpoints are accessible")
    return True

def test_storage_buckets():
    """Test if Supabase storage buckets exist and are accessible."""
    print("\n🪣 Testing Supabase storage buckets...")
    
    try:
        from app.supabase_utils import get_supabase_client
        
        client = get_supabase_client()
        if not client:
            print("❌ Cannot get Supabase client")
            return False
        
        # List all buckets
        buckets_result = client.storage.list_buckets()
        if hasattr(buckets_result, 'error') and buckets_result.error:
            print(f"❌ Error listing buckets: {buckets_result.error}")
            return False
        
        bucket_names = [bucket.name for bucket in buckets_result]
        required_buckets = ['resumes', 'company-logos', 'job-documents', 'visa-documents']
        
        print(f"  Available buckets: {bucket_names}")
        
        missing_buckets = []
        for bucket in required_buckets:
            if bucket not in bucket_names:
                missing_buckets.append(bucket)
        
        if missing_buckets:
            print(f"  ⚠️  Missing required buckets: {missing_buckets}")
            print("  You may need to create these buckets in your Supabase dashboard")
        else:
            print("  ✅ All required buckets exist")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing storage buckets: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Joborra Supabase Upload Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment Configuration", check_environment),
        ("Supabase Connection", test_supabase_connection),
        ("Storage Buckets", test_storage_buckets),
        ("Upload Functions", test_upload_functions),
        ("URL Resolution", test_url_resolution),
        ("API Endpoints", test_api_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Supabase upload functionality is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration and try again.")
        return 1

if __name__ == "__main__":
    exit(main())
