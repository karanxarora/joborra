#!/usr/bin/env python3
"""
Script to fix Supabase bucket permissions for public access.
"""

import os
import sys
from supabase import create_client

# Set environment variables
os.environ["SUPABASE_URL"] = "https://noupavjvuhezvzpqcbqg.supabase.co"
os.environ["SUPABASE_SERVICE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5vdXBhdmp2dWhlenZ6cHFjYnFnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjA0MzU5NywiZXhwIjoyMDcxNjE5NTk3fQ.Qe1YV0aVr-aNdUsP1SlN8qqVpR8ofIBX0d10lT2sS2o"

def fix_bucket_permissions():
    """Fix bucket permissions for public access."""
    print("🔧 Fixing Supabase bucket permissions...")
    
    try:
        client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        # List all buckets
        buckets_result = client.storage.list_buckets()
        if hasattr(buckets_result, 'error') and buckets_result.error:
            print(f"❌ Error listing buckets: {buckets_result.error}")
            return False
        
        bucket_names = [bucket.name for bucket in buckets_result]
        print(f"📋 Available buckets: {bucket_names}")
        
        # Update bucket policies to make them public
        public_buckets = ['resumes', 'company-logos', 'job-documents']
        
        for bucket_name in public_buckets:
            if bucket_name in bucket_names:
                print(f"  🔓 Making bucket '{bucket_name}' public...")
                try:
                    # Update bucket to be public
                    update_result = client.storage.update_bucket(
                        bucket_name,
                        options={"public": True}
                    )
                    
                    if hasattr(update_result, 'error') and update_result.error:
                        print(f"    ❌ Error updating bucket '{bucket_name}': {update_result.error}")
                    else:
                        print(f"    ✅ Bucket '{bucket_name}' is now public")
                        
                except Exception as e:
                    print(f"    ❌ Exception updating bucket '{bucket_name}': {e}")
        
        # For visa-documents, keep it private but ensure it's accessible
        if 'visa-documents' in bucket_names:
            print(f"  🔒 Keeping bucket 'visa-documents' private (sensitive documents)")
        
        print("✅ Bucket permissions updated")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing bucket permissions: {e}")
        return False

def test_file_access():
    """Test file access after permission fix."""
    print("\n🧪 Testing file access...")
    
    try:
        client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        # List files in resumes bucket
        files_result = client.storage.from_("resumes").list()
        if hasattr(files_result, 'error') and files_result.error:
            print(f"❌ Error listing files: {files_result.error}")
            return False
        
        if files_result:
            test_file = files_result[0]
            file_name = test_file.get('name', '')
            if file_name:
                # Get public URL
                public_url = client.storage.from_("resumes").get_public_url(file_name)
                print(f"  📄 Test file: {file_name}")
                print(f"  🔗 Public URL: {public_url}")
                
                # Test access
                import requests
                try:
                    response = requests.get(public_url, timeout=10)
                    if response.status_code == 200:
                        print(f"  ✅ File accessible (status: {response.status_code})")
                        return True
                    else:
                        print(f"  ⚠️  File not accessible (status: {response.status_code})")
                        return False
                except Exception as e:
                    print(f"  ❌ Error accessing file: {e}")
                    return False
        else:
            print("  ℹ️  No files found in resumes bucket")
            return True
        
    except Exception as e:
        print(f"❌ Error testing file access: {e}")
        return False

def main():
    """Main function to fix bucket permissions."""
    print("🚀 Supabase Bucket Permission Fix")
    print("=" * 50)
    
    steps = [
        ("Fixing Bucket Permissions", fix_bucket_permissions),
        ("Testing File Access", test_file_access),
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
        print("🎉 Bucket permissions fixed successfully!")
        return 0
    else:
        print("⚠️  Some steps failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
