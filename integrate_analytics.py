#!/usr/bin/env python3
"""
Analytics Integration Script
Adds analytics functionality to existing Joborra deployment
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def integrate_analytics():
    """Integrate analytics into existing deployment."""
    print("🔧 Integrating Analytics into Existing Joborra Deployment")
    print("=" * 60)
    
    # Get current directory (should be the app root)
    app_dir = Path.cwd()
    print(f"📁 App Directory: {app_dir}")
    
    # Analytics files to copy
    analytics_files = [
        "analytics_export.py",
        "periodic_analytics.py", 
        "analytics_dashboard.py"
    ]
    
    # Check if files exist
    missing_files = []
    for file in analytics_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing analytics files: {missing_files}")
        return False
    
    print("✅ All analytics files found")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  No virtual environment detected")
    
    # Install required dependencies
    print("🐍 Installing analytics dependencies...")
    dependencies = [
        "supabase",
        "sqlalchemy", 
        "pandas",
        "schedule",
        "requests",
        "python-dotenv"
    ]
    
    try:
        for dep in dependencies:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    # Test analytics export
    print("🧪 Testing analytics export...")
    try:
        result = subprocess.run([sys.executable, "analytics_export.py"], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Analytics export test successful")
        else:
            print(f"⚠️  Analytics export test failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️  Analytics export test timed out")
    except Exception as e:
        print(f"⚠️  Analytics export test error: {e}")
    
    # Create management script
    print("📜 Creating management script...")
    manage_script = app_dir / "manage_analytics.py"
    
    with open(manage_script, 'w') as f:
        f.write('''#!/usr/bin/env python3
"""
Analytics Management Script
"""

import sys
import subprocess
import os
from pathlib import Path

def run_analytics_export():
    """Run analytics export."""
    print("📊 Running analytics export...")
    try:
        result = subprocess.run([sys.executable, "analytics_export.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Analytics export completed successfully")
            print(result.stdout)
        else:
            print("❌ Analytics export failed")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error running analytics export: {e}")

def run_analytics_dashboard():
    """Run analytics dashboard."""
    print("📈 Running analytics dashboard...")
    try:
        subprocess.run([sys.executable, "analytics_dashboard.py"])
    except Exception as e:
        print(f"❌ Error running analytics dashboard: {e}")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python manage_analytics.py {export|dashboard}")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "export":
        run_analytics_export()
    elif command == "dashboard":
        run_analytics_dashboard()
    else:
        print("Unknown command. Use 'export' or 'dashboard'")
        sys.exit(1)

if __name__ == "__main__":
    main()
''')
    
    # Make script executable
    os.chmod(manage_script, 0o755)
    print("✅ Management script created")
    
    # Create cron job template
    print("⏰ Creating cron job template...")
    cron_template = app_dir / "analytics_cron_template.txt"
    
    with open(cron_template, 'w') as f:
        f.write(f'''# Add these lines to your crontab (crontab -e)
# Joborra Analytics Export Jobs - Every Hour

# Hourly export at the top of every hour
0 * * * * cd {app_dir} && {sys.executable} analytics_export.py >> /var/log/joborra/analytics.log 2>&1
''')
    
    print("✅ Cron job template created")
    
    # Create systemd service template
    print("⚙️  Creating systemd service template...")
    service_template = app_dir / "joborra-analytics.service.template"
    
    with open(service_template, 'w') as f:
        f.write(f'''[Unit]
Description=Joborra Analytics Export Scheduler
After=network.target
Wants=network.target

[Service]
Type=simple
User=your-service-user
Group=your-service-user
WorkingDirectory={app_dir}
Environment=PATH={sys.executable}
ExecStart={sys.executable} {app_dir}/periodic_analytics.py --mode scheduler
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=joborra-analytics

[Install]
WantedBy=multi-user.target
''')
    
    print("✅ Systemd service template created")
    
    # Create environment template
    print("🔧 Creating environment template...")
    env_template = app_dir / "analytics.env.template"
    
    with open(env_template, 'w') as f:
        f.write('''# Analytics Environment Configuration
# Copy this to your .env file or set as environment variables

# Supabase Configuration (required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key-here

# Analytics Configuration (optional)
ANALYTICS_EXPORT_INTERVAL=daily
ANALYTICS_RETENTION_DAYS=90
ANALYTICS_BUCKET=analytics-exports

# Database (if different from default)
DATABASE_URL=sqlite:///./joborra.db

# Logging (optional)
LOG_LEVEL=INFO
LOG_FILE=/var/log/joborra/analytics.log
''')
    
    print("✅ Environment template created")
    
    print("")
    print("🎉 Analytics Integration Complete!")
    print("=" * 40)
    print("")
    print("📋 Next Steps:")
    print("1. Update your .env file with Supabase credentials")
    print("2. Test analytics: python manage_analytics.py export")
    print("3. View dashboard: python manage_analytics.py dashboard")
    print("4. Set up cron jobs using: analytics_cron_template.txt")
    print("5. Set up systemd service using: joborra-analytics.service.template")
    print("")
    print("📁 Files Created:")
    print(f"  - {manage_script}")
    print(f"  - {cron_template}")
    print(f"  - {service_template}")
    print(f"  - {env_template}")
    print("")
    print("🔧 Management Commands:")
    print("  - Export: python manage_analytics.py export")
    print("  - Dashboard: python manage_analytics.py dashboard")
    print("")
    
    return True

if __name__ == "__main__":
    success = integrate_analytics()
    sys.exit(0 if success else 1)
