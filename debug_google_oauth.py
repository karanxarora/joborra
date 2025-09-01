#!/usr/bin/env python3
"""
Debug script to identify Google OAuth issues in production.
"""

import os
import sys
import requests
import json
from urllib.parse import urlencode

def check_google_oauth_config():
    """Check Google OAuth configuration."""
    print("🔍 Checking Google OAuth Configuration...")
    
    # Check environment variables
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    frontend_origin = os.getenv("FRONTEND_ORIGIN")
    
    print(f"  📋 Google Client ID: {google_client_id[:20]}..." if google_client_id else "  ❌ Google Client ID: NOT SET")
    print(f"  📋 Google Client Secret: {'SET' if google_client_secret else 'NOT SET'}")
    print(f"  📋 Frontend Origin: {frontend_origin}")
    
    if not google_client_id:
        print("  ❌ Google OAuth not configured - missing GOOGLE_CLIENT_ID")
        return False
    
    if not google_client_secret:
        print("  ❌ Google OAuth not configured - missing GOOGLE_CLIENT_SECRET")
        return False
    
    print("  ✅ Google OAuth environment variables are configured")
    return True

def test_google_oauth_endpoints():
    """Test Google OAuth endpoints."""
    print("\n🌐 Testing Google OAuth Endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test Google login endpoint
    try:
        response = requests.get(f"{base_url}/api/auth/google/login", allow_redirects=False)
        print(f"  📋 Google Login Endpoint: {response.status_code}")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"  📋 Redirect URL: {redirect_url[:100]}...")
            
            # Check if redirect URL contains correct client_id
            if 'client_id=' in redirect_url:
                print("  ✅ Google login endpoint is working")
                return True
            else:
                print("  ❌ Google login endpoint missing client_id")
                return False
        else:
            print(f"  ❌ Google login endpoint returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing Google login endpoint: {e}")
        return False

def test_google_token_validation():
    """Test Google token validation."""
    print("\n🔐 Testing Google Token Validation...")
    
    # This would require a real Google ID token, so we'll just test the endpoint structure
    base_url = "http://localhost:8000"
    
    try:
        # Test with invalid token to see error response
        response = requests.post(
            f"{base_url}/api/auth/oauth/google",
            json={"id_token": "invalid_token"},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"  📋 OAuth Google Endpoint: {response.status_code}")
        
        if response.status_code == 400:
            error_detail = response.json().get('detail', '')
            print(f"  📋 Error Response: {error_detail}")
            
            if "Invalid Google id_token" in error_detail:
                print("  ✅ OAuth endpoint is working (correctly rejected invalid token)")
                return True
            elif "Google token audience mismatch" in error_detail:
                print("  ⚠️  Token audience mismatch - this is the likely issue!")
                return False
            else:
                print("  ✅ OAuth endpoint is working")
                return True
        else:
            print(f"  ❌ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing OAuth endpoint: {e}")
        return False

def check_google_oauth_redirect_uri():
    """Check Google OAuth redirect URI configuration."""
    print("\n🔗 Checking Google OAuth Redirect URI...")
    
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not google_client_id:
        print("  ❌ Cannot check redirect URI - no client ID")
        return False
    
    # Check what redirect URI the backend is using
    base_url = "http://localhost:8000"
    expected_redirect_uri = f"{base_url}/api/auth/google/callback"
    
    print(f"  📋 Expected Redirect URI: {expected_redirect_uri}")
    
    # Test the callback endpoint
    try:
        response = requests.get(f"{base_url}/api/auth/google/callback", allow_redirects=False)
        print(f"  📋 Callback Endpoint: {response.status_code}")
        
        if response.status_code in [400, 422]:  # Expected for missing parameters
            print("  ✅ Callback endpoint is accessible")
            return True
        else:
            print(f"  ⚠️  Unexpected callback response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing callback endpoint: {e}")
        return False

def diagnose_common_issues():
    """Diagnose common Google OAuth issues."""
    print("\n🔍 Diagnosing Common Google OAuth Issues...")
    
    issues = []
    
    # Check if client ID matches between frontend and backend
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    if google_client_id:
        # Check if this is a localhost client ID being used in production
        if "localhost" in google_client_id or "127.0.0.1" in google_client_id:
            issues.append("❌ Client ID appears to be for localhost - may not work in production")
        
        # Check if client ID format is correct
        if not google_client_id.endswith(".apps.googleusercontent.com"):
            issues.append("❌ Client ID format appears incorrect")
    
    # Check frontend origin configuration
    frontend_origin = os.getenv("FRONTEND_ORIGIN")
    if frontend_origin and "localhost" in frontend_origin:
        issues.append("⚠️  Frontend origin is localhost - may cause issues in production")
    
    # Check if redirect URI is properly configured
    if not frontend_origin:
        issues.append("⚠️  FRONTEND_ORIGIN not set - may cause redirect issues")
    
    if issues:
        print("  🚨 Potential Issues Found:")
        for issue in issues:
            print(f"    {issue}")
    else:
        print("  ✅ No obvious configuration issues found")
    
    return len(issues) == 0

def main():
    """Main diagnostic function."""
    print("🔍 Google OAuth Diagnostic Tool")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    tests = [
        ("Google OAuth Configuration", check_google_oauth_config),
        ("Google OAuth Endpoints", test_google_oauth_endpoints),
        ("Google Token Validation", test_google_token_validation),
        ("Google OAuth Redirect URI", check_google_oauth_redirect_uri),
        ("Common Issues Diagnosis", diagnose_common_issues),
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
    print(f"📊 Diagnostic Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Google OAuth configuration appears to be working correctly!")
    else:
        print("⚠️  Issues found with Google OAuth configuration.")
        print("\n🔧 Common Solutions:")
        print("1. Ensure Google Client ID is configured for your production domain")
        print("2. Add your production domain to Google OAuth authorized origins")
        print("3. Update FRONTEND_ORIGIN to your production domain")
        print("4. Check that redirect URIs are properly configured in Google Console")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())
