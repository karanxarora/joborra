#!/usr/bin/env python3
"""
Script to create missing Supabase storage buckets for Joborra app.
This script will create the required storage buckets if they don't exist.
"""

import os
import sys
from typing import List, Dict, Any

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def create_storage_buckets():
    """Create the required storage buckets in Supabase."""
    print("🪣 Setting up Supabase storage buckets...")
    
    try:
        from app.supabase_utils import get_supabase_client
        
        client = get_supabase_client()
        if not client:
            print("❌ Cannot get Supabase client")
            return False
        
        # Define required buckets with their configurations
        required_buckets = [
            {
                "name": "company-logos",
                "public": True,
                "file_size_limit": 5242880,  # 5MB
                "allowed_mime_types": ["image/png", "image/jpeg", "image/jpg", "image/webp", "image/svg+xml"]
            },
            {
                "name": "job-documents", 
                "public": True,
                "file_size_limit": 10485760,  # 10MB
                "allowed_mime_types": ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain", "text/markdown"]
            },
            {
                "name": "visa-documents",
                "public": False,  # Private bucket for sensitive documents
                "file_size_limit": 10485760,  # 10MB
                "allowed_mime_types": ["application/pdf", "image/png", "image/jpeg", "image/jpg", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
            }
        ]
        
        # Get existing buckets
        existing_buckets_result = client.storage.list_buckets()
        if hasattr(existing_buckets_result, 'error') and existing_buckets_result.error:
            print(f"❌ Error listing buckets: {existing_buckets_result.error}")
            return False
        
        existing_bucket_names = [bucket.name for bucket in existing_buckets_result]
        print(f"📋 Existing buckets: {existing_bucket_names}")
        
        created_buckets = []
        for bucket_config in required_buckets:
            bucket_name = bucket_config["name"]
            
            if bucket_name in existing_bucket_names:
                print(f"  ✅ Bucket '{bucket_name}' already exists")
                continue
            
            print(f"  🔨 Creating bucket '{bucket_name}'...")
            
            try:
                # Create the bucket
                create_result = client.storage.create_bucket(
                    bucket_name,
                    options={
                        "public": bucket_config["public"],
                        "file_size_limit": bucket_config["file_size_limit"],
                        "allowed_mime_types": bucket_config["allowed_mime_types"]
                    }
                )
                
                if hasattr(create_result, 'error') and create_result.error:
                    print(f"    ❌ Error creating bucket '{bucket_name}': {create_result.error}")
                    continue
                
                print(f"    ✅ Bucket '{bucket_name}' created successfully")
                created_buckets.append(bucket_name)
                
            except Exception as e:
                print(f"    ❌ Exception creating bucket '{bucket_name}': {e}")
                continue
        
        if created_buckets:
            print(f"\n🎉 Successfully created {len(created_buckets)} buckets: {created_buckets}")
        else:
            print("\n✅ All required buckets already exist")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up storage buckets: {e}")
        return False

def verify_buckets():
    """Verify that all required buckets exist and are accessible."""
    print("\n🔍 Verifying bucket setup...")
    
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
        
        print(f"📋 Available buckets: {bucket_names}")
        
        missing_buckets = []
        for bucket in required_buckets:
            if bucket not in bucket_names:
                missing_buckets.append(bucket)
        
        if missing_buckets:
            print(f"❌ Missing buckets: {missing_buckets}")
            return False
        else:
            print("✅ All required buckets are available")
            return True
        
    except Exception as e:
        print(f"❌ Error verifying buckets: {e}")
        return False

def test_bucket_access():
    """Test access to each bucket by attempting to list files."""
    print("\n🧪 Testing bucket access...")
    
    try:
        from app.supabase_utils import get_supabase_client
        
        client = get_supabase_client()
        if not client:
            print("❌ Cannot get Supabase client")
            return False
        
        buckets_to_test = ['resumes', 'company-logos', 'job-documents', 'visa-documents']
        
        for bucket_name in buckets_to_test:
            try:
                # Try to list files in the bucket
                files_result = client.storage.from_(bucket_name).list()
                if hasattr(files_result, 'error') and files_result.error:
                    print(f"  ❌ Cannot access bucket '{bucket_name}': {files_result.error}")
                    return False
                else:
                    print(f"  ✅ Bucket '{bucket_name}' is accessible")
            except Exception as e:
                print(f"  ❌ Error accessing bucket '{bucket_name}': {e}")
                return False
        
        print("✅ All buckets are accessible")
        return True
        
    except Exception as e:
        print(f"❌ Error testing bucket access: {e}")
        return False

def main():
    """Main function to set up Supabase storage buckets."""
    print("🚀 Supabase Storage Bucket Setup")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_KEY"):
        print("❌ Missing required environment variables:")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_SERVICE_KEY")
        print("\nPlease set these variables and try again.")
        return 1
    
    # Run setup steps
    steps = [
        ("Creating Storage Buckets", create_storage_buckets),
        ("Verifying Buckets", verify_buckets),
        ("Testing Bucket Access", test_bucket_access),
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
    print(f"📊 Setup Results: {passed}/{total} steps completed successfully")
    
    if passed == total:
        print("🎉 Supabase storage buckets are ready!")
        print("\nYou can now run the upload test again:")
        print("python test_supabase_uploads.py")
        return 0
    else:
        print("⚠️  Some setup steps failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
