#!/usr/bin/env python3
"""
Debug script to understand Supabase client behavior.
"""

import os
import sys
from supabase import create_client

# Set environment variables
os.environ["SUPABASE_URL"] = "https://noupavjvuhezvzpqcbqg.supabase.co"
os.environ["SUPABASE_SERVICE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5vdXBhdmp2dWhlenZ6cHFjYnFnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjA0MzU5NywiZXhwIjoyMDcxNjE5NTk3fQ.Qe1YV0aVr-aNdUsP1SlN8qqVpR8ofIBX0d10lT2sS2o"

def test_supabase_client():
    """Test Supabase client behavior."""
    print("🔍 Testing Supabase client behavior...")
    
    try:
        client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        # Test upload
        test_content = b"test content"
        filename = "test_file.txt"
        
        print("📤 Testing upload...")
        result = client.storage.from_("resumes").upload(
            filename,
            test_content,
            file_options={"content-type": "text/plain"}
        )
        
        print(f"Upload result type: {type(result)}")
        print(f"Upload result: {result}")
        
        if hasattr(result, 'error') and result.error:
            print(f"Upload error: {result.error}")
            return
        
        # Test get_public_url
        print("🔗 Testing get_public_url...")
        url_result = client.storage.from_("resumes").get_public_url(filename)
        
        print(f"URL result type: {type(url_result)}")
        print(f"URL result: {url_result}")
        
        # Check if it's a coroutine
        import asyncio
        if asyncio.iscoroutine(url_result):
            print("URL result is a coroutine, awaiting...")
            url_result = asyncio.run(url_result)
            print(f"After await - type: {type(url_result)}")
            print(f"After await - value: {url_result}")
        
        # Check attributes
        if hasattr(url_result, '__dict__'):
            print(f"URL result attributes: {url_result.__dict__}")
        
        # Try to access public_url attribute
        if hasattr(url_result, 'public_url'):
            print(f"public_url: {url_result.public_url}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_supabase_client()
