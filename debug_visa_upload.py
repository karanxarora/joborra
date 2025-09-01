#!/usr/bin/env python3
"""
Debug script to test visa document upload.
"""

import requests
import json
import io

def test_visa_upload():
    """Test visa document upload."""
    print("🛂 Testing visa document upload...")
    
    # Login as student
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create test PDF content
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test VEVO Document) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
299
%%EOF"""
    
    # Test upload
    files = {
        "file": ("test_vevo.pdf", io.BytesIO(pdf_content), "application/pdf")
    }
    
    response = requests.post(
        "http://localhost:8000/api/auth/visa/documents/upload?document_type=vevo",
        headers=headers,
        files=files
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response text: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Visa document uploaded successfully: {result.get('document_url')}")
    else:
        print(f"❌ Visa document upload failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_visa_upload()
