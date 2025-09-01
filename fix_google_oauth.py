#!/usr/bin/env python3
"""
Script to fix Google OAuth redirect URI issue.
"""

import os
import re

def fix_google_oauth_redirect_uri():
    """Fix the Google OAuth redirect URI in .env file."""
    print("🔧 Fixing Google OAuth Redirect URI...")
    
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print(f"❌ {env_file} file not found")
        return False
    
    # Read the current .env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Check current redirect URI
    current_match = re.search(r'GOOGLE_REDIRECT_URI=(.+)', content)
    if current_match:
        current_uri = current_match.group(1)
        print(f"  📋 Current Redirect URI: {current_uri}")
        
        # Check if it's pointing to port 3000 instead of 8000
        if ":3000/" in current_uri:
            print("  ⚠️  Redirect URI is pointing to port 3000 (frontend) instead of 8000 (backend)")
            
            # Fix the redirect URI
            fixed_uri = current_uri.replace(":3000/", ":8000/")
            new_content = content.replace(current_uri, fixed_uri)
            
            # Write the fixed content back
            with open(env_file, 'w') as f:
                f.write(new_content)
            
            print(f"  ✅ Fixed Redirect URI: {fixed_uri}")
            return True
        else:
            print("  ✅ Redirect URI appears to be correct")
            return True
    else:
        print("  ❌ GOOGLE_REDIRECT_URI not found in .env file")
        return False

def check_google_oauth_configuration():
    """Check Google OAuth configuration for production issues."""
    print("\n🔍 Checking Google OAuth Configuration for Production...")
    
    issues = []
    
    # Check if using localhost in production
    if os.path.exists(".env"):
        with open(".env", 'r') as f:
            content = f.read()
        
        if "localhost" in content:
            issues.append("⚠️  Using localhost URLs - these won't work in production")
        
        if ":3000" in content:
            issues.append("⚠️  Frontend port 3000 references - should be production domain")
        
        if ":8000" in content:
            issues.append("⚠️  Backend port 8000 references - should be production domain")
    
    if issues:
        print("  🚨 Production Issues Found:")
        for issue in issues:
            print(f"    {issue}")
        
        print("\n  🔧 Production Configuration Needed:")
        print("    1. Update GOOGLE_REDIRECT_URI to your production domain")
        print("    2. Update FRONTEND_ORIGIN to your production domain")
        print("    3. Configure Google OAuth in Google Console for production domain")
        print("    4. Add authorized origins and redirect URIs in Google Console")
    else:
        print("  ✅ No obvious production issues found")
    
    return len(issues) == 0

def test_google_oauth_after_fix():
    """Test Google OAuth after the fix."""
    print("\n🧪 Testing Google OAuth After Fix...")
    
    import requests
    
    try:
        # Test the Google login endpoint
        response = requests.get("http://localhost:8000/api/auth/google/login", allow_redirects=False)
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"  📋 Redirect Location: {location[:100]}...")
            
            # Check if redirect URI is now correct
            if "localhost:8000" in location:
                print("  ✅ Redirect URI is now pointing to correct backend port")
                return True
            else:
                print("  ❌ Redirect URI still incorrect")
                return False
        else:
            print(f"  ❌ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing Google OAuth: {e}")
        return False

def main():
    """Main function to fix Google OAuth issues."""
    print("🔧 Google OAuth Fix Tool")
    print("=" * 50)
    
    steps = [
        ("Fixing Redirect URI", fix_google_oauth_redirect_uri),
        ("Checking Production Config", check_google_oauth_configuration),
        ("Testing After Fix", test_google_oauth_after_fix),
    ]
    
    passed = 0
    total = len(steps)
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        try:
            if step_func():
                passed += 1
            else:
                print(f"❌ {step_name} failed")
        except Exception as e:
            print(f"❌ {step_name} failed with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 Results: {passed}/{total} steps completed successfully")
    
    if passed == total:
        print("🎉 Google OAuth redirect URI fixed successfully!")
        print("\n📝 Next Steps:")
        print("1. Restart your backend server to pick up the new environment variables")
        print("2. Test Google OAuth login in your application")
        print("3. For production, update the redirect URI to your production domain")
        return 0
    else:
        print("⚠️  Some steps failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
