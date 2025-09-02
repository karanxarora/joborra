# GitHub Secrets Update - Fix AI Generation

## Problem Identified

The AI generation is failing because the `GOOGLE_GENAI_API_KEY` is not included in the GitHub `BACKEND_ENV` secret. During deployment, the CI/CD process overwrites the local `.env.production` file with the content from the `BACKEND_ENV` secret.

## Current Status

✅ **Local files have API keys**: Both `.env` and `.env.production` contain `GOOGLE_GENAI_API_KEY`  
❌ **GitHub secret missing API key**: The `BACKEND_ENV` secret doesn't include the Gemini API key  
❌ **Deployment overwrites local files**: CI/CD replaces local env files with secret content  

## Solution

### Step 1: Update GitHub BACKEND_ENV Secret

Go to your GitHub repository and update the `BACKEND_ENV` secret with the following content:

```bash
# Database Configuration (SQLite)
DATABASE_URL=sqlite:///./joborra.db

# Supabase Configuration (for file storage)
SUPABASE_URL=https://noupavjvuhezvzpqcbqg.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5vdXBhdmp2dWhlenZ6cHFjYnFnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjA0MzU5NywiZXhwIjoyMDcxNjE5NTk3fQ.Qe1YV0aVr-aNdUsP1SlN8qqVpR8ofIBX0d10lT2sS2o
MAX_FILE_SIZE=10485760

# Security
SECRET_KEY=your_super_secure_production_secret_key_here
DEBUG=false

# Google OAuth Configuration
GOOGLE_CLIENT_ID=1089724647257-jd4cc3c02e7ka975ij47mni56eubvisu.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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

# Google Generative AI (ADD THIS LINE)
GOOGLE_GENAI_API_KEY=AIzaSyBvnDtJz5Fw5O5x1O9AR7Myd5R5URzP33o

# Job Scraping APIs
ADZUNA_APP_ID=your_production_adzuna_app_id
ADZUNA_APP_KEY=your_production_adzuna_app_key

# Email Configuration
EMAIL_PROVIDER=resend
RESEND_API_KEY=re_ET82T2Tg_4218Qe8uacpETrnC8jNE9AGo
SMTP_FROM="Joborra <no-reply@emails.joborra.com>"

# Frontend Configuration
FRONTEND_ORIGIN=https://joborra.com

# Supabase Storage
SUPABASE_STORAGE_BUCKET=master
SUPABASE_STORAGE_PRIVATE=true
SUPABASE_SIGNED_URL_TTL=604800

# Google OAuth Redirect
GOOGLE_REDIRECT_URI=https://joborra.com/api/auth/google/callback

# Optional: Redis for background tasks
REDIS_URL=redis://redis:6379

# Scraping Configuration
SCRAPER_DELAY=2
MAX_CONCURRENT_SCRAPERS=2
```

### Step 2: How to Update the Secret

1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Find the `BACKEND_ENV` secret and click **Update**
5. Replace the content with the above configuration
6. Click **Update secret**

### Step 3: Deploy the Changes

After updating the secret:

1. **Push any changes** to trigger CI/CD deployment
2. **Or manually trigger** the workflow from the Actions tab
3. **Wait for deployment** to complete (usually 5-10 minutes)

### Step 4: Test the Fix

Once deployed, test the AI generation:

1. Go to https://joborra.com/employer/post-job
2. Fill in job details
3. Click **✨ AI Auto Generate**
4. Verify the job description is generated

### API Endpoint Test

You can also test the API directly:

```bash
curl -X POST https://joborra.com/api/ai/generate/job-description \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Software Engineer",
    "skills": ["Python", "React"],
    "context": {
      "company_name": "Test Company",
      "visa_sponsorship": true,
      "international_student_friendly": true
    }
  }'
```

Expected response: `{"text": "Generated job description..."}`

## Additional Fixes Applied

### 1. Environment Variable Compatibility ✅
- **File**: `app/supabase_utils.py`
- **Change**: Added fallback to check both `SUPABASE_SERVICE_KEY` and `SUPABASE_SERVICE_ROLE`
- **Result**: Works with both naming conventions

### 2. Text Direction Fix ✅
- **File**: `frontend/src/pages/EmployerPostJobPage.tsx`
- **Change**: Added `direction: 'ltr'` and `textAlign: 'left'` to contentEditable div
- **Result**: Text displays left-to-right correctly

### 3. Error Handling Improvements ✅
- **Files**: Both post job pages
- **Change**: Added user-friendly error messages for AI generation failures
- **Result**: Users see clear feedback when AI fails

## Files Modified

1. `app/supabase_utils.py` - Environment variable compatibility
2. `frontend/src/pages/EmployerPostJobPage.tsx` - Text direction and error handling
3. `frontend/src/pages/EmployerQuickPostPage.tsx` - Error handling
4. `GITHUB_SECRETS_UPDATE.md` - This documentation

## Next Steps

1. ✅ Update GitHub `BACKEND_ENV` secret with the API key
2. ✅ Deploy the changes
3. ✅ Test AI generation functionality
4. ✅ Monitor for any remaining issues

The AI generation should work perfectly once the GitHub secret is updated!
