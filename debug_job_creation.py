#!/usr/bin/env python3
"""
Debug script to test job creation.
"""

import requests
import json

def test_job_creation():
    """Test job creation with minimal data."""
    print("🔨 Testing job creation...")
    
    # Login as employer
    login_data = {
        "email": "employer2@example.com",
        "password": "testpass123"
    }
    
    response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to create a job with minimal data
    job_data = {
        "title": "Test Job",
        "description": "A comprehensive test job for document upload testing. This position requires strong technical skills and experience in software development.",
        "location": "Sydney, NSW",
        "city": "Sydney",
        "state": "NSW",
        "salary_min": 80000,
        "salary_max": 120000,
        "employment_type": "full-time",
        "job_type": "permanent",
        "role_category": "STUDY_ALIGNED_PROFESSIONAL",
        "experience_level": "mid-level",
        "remote_option": True,
        "visa_sponsorship": True,
        "international_student_friendly": True
    }
    
    response = requests.post(
        "http://localhost:8000/api/auth/employer/jobs",
        headers=headers,
        json=job_data
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response text: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Job created successfully with ID: {result.get('id')}")
        return result.get('id')
    else:
        print(f"❌ Job creation failed: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    test_job_creation()
