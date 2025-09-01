#!/bin/bash
# Add Analytics to Existing Joborra Deployment
# This script integrates analytics into your existing deployment

set -e

echo "🔧 Adding Analytics to Existing Joborra Deployment"
echo "================================================="

# Configuration - Update these paths to match your existing deployment
APP_DIR="/opt/joborra"  # Update to your app directory
SERVICE_USER="joborra"  # Update to your service user
LOG_DIR="/var/log/joborra"  # Update to your log directory

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Verify existing deployment
if [ ! -d "$APP_DIR" ]; then
    echo "❌ App directory $APP_DIR not found. Please update APP_DIR in this script."
    exit 1
fi

if ! id "$SERVICE_USER" &>/dev/null; then
    echo "❌ Service user $SERVICE_USER not found. Please update SERVICE_USER in this script."
    exit 1
fi

print_status "Found existing deployment at $APP_DIR"

# Create analytics directory
ANALYTICS_DIR="$APP_DIR/analytics"
mkdir -p "$ANALYTICS_DIR"
chown "$SERVICE_USER:$SERVICE_USER" "$ANALYTICS_DIR"

# Copy analytics files to existing deployment
echo "📁 Copying analytics files..."
cp analytics_export.py "$APP_DIR/"
cp periodic_analytics.py "$APP_DIR/"
cp analytics_dashboard.py "$APP_DIR/"

# Set permissions
chown "$SERVICE_USER:$SERVICE_USER" "$APP_DIR"/*.py
chmod +x "$APP_DIR"/*.py

print_status "Copied analytics files"

# Add analytics to existing systemd service (if it exists)
if [ -f "/etc/systemd/system/joborra.service" ]; then
    echo "📝 Adding analytics to existing systemd service..."
    
    # Create a separate analytics service
    cat > /etc/systemd/system/joborra-analytics.service << EOF
[Unit]
Description=Joborra Analytics Export Scheduler
After=network.target joborra.service
Wants=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/periodic_analytics.py --mode scheduler
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=joborra-analytics

[Install]
WantedBy=multi-user.target
EOF

    print_status "Created analytics systemd service"
fi

# Add cron jobs to existing crontab
echo "⏰ Adding analytics cron jobs..."
CRON_FILE="/tmp/joborra-analytics-cron"

# Get existing crontab
crontab -u "$SERVICE_USER" -l 2>/dev/null > "$CRON_FILE" || touch "$CRON_FILE"

# Add analytics cron jobs if not already present
if ! grep -q "analytics_export.py" "$CRON_FILE"; then
    cat >> "$CRON_FILE" << EOF

# Joborra Analytics Export Jobs
# Daily export at 2:00 AM
0 2 * * * cd $APP_DIR && $APP_DIR/venv/bin/python $APP_DIR/analytics_export.py >> $LOG_DIR/analytics.log 2>&1

# Weekly export on Sundays at 3:00 AM  
0 3 * * 0 cd $APP_DIR && $APP_DIR/venv/bin/python $APP_DIR/analytics_export.py >> $LOG_DIR/analytics.log 2>&1

# Monthly export on 1st at 4:00 AM
0 4 1 * * cd $APP_DIR && $APP_DIR/venv/bin/python $APP_DIR/analytics_export.py >> $LOG_DIR/analytics.log 2>&1
EOF

    # Install the updated crontab
    crontab -u "$SERVICE_USER" "$CRON_FILE"
    rm "$CRON_FILE"
    
    print_status "Added analytics cron jobs"
else
    print_warning "Analytics cron jobs already exist"
fi

# Add analytics environment variables to existing .env
ENV_FILE="$APP_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    echo "🔧 Adding analytics environment variables..."
    
    # Add analytics config if not already present
    if ! grep -q "ANALYTICS_EXPORT_INTERVAL" "$ENV_FILE"; then
        cat >> "$ENV_FILE" << EOF

# Analytics Configuration
ANALYTICS_EXPORT_INTERVAL=daily
ANALYTICS_RETENTION_DAYS=90
ANALYTICS_BUCKET=analytics-exports
EOF
        print_status "Added analytics environment variables"
    else
        print_warning "Analytics environment variables already exist"
    fi
fi

# Install additional Python dependencies
echo "🐍 Installing analytics dependencies..."
if [ -d "$APP_DIR/venv" ]; then
    source "$APP_DIR/venv/bin/activate"
    pip install supabase sqlalchemy pandas schedule requests python-dotenv
    print_status "Installed analytics dependencies"
else
    print_warning "Virtual environment not found. Please install dependencies manually."
fi

# Create analytics management script
echo "📜 Creating analytics management script..."
cat > "$APP_DIR/manage_analytics.sh" << 'EOF'
#!/bin/bash
# Analytics management script for existing deployment

APP_DIR="/opt/joborra"
SERVICE_USER="joborra"

case "$1" in
    start)
        echo "Starting analytics service..."
        systemctl start joborra-analytics
        ;;
    stop)
        echo "Stopping analytics service..."
        systemctl stop joborra-analytics
        ;;
    restart)
        echo "Restarting analytics service..."
        systemctl restart joborra-analytics
        ;;
    status)
        echo "Analytics service status:"
        systemctl status joborra-analytics --no-pager
        ;;
    logs)
        echo "Analytics logs:"
        journalctl -u joborra-analytics -f
        ;;
    export)
        echo "Running manual analytics export..."
        cd "$APP_DIR"
        source venv/bin/activate
        python analytics_export.py
        ;;
    dashboard)
        echo "Running analytics dashboard..."
        cd "$APP_DIR"
        source venv/bin/activate
        python analytics_dashboard.py
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|export|dashboard}"
        exit 1
        ;;
esac
EOF

chmod +x "$APP_DIR/manage_analytics.sh"
chown "$SERVICE_USER:$SERVICE_USER" "$APP_DIR/manage_analytics.sh"

print_status "Created analytics management script"

# Reload systemd and start service
echo "🔄 Starting analytics service..."
systemctl daemon-reload
systemctl enable joborra-analytics
systemctl start joborra-analytics

print_status "Analytics service started"

# Test the setup
echo "🧪 Testing analytics setup..."
cd "$APP_DIR"
source venv/bin/activate
if python -c "import supabase, sqlalchemy, pandas; print('Dependencies OK')"; then
    print_status "Analytics dependencies verified"
else
    print_warning "Some dependencies may be missing"
fi

echo ""
echo "🎉 Analytics Successfully Added to Existing Deployment!"
echo "======================================================"
echo ""
echo "📋 Management Commands:"
echo "  - Start: sudo $APP_DIR/manage_analytics.sh start"
echo "  - Stop: sudo $APP_DIR/manage_analytics.sh stop"
echo "  - Status: sudo $APP_DIR/manage_analytics.sh status"
echo "  - Logs: sudo $APP_DIR/manage_analytics.sh logs"
echo "  - Manual Export: sudo $APP_DIR/manage_analytics.sh export"
echo "  - Dashboard: sudo $APP_DIR/manage_analytics.sh dashboard"
echo ""
echo "⏰ Scheduled Exports:"
echo "  - Daily: 2:00 AM"
echo "  - Weekly: Sunday 3:00 AM"
echo "  - Monthly: 1st at 4:00 AM"
echo ""
echo "📁 Files Added:"
echo "  - $APP_DIR/analytics_export.py"
echo "  - $APP_DIR/periodic_analytics.py"
echo "  - $APP_DIR/analytics_dashboard.py"
echo "  - $APP_DIR/manage_analytics.sh"
echo "  - /etc/systemd/system/joborra-analytics.service"
echo ""
echo "🔧 Next Steps:"
echo "1. Update your .env file with Supabase credentials"
echo "2. Test with: sudo $APP_DIR/manage_analytics.sh export"
echo "3. Check status: sudo $APP_DIR/manage_analytics.sh status"
echo ""
print_status "Integration completed successfully!"
