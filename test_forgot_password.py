#!/usr/bin/env python3
"""
Test script for forgot password functionality
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/auth"

def test_forgot_password():
    """Test the forgot password flow"""
    print("🧪 Testing Forgot Password Functionality")
    print("=" * 50)
    
    # Test 1: Request password reset for non-existent email
    print("\n1. Testing forgot password with non-existent email...")
    try:
        response = requests.post(f"{API_BASE}/forgot-password", json={
            "email": "nonexistent@example.com"
        })
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print("   ✅ Success: Non-existent email handled gracefully")
        else:
            print("   ❌ Failed: Expected 200 status")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Request password reset with invalid email format
    print("\n2. Testing forgot password with invalid email format...")
    try:
        response = requests.post(f"{API_BASE}/forgot-password", json={
            "email": "invalid-email"
        })
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 422:
            print("   ✅ Success: Invalid email format properly validated")
        else:
            print("   ❌ Failed: Expected 422 validation error")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Test reset password with invalid token
    print("\n3. Testing reset password with invalid token...")
    try:
        response = requests.post(f"{API_BASE}/reset-password", json={
            "token": "invalid-token",
            "new_password": "newpassword123"
        })
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 400:
            print("   ✅ Success: Invalid token properly rejected")
        else:
            print("   ❌ Failed: Expected 400 status for invalid token")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Test reset password with short password
    print("\n4. Testing reset password with short password...")
    try:
        response = requests.post(f"{API_BASE}/reset-password", json={
            "token": "valid-token-here",
            "new_password": "123"
        })
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 422:
            print("   ✅ Success: Short password properly validated")
        else:
            print("   ❌ Failed: Expected 422 validation error for short password")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Forgot Password Tests Completed!")
    print("\nNote: To test with a real email, you'll need to:")
    print("1. Start the backend server")
    print("2. Have email configuration set up")
    print("3. Use a real email address that exists in your database")

if __name__ == "__main__":
    test_forgot_password()
