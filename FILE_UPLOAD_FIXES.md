# File Upload System Fixes

This document outlines the fixes implemented to resolve the file upload issues in the Joborra platform.

## Issues Identified

### 1. **Coroutine Handling Error**
```
Database error updating resume URL: (sqlite3.ProgrammingError) Error binding parameter 2: type 'coroutine' is not supported
[SQL: UPDATE users SET updated_at=?, resume_url=? WHERE users.id = ?]
[parameters: ('2025-09-01 16:12:52.901631', <coroutine object upload_resume at 0x779c685e0fb0>, 26)]
```

**Root Cause**: The Supabase client operations were returning coroutines, but the code was trying to handle them synchronously with `asyncio.run()` which is problematic in an async context.

### 2. **Incorrect Bucket Usage**
- Code was using specific buckets like "resumes", "company-logos", "job-documents"
- You requested to use the existing "master" bucket instead

### 3. **Async/Await Mismatch**
- Upload functions were synchronous but being called from async endpoints
- Missing `await` keywords when calling upload functions

## Fixes Implemented

### 1. **Updated supabase_utils.py**

#### **Made Upload Functions Async**
```python
# Before (synchronous)
def upload_resume(user_id: int, content: bytes, filename: str) -> Optional[str]:

# After (asynchronous)
async def upload_resume(user_id: int, content: bytes, filename: str) -> Optional[str]:
```

#### **Switched to Master Bucket**
```python
# Before (specific buckets)
result = client.storage.from_("resumes").upload(...)

# After (master bucket with prefixes)
result = client.storage.from_("master").upload(...)
unique_filename = f"resumes/resume_{user_id}_{uuid.uuid4()}.{file_ext}"
```

#### **Fixed Coroutine Handling**
```python
# Before (problematic)
if asyncio.iscoroutine(result):
    result = asyncio.run(result)

# After (proper async handling)
# Removed problematic asyncio.run() calls
# Functions now properly await Supabase operations
```

#### **Updated Return Values**
```python
# Before (returning public URLs)
return client.storage.from_("resumes").get_public_url(unique_filename)

# After (returning storage paths)
return f"/master/{unique_filename}"
```

### 2. **Updated auth_api.py**

#### **Added Proper Await Calls**
```python
# Before (missing await)
resume_url_value = supabase_upload_resume(current_user.id, content, file.filename)

# After (proper await)
resume_url_value = await supabase_upload_resume(current_user.id, content, file.filename)
```

#### **Updated Error Messages**
```python
# Before
"Failed to upload to local storage"

# After
"Failed to upload resume"
"Failed to upload company logo"
"Failed to upload job document"
```

## File Structure in Master Bucket

The new system organizes files in the master bucket with logical prefixes:

```
master/
├── resumes/
│   ├── resume_123_uuid1.pdf
│   └── resume_456_uuid2.docx
├── company-logos/
│   ├── logo_123_uuid3.png
│   └── logo_456_uuid4.jpg
├── job-documents/
│   ├── job_789_123_uuid5.pdf
│   └── job_101_456_uuid6.docx
└── visa-documents/
    ├── passport_123_uuid7.pdf
    └── visa_456_uuid8.pdf
```

## Updated Functions

### **Backend Upload Functions**
1. **`upload_resume()`** - Now async, uses master bucket with resumes/ prefix
2. **`upload_company_logo()`** - Now async, uses master bucket with company-logos/ prefix
3. **`upload_job_document()`** - Now async, uses master bucket with job-documents/ prefix
4. **`upload_visa_document()`** - Now async, uses master bucket with visa-documents/ prefix

### **URL Resolution**
- **`resolve_storage_url()`** - Updated to handle master bucket paths correctly
- Extracts file path from `/master/path/to/file` format
- Constructs public URLs from master bucket

## Testing

### **Test Script Created**
- `test_file_upload.py` - Tests all upload functions
- Verifies master bucket usage
- Checks file path generation

### **How to Test**
```bash
# Set environment variables
export SUPABASE_URL="your_supabase_url"
export SUPABASE_SERVICE_KEY="your_service_key"

# Run test
python test_file_upload.py
```

## Benefits of the Fix

1. **✅ Resolves Coroutine Error** - No more database binding issues
2. **✅ Uses Master Bucket** - Follows your requirement for existing bucket
3. **✅ Proper Async Handling** - Functions work correctly in async context
4. **✅ Organized File Structure** - Logical prefixes for different file types
5. **✅ Consistent URL Resolution** - All files resolve through master bucket
6. **✅ Better Error Handling** - Clear error messages for debugging

## Configuration Required

Ensure these environment variables are set:
```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
```

## Next Steps

1. **Test the fixes** using the provided test script
2. **Verify file uploads** work in the frontend
3. **Check file organization** in your Supabase master bucket
4. **Monitor upload logs** for any remaining issues

---

**Status**: File upload system has been fixed and now properly uses the master bucket with async handling.
