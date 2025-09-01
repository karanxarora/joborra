# Supabase Setup Guide for File Uploads

This guide will help you set up Supabase to enable file uploads in the Joborra platform.

## Current Issue

The file upload functionality is currently failing with a 500 error because:
- **Supabase environment variables are not configured**
- **`supabase_configured()` returns `False`**
- **File upload endpoints throw errors when storage is not available**

## Required Environment Variables

You need to set these environment variables for file uploads to work:

```bash
# Supabase Project Configuration
export SUPABASE_URL="https://your-project-id.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-role-key-here"
export SUPABASE_ANON_KEY="your-anon-key-here"
```

## How to Get These Values

### 1. **SUPABASE_URL**
- Go to your [Supabase Dashboard](https://supabase.com/dashboard)
- Select your project
- Go to **Settings** → **API**
- Copy the **Project URL**

### 2. **SUPABASE_SERVICE_KEY**
- In the same **Settings** → **API** section
- Copy the **service_role** key (starts with `eyJ...`)
- **⚠️ Keep this secret - it has admin privileges**

### 3. **SUPABASE_ANON_KEY**
- In the same **Settings** → **API** section
- Copy the **anon** key (starts with `eyJ...`)
- This is safe to expose publicly

## Setting Environment Variables

### **Option 1: Export in Current Session**
```bash
export SUPABASE_URL="https://your-project-id.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-role-key"
export SUPABASE_ANON_KEY="your-anon-key"
```

### **Option 2: Add to ~/.bashrc or ~/.zshrc**
```bash
echo 'export SUPABASE_URL="https://your-project-id.supabase.co"' >> ~/.bashrc
echo 'export SUPABASE_SERVICE_KEY="your-service-role-key"' >> ~/.bashrc
echo 'export SUPABASE_ANON_KEY="your-anon-key"' >> ~/.bashrc
source ~/.bashrc
```

### **Option 3: Create .env file**
```bash
# Create .env file in project root
cat > .env << EOF
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key
EOF

# Load environment variables
export $(cat .env | xargs)
```

## Required Supabase Setup

### 1. **Create Storage Bucket**
- Go to **Storage** in your Supabase dashboard
- Create a bucket named **`master`**
- Set it to **Public** (for file access)

### 2. **Set Storage Policies**
- Go to **Storage** → **Policies**
- Add policies for the `master` bucket:

```sql
-- Allow authenticated users to upload files
CREATE POLICY "Allow authenticated uploads" ON storage.objects
FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Allow public access to view files
CREATE POLICY "Allow public viewing" ON storage.objects
FOR SELECT USING (true);
```

### 3. **Enable Row Level Security (RLS)**
- Go to **Storage** → **Settings**
- Enable **Row Level Security**

## Testing the Setup

### 1. **Check Environment Variables**
```bash
echo "SUPABASE_URL: $SUPABASE_URL"
echo "SUPABASE_SERVICE_KEY: ${SUPABASE_SERVICE_KEY:0:20}..."
echo "SUPABASE_ANON_KEY: ${SUPABASE_ANON_KEY:0:20}..."
```

### 2. **Test Supabase Connection**
```bash
python -c "
from app.supabase_utils import supabase_configured
print(f'Supabase configured: {supabase_configured()}')
"
```

### 3. **Test File Upload**
- Restart your backend server
- Try uploading a resume in the frontend
- Check backend logs for any errors

## File Structure in Master Bucket

Once configured, files will be organized as:

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

## Troubleshooting

### **Error: "File upload service is currently unavailable"**
- Check if environment variables are set correctly
- Verify Supabase project is active
- Check if `master` bucket exists

### **Error: "Storage upload failed"**
- Check Supabase service key permissions
- Verify storage policies are set correctly
- Check backend logs for detailed error messages

### **Files not accessible**
- Ensure bucket is set to public
- Check storage policies allow public viewing
- Verify file paths are correct

## Security Notes

- **Service Key**: Has admin privileges, keep secret
- **Anon Key**: Safe to expose publicly
- **Storage Policies**: Configure carefully to control access
- **File Validation**: Backend validates file types and sizes

## Next Steps

1. **Set up Supabase project** if you haven't already
2. **Configure environment variables** as shown above
3. **Create master bucket** with proper policies
4. **Restart backend server** to load new environment
5. **Test file uploads** in the frontend

---

**Status**: File upload system is ready but requires Supabase configuration to function.
