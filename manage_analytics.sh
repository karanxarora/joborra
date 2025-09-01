#!/bin/bash
# Analytics Management Script for Production
# This script manages analytics in your Docker-based deployment

set -e

APP_DIR="/opt/joborra"  # Update this to match your deployment directory
CONTAINER_NAME="joborra-api-1"  # Update this to match your container name

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if container is running
check_container() {
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        print_error "Container $CONTAINER_NAME is not running"
        exit 1
    fi
}

case "$1" in
    export)
        echo "📊 Running Analytics Export..."
        check_container
        docker exec "$CONTAINER_NAME" python /app/analytics_export.py
        print_status "Analytics export completed"
        ;;
    
    dashboard)
        echo "📈 Running Analytics Dashboard..."
        check_container
        docker exec -it "$CONTAINER_NAME" python /app/analytics_dashboard.py
        ;;
    
    install)
        echo "🔧 Installing Analytics Dependencies..."
        check_container
        docker exec "$CONTAINER_NAME" pip install supabase sqlalchemy pandas schedule requests python-dotenv
        print_status "Analytics dependencies installed"
        ;;
    
    copy-files)
        echo "📁 Copying Analytics Files to Container..."
        check_container
        docker cp analytics_export.py "$CONTAINER_NAME:/app/analytics_export.py"
        docker cp periodic_analytics.py "$CONTAINER_NAME:/app/periodic_analytics.py"
        docker cp analytics_dashboard.py "$CONTAINER_NAME:/app/analytics_dashboard.py"
        print_status "Analytics files copied to container"
        ;;
    
    setup-cron)
        echo "⏰ Setting up Analytics Cron Jobs (Every Hour)..."
        (crontab -l 2>/dev/null; echo "# Joborra Analytics Export Jobs - Every Hour") | crontab - || true
        (crontab -l 2>/dev/null; echo "0 * * * * cd $APP_DIR && docker exec $CONTAINER_NAME python /app/analytics_export.py >> /var/log/joborra/analytics.log 2>&1") | crontab - || true
        print_status "Analytics cron jobs set up (every hour)"
        ;;
    
    status)
        echo "📊 Analytics Status Check..."
        echo "Container Status:"
        docker ps | grep "$CONTAINER_NAME" || print_warning "Container not running"
        
        echo ""
        echo "Analytics Dependencies:"
        docker exec "$CONTAINER_NAME" python -c "
        try:
            import supabase, sqlalchemy, pandas, schedule
            print('✅ All analytics dependencies available')
        except ImportError as e:
            print(f'❌ Missing dependency: {e}')
        " 2>/dev/null || print_warning "Could not check dependencies"
        
        echo ""
        echo "Analytics Files:"
        docker exec "$CONTAINER_NAME" ls -la /app/analytics_*.py 2>/dev/null || print_warning "Analytics files not found"
        
        echo ""
        echo "Cron Jobs:"
        crontab -l | grep -i analytics || print_warning "No analytics cron jobs found"
        ;;
    
    logs)
        echo "📋 Analytics Logs:"
        tail -n 50 /var/log/joborra/analytics.log 2>/dev/null || print_warning "No analytics logs found"
        ;;
    
    test)
        echo "🧪 Testing Analytics System..."
        check_container
        
        echo "Testing dependencies..."
        docker exec "$CONTAINER_NAME" python -c "
        import sys
        try:
            import supabase, sqlalchemy, pandas, schedule
            print('✅ Dependencies OK')
        except ImportError as e:
            print(f'❌ Dependency error: {e}')
            sys.exit(1)
        "
        
        echo "Testing Supabase connection..."
        docker exec "$CONTAINER_NAME" python -c "
        import os
        from supabase import create_client
        try:
            client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
            buckets = client.storage.list_buckets()
            print('✅ Supabase connection OK')
        except Exception as e:
            print(f'❌ Supabase error: {e}')
        "
        
        print_status "Analytics system test completed"
        ;;
    
    *)
        echo "📊 Joborra Analytics Management"
        echo "=============================="
        echo ""
        echo "Usage: $0 {export|dashboard|install|copy-files|setup-cron|status|logs|test}"
        echo ""
        echo "Commands:"
        echo "  export      - Run analytics export"
        echo "  dashboard   - Run analytics dashboard"
        echo "  install     - Install analytics dependencies"
        echo "  copy-files  - Copy analytics files to container"
        echo "  setup-cron  - Set up automated cron jobs (every hour)"
        echo "  status      - Check analytics system status"
        echo "  logs        - View analytics logs"
        echo "  test        - Test analytics system"
        echo ""
        echo "Examples:"
        echo "  $0 install     # Install dependencies"
        echo "  $0 copy-files  # Copy files to container"
        echo "  $0 setup-cron  # Set up automated exports"
        echo "  $0 export      # Run manual export"
        echo "  $0 status      # Check system status"
        exit 1
        ;;
esac
