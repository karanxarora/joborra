#!/bin/bash
# Enhanced deployment script with fresh vs existing deployment logic
# This script mirrors the CI/CD logic for local testing

set -euo pipefail

echo "🚀 Starting Enhanced Deployment with Migration Check..."

# === DATABASE DEPLOYMENT STRATEGY ===
echo "🔄 Starting Database Deployment Strategy..."

# Create backups directory
mkdir -p backups

# Check deployment scenario
DEPLOYMENT_TYPE="fresh"

if [ -f "joborra.db" ]; then
  echo "📁 Found existing SQLite database - EXISTING DEPLOYMENT detected"
  DEPLOYMENT_TYPE="existing"
  
  # Create timestamped backup
  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  cp "joborra.db" "backups/joborra_pre_migration_${TIMESTAMP}.db"
  if [ -f "joborra.db-wal" ]; then
    cp "joborra.db-wal" "backups/joborra_pre_migration_${TIMESTAMP}.db-wal" 2>/dev/null || true
  fi
  if [ -f "joborra.db-shm" ]; then
    cp "joborra.db-shm" "backups/joborra_pre_migration_${TIMESTAMP}.db-shm" 2>/dev/null || true
  fi
  echo "✅ SQLite backup created: joborra_pre_migration_${TIMESTAMP}.db"
else
  echo "🆕 No existing SQLite database found - FRESH DEPLOYMENT detected"
  echo "✅ Fresh deployment: will use Supabase directly, no migration needed"
fi

echo "📋 Deployment Type: $DEPLOYMENT_TYPE"

# === ENVIRONMENT CONFIGURATION ===
echo "⚙️ Configuring environment for deployment type..."

# Check if .env exists
if [ ! -f ".env" ]; then
  echo "⚠️ No .env file found. Please create one with your Supabase configuration."
  echo "📋 Example: cp env.supabase.example .env"
  exit 1
fi

# Configure based on deployment type
if [ "$DEPLOYMENT_TYPE" = "existing" ]; then
  echo "🔧 Configuring for EXISTING deployment with migration..."
  
  # Temporarily set to SQLite for migration
  sed -i.bak 's/USE_SUPABASE=true/USE_SUPABASE=false/' .env 2>/dev/null || true
  
  # Add migration mode if not present
  if ! grep -q "MIGRATION_MODE" .env; then
    echo "MIGRATION_MODE=true" >> .env
  else
    sed -i.bak 's/MIGRATION_MODE=false/MIGRATION_MODE=true/' .env 2>/dev/null || true
  fi
  
  echo "✅ Environment configured for EXISTING deployment with migration"
else
  echo "🔧 Configuring for FRESH deployment..."
  
  # Set to use Supabase directly
  sed -i.bak 's/USE_SUPABASE=false/USE_SUPABASE=true/' .env 2>/dev/null || true
  
  # Set migration mode to false
  if ! grep -q "MIGRATION_MODE" .env; then
    echo "MIGRATION_MODE=false" >> .env
  else
    sed -i.bak 's/MIGRATION_MODE=true/MIGRATION_MODE=false/' .env 2>/dev/null || true
  fi
  
  echo "✅ Environment configured for FRESH deployment (Supabase only)"
fi

# === MIGRATION EXECUTION LOGIC ===
if [ "$DEPLOYMENT_TYPE" = "existing" ]; then
  echo "🔄 Processing EXISTING deployment - Migration Required"
  
  # Check if Python 3 is available
  if command -v python3 >/dev/null 2>&1; then
    echo "🐍 Python3 found, proceeding with migration..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "migration_env" ]; then
      echo "📦 Creating virtual environment..."
      python3 -m venv migration_env
    fi
    
    # Activate virtual environment
    source migration_env/bin/activate
    
    # Install/upgrade requirements
    echo "📚 Installing/upgrading requirements..."
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    
    # Run migration
    echo "🚀 Running SQLite to Supabase migration..."
    if python3 migrate_production_final.py; then
      echo "✅ Migration to Supabase completed successfully"
      
      # Update environment to use Supabase
      sed -i.bak 's/USE_SUPABASE=false/USE_SUPABASE=true/' .env
      sed -i.bak 's/MIGRATION_MODE=true/MIGRATION_MODE=false/' .env
      
      echo "✅ Application configured to use Supabase as primary"
      echo "✅ SQLite preserved as backup"
    else
      echo "❌ Migration failed, keeping SQLite as primary database"
      echo "✅ SQLite backup preserved for fallback"
    fi
    
    # Deactivate virtual environment
    deactivate
  else
    echo "⚠️ Python3 not found - skipping migration"
    echo "❌ Cannot proceed with existing deployment without Python3"
    exit 1
  fi
  
else
  echo "🆕 Processing FRESH deployment - No Migration Needed"
  echo "✅ Application will use Supabase directly"
  echo "✅ SQLAlchemy will create tables automatically on first run"
fi

# === DOCKER DEPLOYMENT ===
echo "🐳 Starting Docker deployment..."

# Stop existing containers
echo "⏹️ Stopping existing containers..."
docker compose down || true

# Build fresh containers
echo "🔨 Building fresh containers..."
docker compose build --no-cache

# Start services
echo "🚀 Starting services..."
docker compose up -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

# === FINAL DEPLOYMENT SUMMARY ===
echo ""
echo "📊 Final Database Configuration Summary:"
echo "🔹 Deployment Type: $DEPLOYMENT_TYPE"

if [ "$DEPLOYMENT_TYPE" = "existing" ]; then
  if grep -q "USE_SUPABASE=true" .env 2>/dev/null; then
    echo "✅ Primary Database: Supabase PostgreSQL"
    echo "✅ Fallback Database: SQLite (preserved as backup)"
    echo "✅ Migration: Successfully completed"
    echo "✅ User Data: Preserved and migrated"
  else
    echo "✅ Primary Database: SQLite (migration failed/skipped)"
    echo "ℹ️ Supabase: Migration was attempted but failed"
    echo "✅ Backup: SQLite data preserved"
  fi
else
  echo "✅ Primary Database: Supabase PostgreSQL"
  echo "✅ Deployment: Fresh installation"
  echo "✅ Schema: Will be created automatically"
  echo "ℹ️ Migration: Not required (no existing data)"
fi

# === HEALTH CHECK ===
echo ""
echo "🏥 Running health checks..."

# Check if containers are running
if docker compose ps | grep -q "Up"; then
  echo "✅ Containers are running"
  
  # Check API health
  echo "🔍 Checking API health..."
  if curl -f http://localhost:8000/ >/dev/null 2>&1; then
    echo "✅ API is responding"
  else
    echo "⚠️ API health check failed, but containers are running"
  fi
else
  echo "❌ Some containers may not be running properly"
fi

echo ""
echo "🎉 Deployment completed!"
echo "🌐 Application should be available at: http://localhost:3000"
echo "🔗 API endpoint available at: http://localhost:8000"

# Clean up backup files
rm -f .env.bak 2>/dev/null || true
