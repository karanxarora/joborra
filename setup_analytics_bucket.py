#!/usr/bin/env python3
"""
Script to create analytics bucket in Supabase for storing user data exports.
"""

import os
import sys
from supabase import create_client

# Set environment variables
os.environ["SUPABASE_URL"] = "https://noupavjvuhezvzpqcbqg.supabase.co"
os.environ["SUPABASE_SERVICE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5vdXBhdmp2dWhlenZ6cHFjYnFnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjA0MzU5NywiZXhwIjoyMDcxNjE5NTk3fQ.Qe1YV0aVr-aNdUsP1SlN8qqVpR8ofIBX0d10lT2sS2o"

def create_analytics_bucket():
    """Create analytics bucket for storing user data exports."""
    print("📊 Creating Analytics Bucket...")
    
    try:
        client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        # List existing buckets
        buckets_result = client.storage.list_buckets()
        if hasattr(buckets_result, 'error') and buckets_result.error:
            print(f"❌ Error listing buckets: {buckets_result.error}")
            return False
        
        bucket_names = [bucket.name for bucket in buckets_result]
        print(f"📋 Existing buckets: {bucket_names}")
        
        # Create analytics bucket if it doesn't exist
        analytics_bucket = "analytics-exports"
        
        if analytics_bucket in bucket_names:
            print(f"  ✅ Analytics bucket '{analytics_bucket}' already exists")
        else:
            print(f"  🔨 Creating analytics bucket '{analytics_bucket}'...")
            create_result = client.storage.create_bucket(
                analytics_bucket,
                options={"public": False}  # Keep private for sensitive data
            )
            
            if hasattr(create_result, 'error') and create_result.error:
                print(f"    ❌ Error creating bucket: {create_result.error}")
                return False
            else:
                print(f"    ✅ Analytics bucket '{analytics_bucket}' created successfully")
        
        # Test bucket access
        print(f"  🧪 Testing bucket access...")
        try:
            # Try to list files (should be empty initially)
            files_result = client.storage.from_(analytics_bucket).list()
            if hasattr(files_result, 'error') and files_result.error:
                print(f"    ❌ Error accessing bucket: {files_result.error}")
                return False
            else:
                print(f"    ✅ Analytics bucket is accessible")
                return True
        except Exception as e:
            print(f"    ❌ Error testing bucket access: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error creating analytics bucket: {e}")
        return False

def main():
    """Main function to create analytics bucket."""
    print("🚀 Analytics Bucket Setup")
    print("=" * 50)
    
    if create_analytics_bucket():
        print("\n🎉 Analytics bucket setup completed successfully!")
        print("\n📝 Next Steps:")
        print("1. Use the 'analytics-exports' bucket for storing user data exports")
        print("2. Create data export scripts to generate reports")
        print("3. Set up periodic exports for regular data analysis")
        return 0
    else:
        print("\n❌ Analytics bucket setup failed!")
        return 1

if __name__ == "__main__":
    exit(main())
