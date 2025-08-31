# Migration to SQLite-Only Setup

This document outlines the changes made to migrate Joborra from a hybrid SQLite/Supabase setup to a pure SQLite setup for both local development and production.

## Changes Made

### 1. Database Configuration (`app/database.py`)
- **Removed**: PostgreSQL/Supabase connection handling
- **Updated**: Force SQLite usage regardless of `DATABASE_URL` environment variable
- **Added**: SQLite optimization pragmas for production use:
  - WAL (Write-Ahead Logging) mode for better concurrency
  - Optimized cache size (64MB)
  - Foreign key enforcement
  - Memory-based temporary storage

### 2. File Storage System
- **Created**: `app/local_storage.py` - comprehensive local file storage utility
- **Replaced**: Supabase storage with organized local filesystem storage
- **Features**:
  - Automatic directory creation for different file types
  - File type validation and size limits
  - Unique filename generation
  - Support for resumes, company logos, job documents, and visa documents

### 3. API Endpoints Updated
- **Files Modified**: `app/auth_api.py`, `app/visa_api.py`
- **Changes**: 
  - Replaced Supabase upload calls with local storage functions
  - Simplified error handling
  - Maintained same API interface for frontend compatibility

### 4. Schema Compatibility (`main.py`)
- **Simplified**: Removed PostgreSQL-specific schema handling
- **Focused**: SQLite-only schema evolution and compatibility
- **Maintained**: Automatic column addition for schema updates

### 5. Docker Configuration (`docker-compose.yml`)
- **Added**: Volume mounts for SQLite database persistence
- **Included**: WAL and shared memory file mounts for SQLite
- **Environment**: Set explicit SQLite configuration variables

### 6. Documentation Updates
- **Files**: `README.md`, `WARP.md`
- **Updated**: Installation instructions, environment variables, tech stack description
- **Removed**: PostgreSQL and Supabase references

### 7. Cleanup
- **Removed Files**:
  - `app/supabase_utils.py`
  - `scripts/migrate_sqlite_to_supabase.py`
  - `scripts/init_supabase_schema.py`
- **Added**: `scripts/migrate_to_local_storage.py` for migrating existing remote files

## Production Deployment Changes

### Environment Variables
```bash
# Required
DATABASE_URL=sqlite:///./joborra.db
LOCAL_STORAGE_PATH=/app/data
LOCAL_STORAGE_URL_PREFIX=/data

# Optional
MAX_FILE_SIZE=10485760  # 10MB default
```

### Docker Volumes
```yaml
volumes:
  - ./data:/app/data              # File storage
  - ./joborra.db:/app/joborra.db  # Database
  - ./joborra.db-wal:/app/joborra.db-wal  # WAL file
  - ./joborra.db-shm:/app/joborra.db-shm  # Shared memory
```

### File Structure
```
data/
├── resumes/
│   └── {user_id}/
├── company_logos/
│   └── {user_id}/
├── job_docs/
│   └── {user_id}/{job_id}/
└── visa_documents/
    └── {user_id}/{document_type}/
```

## Benefits of SQLite-Only Setup

1. **Simplified Architecture**: No external database dependencies
2. **Cost Reduction**: No Supabase subscription required
3. **Improved Performance**: Local file access and optimized SQLite configuration
4. **Easy Deployment**: Single database file with simple volume mounting
5. **Development Consistency**: Same database system in dev and production
6. **Better Concurrency**: WAL mode enables better concurrent access
7. **Easier Backup**: Simple file-based backup of database and uploads

## Migration Steps for Existing Deployments

1. **Backup Current Data**: Export existing data from Supabase
2. **Run Migration Script**: Use `scripts/migrate_to_local_storage.py`
3. **Update Environment**: Set SQLite environment variables
4. **Deploy Changes**: Use updated Docker configuration
5. **Verify**: Test file uploads and database operations

## Performance Considerations

- **SQLite Limitations**: Single writer, but WAL mode allows concurrent readers
- **File Storage**: Local filesystem performance depends on storage type
- **Scaling**: For high-volume deployments, consider read replicas or database sharding
- **Backup Strategy**: Regular backups of SQLite file and data directory

## Monitoring

- Monitor SQLite database size growth
- Watch for file storage disk usage
- Check WAL file size (should auto-checkpoint)
- Monitor concurrent connection handling

## Rollback Plan

If rollback is needed:
1. Restore previous codebase version
2. Migrate data back to Supabase using reverse migration script
3. Update environment variables to Supabase configuration
4. Redeploy with original Docker configuration

This migration provides a more streamlined, cost-effective, and maintainable solution while preserving all existing functionality.
