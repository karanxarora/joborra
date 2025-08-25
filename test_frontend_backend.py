#!/usr/bin/env python3
"""
Test script to verify all frontend-backend API connections
"""
import pytest
pytestmark = pytest.mark.skip(reason="Manual connectivity script; skip in unit test runs")
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000/api"

def test_endpoint(method, endpoint, data=None, headers=None, description=""):
    """Test a single API endpoint"""
    url = f"{API_BASE}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            return f"❌ {description}: Unsupported method {method}"
            
        status = "✅" if response.status_code < 400 else "❌"
        return f"{status} {description}: {response.status_code} - {response.text[:100]}"
    except Exception as e:
        return f"❌ {description}: Error - {str(e)}"

def main():
    print("🔍 Testing Joborra Frontend-Backend Connections")
    print("=" * 60)
    
    # Test basic API health
    print("\n📊 Basic API Tests:")
    print(test_endpoint("GET", "/", description="API Health Check"))
    
    # Test job-related endpoints
    print("\n💼 Job API Tests:")
    print(test_endpoint("GET", "/jobs/search?per_page=5", description="Job Search"))
    print(test_endpoint("GET", "/jobs/visa-friendly?per_page=5", description="Visa-Friendly Jobs"))
    print(test_endpoint("GET", "/jobs/student-friendly?per_page=5", description="Student-Friendly Jobs"))
    
    # Test the problematic stats endpoint
    print(test_endpoint("GET", "/jobs/stats", description="Job Statistics"))
    
    # Test authentication endpoints
    print("\n🔐 Authentication API Tests:")
    print(test_endpoint("POST", "/auth/register", 
                       data={"email": "test@example.com", "password": "testpass123", "role": "student"},
                       description="User Registration"))
    
    # Test a job by ID (if any exist)
    print("\n🔍 Individual Job Tests:")
    print(test_endpoint("GET", "/jobs/1", description="Get Job by ID"))
    
    # Test visa keywords
    print("\n📝 Visa Keywords Tests:")
    print(test_endpoint("GET", "/visa-keywords", description="Get Visa Keywords"))
    
    print("\n" + "=" * 60)
    print("✅ Test completed at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()
