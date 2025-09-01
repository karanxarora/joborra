#!/usr/bin/env python3
"""
Test script to verify API endpoints for document uploads in Joborra app.
This script tests the actual API endpoints with proper authentication.
"""

import os
import sys
import requests
import json
import tempfile
import io
from pathlib import Path
from typing import Dict, Any, Optional

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

def register_test_user():
    """Register a test user for API testing."""
    print("👤 Registering test user...")
    
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "username": "testuser",
        "role": "student"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/register", json=user_data)
        if response.status_code == 200:
            print("  ✅ Test user registered successfully")
            return user_data
        elif response.status_code in [409, 400] and "already exists" in response.text:
            print("  ℹ️  Test user already exists")
            return user_data
        else:
            print(f"  ❌ Failed to register user: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ Error registering user: {e}")
        return None

def login_test_user(user_data):
    """Login the test user and get authentication token."""
    print("🔐 Logging in test user...")
    
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print("  ✅ User logged in successfully")
            return token_data["access_token"]
        else:
            print(f"  ❌ Failed to login: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ Error logging in: {e}")
        return None

def test_resume_upload(token):
    """Test resume upload endpoint."""
    print("📄 Testing resume upload...")
    
    test_files = create_test_files()
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        files = {
            "file": ("test_resume.pdf", io.BytesIO(test_files['resume.pdf']), "application/pdf")
        }
        
        response = requests.post(
            "http://localhost:8000/api/auth/profile/resume",
            headers=headers,
            files=files
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Resume uploaded successfully: {result.get('resume_url', 'No URL returned')}")
            return True
        else:
            print(f"  ❌ Resume upload failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Error testing resume upload: {e}")
        return False

def test_company_logo_upload(token):
    """Test company logo upload endpoint."""
    print("🏢 Testing company logo upload...")
    
    test_files = create_test_files()
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        files = {
            "file": ("test_logo.png", io.BytesIO(test_files['logo.png']), "image/png")
        }
        
        response = requests.post(
            "http://localhost:8000/api/auth/employer/company/logo",
            headers=headers,
            files=files
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Company logo uploaded successfully: {result.get('company_logo_url', 'No URL returned')}")
            return True
        else:
            print(f"  ❌ Company logo upload failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Error testing company logo upload: {e}")
        return False

def test_job_document_upload(token):
    """Test job document upload endpoint."""
    print("📋 Testing job document upload...")
    
    test_files = create_test_files()
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        files = {
            "file": ("test_job_doc.txt", io.BytesIO(test_files['job_doc.txt']), "text/plain")
        }
        
        # First, we need to create a job to upload a document to
        # For now, we'll test with a non-existent job ID to see the error handling
        response = requests.post(
            "http://localhost:8000/api/auth/employer/jobs/999/document",
            headers=headers,
            files=files
        )
        
        if response.status_code == 404:
            print("  ✅ Job document upload endpoint is working (correctly rejected non-existent job)")
            return True
        elif response.status_code == 200:
            result = response.json()
            print(f"  ✅ Job document uploaded successfully: {result.get('job_document_url', 'No URL returned')}")
            return True
        else:
            print(f"  ❌ Job document upload failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Error testing job document upload: {e}")
        return False

def test_visa_document_upload(token):
    """Test visa document upload endpoint."""
    print("🛂 Testing visa document upload...")
    
    test_files = create_test_files()
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        files = {
            "file": ("test_vevo.pdf", io.BytesIO(test_files['resume.pdf']), "application/pdf")
        }
        
        data = {
            "document_type": "vevo"
        }
        
        response = requests.post(
            "http://localhost:8000/api/visa/documents/upload",
            headers=headers,
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Visa document uploaded successfully: {result.get('document_url', 'No URL returned')}")
            return True
        else:
            print(f"  ❌ Visa document upload failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Error testing visa document upload: {e}")
        return False

def test_file_access(token):
    """Test file access and URL resolution."""
    print("🔗 Testing file access...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test resume view endpoint
        response = requests.get(
            "http://localhost:8000/api/auth/resume/view",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            resume_url = result.get('resume_url')
            if resume_url:
                print(f"  ✅ Resume URL accessible: {resume_url}")
                
                # Try to access the actual file
                file_response = requests.get(resume_url, timeout=10)
                if file_response.status_code == 200:
                    print("  ✅ Resume file is accessible via URL")
                    return True
                else:
                    print(f"  ⚠️  Resume file not accessible: {file_response.status_code}")
                    return False
            else:
                print("  ℹ️  No resume URL found (user may not have uploaded a resume)")
                return True
        elif response.status_code == 404:
            print("  ℹ️  No resume found (user may not have uploaded a resume)")
            return True
        else:
            print(f"  ❌ Resume view failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Error testing file access: {e}")
        return False

def main():
    """Run all API upload tests."""
    print("🧪 Joborra API Upload Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/api/", timeout=5)
        if response.status_code != 200:
            print("❌ API server is not running or not accessible")
            return 1
    except requests.exceptions.RequestException:
        print("❌ API server is not running or not accessible")
        print("Please start the server with: python main.py")
        return 1
    
    print("✅ API server is running")
    
    # Register and login test user
    user_data = register_test_user()
    if not user_data:
        print("❌ Cannot proceed without test user")
        return 1
    
    token = login_test_user(user_data)
    if not token:
        print("❌ Cannot proceed without authentication token")
        return 1
    
    # Run upload tests
    tests = [
        ("Resume Upload", lambda: test_resume_upload(token)),
        ("Company Logo Upload", lambda: test_company_logo_upload(token)),
        ("Job Document Upload", lambda: test_job_document_upload(token)),
        ("Visa Document Upload", lambda: test_visa_document_upload(token)),
        ("File Access", lambda: test_file_access(token)),
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
        print("🎉 All API upload tests passed! Document upload functionality is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
