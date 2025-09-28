#!/bin/bash

# Deploy with Migration Script
# ===========================
# This script handles the complete deployment process including:
# 1. SQLite to Supabase migration
# 2. Environment configuration updates
# 3. Application deployment

set -e  # Exit on any error

# Configuration
LOG_FILE="deployment_$(date +%Y%m%d_%H%M%S).log"
BACKUP_DIR="backups"
MIGRATION_SCRIPT="migrate_sqlite_to_supabase.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if required environment variables are set
    required_vars=("SUPABASE_URL" "SUPABASE_SERVICE_KEY")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        error "Python3 is not installed"
        exit 1
    fi
    
    # Check if migration script exists
    if [ ! -f "$MIGRATION_SCRIPT" ]; then
        error "Migration script $MIGRATION_SCRIPT not found"
        exit 1
    fi
    
    # Check if SQLite database exists
    if [ ! -f "joborra.db" ]; then
        warning "SQLite database joborra.db not found - this might be a fresh deployment"
    fi
    
    success "Prerequisites check passed"
}

# Function to create backup
create_backup() {
    log "Creating backup..."
    
    mkdir -p "$BACKUP_DIR"
    timestamp=$(date +%Y%m%d_%H%M%S)
    
    # Backup SQLite database if it exists
    if [ -f "joborra.db" ]; then
        cp "joborra.db" "$BACKUP_DIR/joborra_${timestamp}.db"
        if [ -f "joborra.db-wal" ]; then
            cp "joborra.db-wal" "$BACKUP_DIR/joborra_${timestamp}.db-wal"
        fi
        if [ -f "joborra.db-shm" ]; then
            cp "joborra.db-shm" "$BACKUP_DIR/joborra_${timestamp}.db-shm"
        fi
        success "SQLite database backup created"
    fi
    
    # Backup data directory if it exists
    if [ -d "data" ]; then
        tar -czf "$BACKUP_DIR/data_${timestamp}.tar.gz" data/
        success "Data directory backup created"
    fi
}

# Function to run migration
run_migration() {
    log "Starting migration from SQLite to Supabase..."
    
    # Check if this is a dry run
    if [ "$DRY_RUN" = "true" ]; then
        log "Running migration in DRY RUN mode"
        python3 "$MIGRATION_SCRIPT" --dry-run --batch-size=500
    else
        # Check if force migration is requested
        if [ "$FORCE_MIGRATION" = "true" ]; then
            warning "Running migration with FORCE flag - existing Supabase data will be overwritten"
            python3 "$MIGRATION_SCRIPT" --force --batch-size=500
        else
            python3 "$MIGRATION_SCRIPT" --batch-size=500
        fi
    fi
    
    migration_exit_code=$?
    
    if [ $migration_exit_code -eq 0 ]; then
        success "Migration completed successfully"
    else
        error "Migration failed with exit code $migration_exit_code"
        exit $migration_exit_code
    fi
}

# Function to update environment configuration
update_environment() {
    log "Updating environment configuration for Supabase..."
    
    # Create or update environment variables for Supabase usage
    if [ ! -f ".env" ]; then
        log "Creating .env file"
        touch .env
    fi
    
    # Add or update USE_SUPABASE flag
    if grep -q "USE_SUPABASE" .env; then
        sed -i 's/USE_SUPABASE=.*/USE_SUPABASE=true/' .env
    else
        echo "USE_SUPABASE=true" >> .env
    fi
    
    # Add database type for easier identification
    if grep -q "DATABASE_TYPE" .env; then
        sed -i 's/DATABASE_TYPE=.*/DATABASE_TYPE=supabase/' .env
    else
        echo "DATABASE_TYPE=supabase" >> .env
    fi
    
    success "Environment configuration updated"
}

# Function to restart services
restart_services() {
    log "Restarting services..."
    
    # If using Docker
    if [ -f "docker-compose.yml" ]; then
        log "Restarting Docker services..."
        docker-compose down --remove-orphans
        docker-compose up -d --build
        
        # Wait for services to be healthy
        log "Waiting for services to be ready..."
        sleep 30
        
        # Check API health
        if curl -f http://localhost:8000/ > /dev/null 2>&1; then
            success "API is responding"
        else
            error "API is not responding after restart"
            exit 1
        fi
    else
        warning "docker-compose.yml not found, manual service restart required"
    fi
}

# Function to verify deployment
verify_deployment() {
    log "Verifying deployment..."
    
    # Check if API is using Supabase
    api_response=$(curl -s http://localhost:8000/ || echo "")
    if [ -n "$api_response" ]; then
        success "API is accessible"
    else
        error "API is not accessible"
        exit 1
    fi
    
    # Test database connectivity by checking a simple endpoint
    # You can customize this based on your API endpoints
    if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
        success "Database connectivity test passed"
    else
        warning "Database connectivity test failed or health endpoint not available"
    fi
    
    success "Deployment verification completed"
}

# Function to cleanup
cleanup() {
    log "Cleaning up..."
    
    # Remove old backup files (keep last 5)
    if [ -d "$BACKUP_DIR" ]; then
        cd "$BACKUP_DIR"
        ls -t joborra_*.db 2>/dev/null | tail -n +6 | xargs rm -f
        ls -t data_*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f
        cd ..
    fi
    
    success "Cleanup completed"
}

# Function to rollback on failure
rollback() {
    error "Deployment failed, attempting rollback..."
    
    # Find the latest backup
    latest_backup=$(ls -t "$BACKUP_DIR"/joborra_*.db 2>/dev/null | head -n1)
    
    if [ -n "$latest_backup" ]; then
        log "Restoring from backup: $latest_backup"
        cp "$latest_backup" "joborra.db"
        
        # Restore WAL and SHM files if they exist
        backup_base="${latest_backup%.db}"
        if [ -f "${backup_base}.db-wal" ]; then
            cp "${backup_base}.db-wal" "joborra.db-wal"
        fi
        if [ -f "${backup_base}.db-shm" ]; then
            cp "${backup_base}.db-shm" "joborra.db-shm"
        fi
        
        # Update environment to use SQLite
        sed -i 's/USE_SUPABASE=.*/USE_SUPABASE=false/' .env
        sed -i 's/DATABASE_TYPE=.*/DATABASE_TYPE=sqlite/' .env
        
        # Restart with SQLite
        if [ -f "docker-compose.yml" ]; then
            docker-compose down --remove-orphans
            docker-compose up -d --build
        fi
        
        success "Rollback completed"
    else
        error "No backup found for rollback"
        exit 1
    fi
}

# Main deployment function
main() {
    log "Starting deployment with migration..."
    log "Arguments: $@"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                export DRY_RUN=true
                shift
                ;;
            --force)
                export FORCE_MIGRATION=true
                shift
                ;;
            --no-backup)
                export NO_BACKUP=true
                shift
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --dry-run          Run migration simulation without making changes"
                echo "  --force            Force overwrite existing Supabase data"
                echo "  --no-backup        Skip backup creation"
                echo "  --help             Show this help message"
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Set trap for error handling
    trap rollback ERR
    
    # Execute deployment steps
    check_prerequisites
    
    if [ "$NO_BACKUP" != "true" ]; then
        create_backup
    fi
    
    run_migration
    
    if [ "$DRY_RUN" != "true" ]; then
        update_environment
        restart_services
        verify_deployment
        cleanup
    fi
    
    success "Deployment completed successfully!"
    log "Log file: $LOG_FILE"
    
    # Remove error trap
    trap - ERR
}

# Run main function with all arguments
main "$@"
