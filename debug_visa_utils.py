#!/usr/bin/env python3
"""
Debug script to test visa document upload utility function.
"""

import os
import sys

# Set environment variables
os.environ["SUPABASE_URL"] = "https://noupavjvuhezvzpqcbqg.supabase.co"
os.environ["SUPABASE_SERVICE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5vdXBhdmp2dWhlenZ6cHFjYnFnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjA0MzU5NywiZXhwIjoyMDcxNjE5NTk3fQ.Qe1YV0aVr-aNdUsP1SlN8qqVpR8ofIBX0d10lT2sS2o"

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_visa_upload_utils():
    """Test visa document upload utility function."""
    print("🛂 Testing visa document upload utility function...")
    
    try:
        from app.supabase_utils import upload_visa_document
        
        # Create test content
        test_content = b"Test VEVO document content"
        
        # Test upload
        result = upload_visa_document(999, "vevo", test_content, "test_vevo.pdf")
        
        if result:
            print(f"✅ Visa document uploaded successfully: {result}")
            return True
        else:
            print("❌ Visa document upload failed: No URL returned")
            return False
            
    except Exception as e:
        print(f"❌ Error testing visa document upload: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_visa_upload_utils()
