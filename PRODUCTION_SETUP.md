# Production Environment Setup Guide

This guide covers the environment configuration needed for deploying Joborra with SQLite + Local Storage setup.

## GitHub Secrets Configuration

Set the following secrets in your GitHub repository for CI/CD deployment:

### Required Secrets

1. **SSH_HOST** - Your server's IP address or domain
2. **SSH_USER** - SSH username for server access
3. **SSH_PRIVATE_KEY** - SSH private key for authentication (or SSH_PASSWORD)
4. **REMOTE_APP_DIR** - Directory path on server where app will be deployed

### Backend Environment (BACKEND_ENV secret)

Create a secret named `BACKEND_ENV` with the following content:

```bash
# Database Configuration (SQLite)
DATABASE_URL=sqlite:///./joborra.db

# Local File Storage
LOCAL_STORAGE_PATH=/app/data
LOCAL_STORAGE_URL_PREFIX=/data
MAX_FILE_SIZE=10485760

# Security (CHANGE THESE!)
SECRET_KEY=your_super_secure_production_secret_key_here
DEBUG=false

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_production_google_client_id
GOOGLE_CLIENT_SECRET=your_production_google_client_secret

# Google Generative AI
GOOGLE_GENAI_API_KEY=your_production_gemini_api_key

# Job Scraping APIs
ADZUNA_APP_ID=your_production_adzuna_app_id
ADZUNA_APP_KEY=your_production_adzuna_app_key

# Optional: Redis for background tasks
REDIS_URL=redis://redis:6379

# Scraping Configuration
SCRAPER_DELAY=2
MAX_CONCURRENT_SCRAPERS=2

# Production optimizations
WORKERS=3
TIMEOUT=180

# CORS Origins (update with your domain)
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### Frontend Environment (FRONTEND_ENV secret)

Create a secret named `FRONTEND_ENV` with the following content:

```bash
# API URL - points to the backend API through Caddy reverse proxy
REACT_APP_API_URL=/api

# Production optimizations
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false
BUILD_PATH=build
```

## Local Development Environment

For local development, create a `.env` file in the root directory:

```bash
# Copy from .env.example and modify as needed
cp .env.example .env

# Key configurations for local dev:
DATABASE_URL=sqlite:///./joborra.db
LOCAL_STORAGE_PATH=./data
LOCAL_STORAGE_URL_PREFIX=/data
DEBUG=true
SECRET_KEY=your_local_development_secret_key
```

## Docker Volume Persistence

The production setup uses Docker volumes to persist:

1. **SQLite Database**: `./joborra.db` (including WAL and SHM files)
2. **File Storage**: `./data/` directory for uploads
3. **Caddy Config**: Automatic HTTPS certificates

## Important Notes

### SQLite File Handling
- The pipeline stops containers before rebuilding to avoid database locks
- WAL mode is enabled for better concurrency
- Database files are persisted via Docker volumes

### File Storage
- All uploads (resumes, logos, documents) stored in `./data/`
- Organized in subdirectories by file type and user ID
- Served through Caddy reverse proxy

### Security Considerations
1. **Change SECRET_KEY** in production
2. **Update CORS_ORIGINS** with your actual domain
3. **Set strong Google OAuth credentials**
4. **Use SSH keys** instead of passwords for deployment

### Backup Strategy
For production, implement regular backups of:
- `joborra.db` (and `.db-wal`, `.db-shm` files)
- `data/` directory containing all uploads

## Deployment Verification

After deployment, check:
1. API health: `https://your-domain.com/api/`
2. Database connection: Check logs for SQLite connection success
3. File storage: Test file upload functionality
4. Frontend: Ensure React app loads correctly

## Troubleshooting

### Common Issues

1. **Database Locked**: Ensure Docker containers are properly stopped before rebuild
2. **File Permissions**: Check that `data/` directory has correct permissions
3. **CORS Errors**: Verify CORS_ORIGINS includes your domain
4. **Upload Issues**: Check LOCAL_STORAGE_PATH and MAX_FILE_SIZE settings

### Logs

Check logs with:
```bash
docker compose logs api --tail=100
docker compose logs frontend --tail=100
docker compose logs caddy --tail=100
```

This setup provides a robust, SQLite-based production environment with local file storage and automated deployment.
