#!/bin/bash
# Setup script for Joborra Job Scraping Scheduler

echo "Setting up Joborra Job Scraping Scheduler..."

# Make scheduler executable
chmod +x scheduler.py

# Create cron job for alternate day scraping (every 2 days at 2 AM)
# This will run the scheduler which internally checks if it should run based on alternate day logic
echo "Setting up cron job..."

# Add cron job to run scheduler check every day at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * cd /home/karan/startup/joborra && /home/karan/.pyenv/versions/3.12.0/bin/python scheduler.py run-now >> scheduler_cron.log 2>&1") | crontab -

# Add cron job for daily maintenance at 1 AM
(crontab -l 2>/dev/null; echo "0 1 * * * cd /home/karan/startup/joborra && /home/karan/.pyenv/versions/3.12.0/bin/python scheduler.py maintenance >> scheduler_cron.log 2>&1") | crontab -

echo "Cron jobs added:"
echo "  - Daily scraping check: 0 2 * * * (runs every alternate day)"
echo "  - Daily maintenance: 0 1 * * *"

# Show current cron jobs
echo ""
echo "Current cron jobs:"
crontab -l

echo ""
echo "Setup complete!"
echo ""
echo "Usage:"
echo "  python scheduler.py status          - Show current status"
echo "  python scheduler.py run-now         - Run scraping immediately"
echo "  python scheduler.py maintenance     - Run maintenance immediately"
echo "  python scheduler.py                 - Start interactive scheduler"
echo ""
echo "Log files:"
echo "  scheduler.log                       - Main scheduler logs"
echo "  scheduler_cron.log                  - Cron job logs"
echo "  last_scraping_run.json              - Last run information"
