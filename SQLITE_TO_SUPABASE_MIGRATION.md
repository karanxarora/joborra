# SQLite to Supabase Migration Guide

This guide explains how to migrate your Joborra application from SQLite to Supabase, supporting both local development and production environments.

## Overview

The migration system provides:
- **Seamless migration** from SQLite to Supabase PostgreSQL
- **File migration** from local storage to Supabase Storage
- **Backward compatibility** with existing user authentication
- **Production-ready** deployment with CI/CD integration
- **Rollback capabilities** in case of migration failures

## Architecture

### Before Migration
```
Local/Production: SQLite + Local File Storage
├── joborra.db (SQLite database)
├── data/
│   ├── resumes/
│   ├── company_logos/
│   ├── job_docs/
│   └── visa_documents/
```

### After Migration
```
Local/Production: Supabase PostgreSQL + Supabase Storage
├── Supabase PostgreSQL (cloud database)
├── Supabase Storage Buckets:
│   ├── resumes
│   ├── company-logos
│   ├── job-documents
│   └── visa-documents
```

## Prerequisites

### 1. Supabase Setup
1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Note down your:
   - **Project URL**: `https://your-project.supabase.co`
   - **Anon Key**: Public key for client-side usage
   - **Service Key**: Private key for server-side operations

### 2. Environment Variables
Set the following environment variables:

```bash
# Required for migration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# Enable Supabase usage
USE_SUPABASE=true
DATABASE_TYPE=supabase

# File storage configuration
MAX_FILE_SIZE=10485760
SUPABASE_STORAGE_BUCKET=master
```

### 3. Python Dependencies
```bash
pip install supabase psycopg2-binary
```

## Local Migration

### Step 1: Prepare Environment
```bash
# Copy the example environment file
cp env.supabase.example .env

# Edit .env with your Supabase credentials
nano .env
```

### Step 2: Run Migration (Dry Run)
```bash
# Test migration without making changes
python migrate_sqlite_to_supabase.py --dry-run
```

### Step 3: Run Actual Migration
```bash
# Run the migration
python migrate_sqlite_to_supabase.py --batch-size=500

# Or force overwrite existing data
python migrate_sqlite_to_supabase.py --force --batch-size=500
```

### Step 4: Update Application Configuration
The application will automatically detect the `USE_SUPABASE=true` setting and switch to Supabase.

### Step 5: Restart Application
```bash
# If using Docker
docker-compose down
docker-compose up --build

# If running directly
python main.py
```

## Production Migration via CI/CD

### Step 1: Configure GitHub Secrets
Add these secrets to your GitHub repository:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# Deployment Configuration
SSH_HOST=your-server-ip
SSH_USER=your-ssh-user
SSH_PRIVATE_KEY=your-ssh-private-key
REMOTE_APP_DIR=/path/to/your/app

# Application Secrets
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
# ... other app secrets
```

### Step 2: Deploy with Migration
Push to main branch or trigger manual deployment:

```bash
git push origin main
```

Or use the manual workflow with options:
- **Dry Run**: Test migration without changes
- **Force Migration**: Overwrite existing Supabase data

### Step 3: Monitor Deployment
Check the GitHub Actions workflow for:
- Migration progress
- Deployment status
- Verification results

## Migration Script Details

### migrate_sqlite_to_supabase.py

The migration script handles:

1. **Schema Migration**
   - Analyzes SQLite table structures
   - Creates equivalent PostgreSQL tables in Supabase
   - Converts SQLite types to PostgreSQL types

2. **Data Migration**
   - Migrates all records in configurable batches
   - Preserves relationships and constraints
   - Handles JSON fields and special data types

3. **File Migration**
   - Uploads local files to Supabase Storage buckets
   - Updates database URLs to point to Supabase Storage
   - Maintains file organization and access permissions

4. **Verification**
   - Compares record counts between databases
   - Verifies file accessibility
   - Reports migration statistics

### Usage Options

```bash
# Dry run (simulation only)
python migrate_sqlite_to_supabase.py --dry-run

# Force overwrite existing data
python migrate_sqlite_to_supabase.py --force

# Custom batch size for large datasets
python migrate_sqlite_to_supabase.py --batch-size=1000

# Combination of options
python migrate_sqlite_to_supabase.py --force --batch-size=500
```

## Database Configuration

### Dynamic Database Switching

The application automatically detects which database to use:

```python
# Environment variable controls database choice
USE_SUPABASE=true   # Use Supabase PostgreSQL
USE_SUPABASE=false  # Use SQLite (default)
```

### Connection Details

**SQLite Configuration:**
- Connection pooling with StaticPool
- WAL mode for better concurrency
- Optimized pragmas for performance

**Supabase Configuration:**
- PostgreSQL connection with QueuePool
- Connection pooling (10 connections, 20 overflow)
- Automatic connection recycling

## File Storage Migration

### Storage Buckets

The system creates these Supabase Storage buckets:

| Local Directory | Supabase Bucket | Description |
|----------------|-----------------|-------------|
| `data/resumes/` | `resumes` | User resume files |
| `data/company_logos/` | `company-logos` | Company logo images |
| `data/job_docs/` | `job-documents` | Job-related documents |
| `data/visa_documents/` | `visa-documents` | Visa verification documents |

### URL Updates

File URLs are automatically updated during migration:

**Before:**
```
/data/resumes/123/resume.pdf
```

**After:**
```
https://your-project.supabase.co/storage/v1/object/public/resumes/123/resume.pdf
```

## User Authentication Compatibility

### Password Hashing
- Existing bcrypt password hashes are preserved
- Users can continue logging in with existing credentials
- No password reset required

### User Sessions
- Existing sessions remain valid during migration
- Session tokens and expiration dates are preserved
- Authentication flow continues seamlessly

### OAuth Integration
- Google OAuth integration remains functional
- OAuth user mappings are preserved
- Account linking continues to work

## Rollback Strategy

### Automatic Rollback
The deployment script includes automatic rollback on failure:

1. **Backup Creation**: Automatic backup before migration
2. **Failure Detection**: Monitors migration exit codes
3. **Automatic Restore**: Restores from backup on failure
4. **Environment Reset**: Reverts to SQLite configuration

### Manual Rollback
If manual intervention is needed:

```bash
# Restore from backup
cp backups/joborra_TIMESTAMP.db joborra.db

# Update environment
sed -i 's/USE_SUPABASE=true/USE_SUPABASE=false/' .env

# Restart services
docker-compose restart
```

## Monitoring and Verification

### Health Checks
The system includes several verification steps:

1. **Database Connectivity**: Tests PostgreSQL connection
2. **Record Count Verification**: Compares SQLite vs Supabase record counts
3. **API Health Check**: Verifies application responds correctly
4. **File Accessibility**: Tests file upload/download functionality

### Logging
Comprehensive logging throughout the migration:

- **Migration Progress**: Real-time progress updates
- **Error Details**: Detailed error messages and stack traces
- **Performance Metrics**: Timing and throughput statistics
- **Verification Results**: Detailed verification reports

### Log Files
- `migration.log`: Detailed migration log
- `deployment_TIMESTAMP.log`: Deployment process log

## Troubleshooting

### Common Issues

**1. Connection Timeouts**
```bash
# Increase timeout in database configuration
# Check network connectivity to Supabase
```

**2. Permission Errors**
```bash
# Verify SUPABASE_SERVICE_KEY has correct permissions
# Check Supabase project settings
```

**3. Large File Uploads**
```bash
# Increase MAX_FILE_SIZE if needed
# Consider batch processing for large files
```

**4. Schema Conflicts**
```bash
# Use --force flag to overwrite existing tables
# Manually resolve schema differences
```

### Debug Mode
Enable debug logging:

```bash
DEBUG=true python migrate_sqlite_to_supabase.py
```

### Recovery Procedures

**If Migration Fails Partially:**
1. Check migration.log for specific errors
2. Run with --force to restart from beginning
3. Or manually fix issues and resume

**If Application Won't Start:**
1. Check database connectivity
2. Verify environment variables
3. Review application logs
4. Consider rollback to SQLite

## Performance Considerations

### Migration Performance
- **Batch Size**: Adjust based on available memory and network
- **Concurrent Uploads**: File uploads happen sequentially to avoid API limits
- **Connection Pooling**: Optimized for both SQLite and PostgreSQL

### Post-Migration Performance
- **Connection Pooling**: PostgreSQL supports higher concurrency
- **Query Performance**: PostgreSQL optimized queries vs SQLite
- **File Access**: CDN-backed file access via Supabase Storage

### Optimization Tips
1. **Index Migration**: Indexes are recreated in PostgreSQL
2. **Query Optimization**: Review queries for PostgreSQL compatibility
3. **Connection Limits**: Monitor connection usage in production

## Security Considerations

### Data in Transit
- All connections use TLS encryption
- Supabase provides encrypted connections by default

### Access Control
- Service key used only for server-side operations
- Anon key for client-side operations with RLS (if configured)
- File storage with configurable privacy settings

### Backup Security
- Local backups stored with appropriate file permissions
- Consider encrypting sensitive backup data

## Cost Implications

### Supabase Pricing
- **Database**: Based on storage and compute usage
- **Storage**: Based on storage and bandwidth usage
- **API Requests**: Included in most plans

### Migration from SQLite Benefits
1. **Scalability**: Better concurrent user support
2. **Reliability**: Cloud-managed infrastructure
3. **Features**: Advanced PostgreSQL features
4. **Backup**: Automated backup solutions

## Support and Maintenance

### Regular Tasks
1. **Monitor Database Usage**: Track storage and compute usage
2. **Review Logs**: Regular log review for performance issues
3. **Update Dependencies**: Keep Supabase client libraries updated
4. **Backup Verification**: Test backup restoration procedures

### Updates and Migrations
- **Schema Changes**: Use Alembic for schema migrations
- **Data Updates**: Batch operations for large data changes
- **Application Updates**: Standard deployment procedures

For additional support, refer to:
- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://postgresql.org/docs/)
- Joborra application logs and monitoring
