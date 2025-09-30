# QA Environment Setup Guide

## 🎯 **Overview**

This guide sets up a completely isolated QA environment that mirrors your production setup but uses separate containers, databases, and configurations.

## 🏗️ **Architecture**

```
Production (joborra.com)          QA (qa.joborra.com)
├── joborra-api                   ├── joborra-qa-api
├── joborra-frontend              ├── joborra-qa-frontend  
├── joborra-caddy                 ├── joborra-qa-caddy
└── Supabase (prod project)       └── Supabase (qa project)
```

## 📋 **Prerequisites**

1. **GoDaddy DNS Access** - To add `qa.joborra.com` subdomain
2. **Supabase Account** - To create QA project
3. **GitHub Repository** - With secrets configured
4. **Server Access** - Same server as production

## 🌐 **Step 1: DNS Configuration (GoDaddy)**

1. **Log into GoDaddy**
2. **Go to "My Products" → "DNS"**
3. **Find `joborra.com` and click "Manage"**
4. **Add A record:**
   ```
   Type: A
   Name: qa
   Value: [Your Server IP Address]
   TTL: 600
   ```

## 🗄️ **Step 2: Supabase UAT Project Setup**

✅ **UAT Project Already Exists!**

Your QA environment will use the existing **`joborra-uat`** Supabase project:

- **Project URL**: `https://srnsfxmvgypscewsrrbs.supabase.co`
- **Database URL**: `postgresql://postgres.srnsfxmvgypscewsrrbs:[YOUR-PASSWORD]@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres`

**Next Steps:**
1. **Get UAT Credentials** from your Supabase dashboard:
   - **Anon Key**: Settings → API → anon key
   - **Service Key**: Settings → API → service_role key
   - **Database Password**: The password you used when creating the project

2. **Verify Storage Buckets:**
   - Ensure `master` bucket exists
   - Set appropriate permissions for QA testing

## 🔧 **Step 3: GitHub Secrets Setup**

Add these secrets to your GitHub repository:

### **Required Secrets:**
```
SSH_HOST - Your server IP
SSH_USER - Your server username  
SSH_PRIVATE_KEY - Your server private key
SSH_PASSWORD - Your server password (if using password auth)
REMOTE_APP_DIR - Your app directory path
```

### **QA-Specific Secrets:**
```
QA_BACKEND_ENV - QA backend environment variables
QA_FRONTEND_ENV - QA frontend environment variables
```

### **QA_BACKEND_ENV Content:**
```bash
# QA Environment Configuration (UAT Project)
NODE_ENV=qa
DEBUG=true
USE_SUPABASE=true
SUPABASE_URL=https://srnsfxmvgypscewsrrbs.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNybnNmeG12Z3lwc2Nld3NycmJzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkyNTg3MzAsImV4cCI6MjA3NDgzNDczMH0.t3od6YyP-cUpQ19_pbh89DdlQ74rroFP1egK5iuBDKw
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNybnNmeG12Z3lwc2Nld3NycmJzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTI1ODczMCwiZXhwIjoyMDc0ODM0NzMwfQ.-6B6SHaAfEQIGwHNwXTNKnXVreibPk23nSOxYjiI_A4
SUPABASE_DATABASE_URL=postgresql://postgres.srnsfxmvgypscewsrrbs:[YOUR-PASSWORD]@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres
CORS_ORIGINS=https://qa.joborra.com,https://www.qa.joborra.com
FRONTEND_ORIGIN=https://qa.joborra.com
API_PORT=8001
SECRET_KEY=your_qa_secret_key_here
GOOGLE_CLIENT_ID=your_qa_google_client_id
GOOGLE_CLIENT_SECRET=your_qa_google_client_secret
GOOGLE_GENAI_API_KEY=AIzaSyBR86EkZypycTZ6bRtj0z9WVSCX0QTqgCc
ADZUNA_APP_ID=your_qa_adzuna_app_id
ADZUNA_APP_KEY=your_qa_adzuna_app_key
SUPABASE_STORAGE_BUCKET=master
MAX_FILE_SIZE=10485760
```

### **QA_FRONTEND_ENV Content:**
```bash
REACT_APP_API_URL=https://qa.joborra.com/api
REACT_APP_ENVIRONMENT=qa
REACT_APP_SUPABASE_URL=https://srnsfxmvgypscewsrrbs.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNybnNmeG12Z3lwc2Nld3NycmJzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkyNTg3MzAsImV4cCI6MjA3NDgzNDczMH0.t3od6YyP-cUpQ19_pbh89DdlQ74rroFP1egK5iuBDKw
```

## 🚀 **Step 4: Deployment Workflow**

### **Automatic Deployments:**
- **Push to `develop` branch** → Deploys to QA
- **Push to `main` branch** → Deploys to Production

### **Manual Deployments:**
1. Go to **Actions** tab in GitHub
2. Click **"CI QA"** workflow
3. Click **"Run workflow"**
4. Choose branch: `develop` or `qa`
5. Click **"Run workflow"**

## 🔧 **Step 5: Local QA Management**

### **QA Management Commands:**
```bash
# Navigate to QA directory
cd qa-environment

# Start QA environment
./qa-manage.sh start

# Stop QA environment  
./qa-manage.sh stop

# Restart QA environment
./qa-manage.sh restart

# View QA logs
./qa-manage.sh logs

# Check QA status
./qa-manage.sh status

# Build QA containers
./qa-manage.sh build

# Full QA deployment
./qa-manage.sh deploy

# Clean QA environment
./qa-manage.sh clean
```

## 🔍 **Step 6: Verification**

### **Check DNS Resolution:**
```bash
nslookup qa.joborra.com
```

### **Check QA Environment:**
```bash
# Check if QA containers are running
cd qa-environment
./qa-manage.sh status

# Check QA logs
./qa-manage.sh logs
```

### **Test QA URLs:**
- **QA Website**: https://qa.joborra.com
- **QA API**: https://qa.joborra.com/api
- **QA Health**: https://qa.joborra.com/api/health

## 📊 **Step 7: Monitoring**

### **QA Environment Status:**
```bash
# Check container status
docker ps | grep qa

# Check QA logs
docker logs joborra-qa-api
docker logs joborra-qa-frontend
docker logs joborra-qa-caddy

# Check QA network
docker network ls | grep qa
```

## 🎯 **Key Benefits**

1. **✅ Complete Isolation**: QA and Production are completely separate
2. **✅ No Conflicts**: Different ports, container names, and networks
3. **✅ Independent Scaling**: Each environment can be managed separately
4. **✅ Safe Testing**: QA changes don't affect production
5. **✅ Flexible Deployment**: Choose what to deploy and when
6. **✅ Easy Management**: Simple scripts for all operations

## 🚨 **Important Notes**

1. **Separate Supabase Projects**: QA uses its own Supabase project
2. **Different Ports**: QA uses ports 8001, 3001, 8080, 8443
3. **Isolated Networks**: QA has its own Docker network
4. **Separate Volumes**: QA has its own data volumes
5. **Independent SSL**: QA has its own SSL certificates

## 🔧 **Troubleshooting**

### **QA Not Starting:**
```bash
cd qa-environment
./qa-manage.sh logs
```

### **DNS Not Resolving:**
- Check GoDaddy DNS settings
- Wait for DNS propagation (5-10 minutes)
- Use `nslookup qa.joborra.com`

### **QA API Not Responding:**
```bash
# Check QA API container
docker logs joborra-qa-api

# Check QA API health
curl https://qa.joborra.com/api/
```

### **QA Frontend Not Loading:**
```bash
# Check QA frontend container
docker logs joborra-qa-frontend

# Check QA frontend URL
curl https://qa.joborra.com/
```

## 🎉 **Success!**

Once set up, you'll have:
- **Production**: https://joborra.com (unchanged)
- **QA**: https://qa.joborra.com (new isolated environment)

Both environments are completely independent and can be managed separately! 🚀
