#!/usr/bin/env python3
"""
Periodic Analytics Export - Run analytics exports on a schedule.
"""

import os
import sys
import schedule
import time
from datetime import datetime
from analytics_export import main as run_analytics_export

def run_daily_export():
    """Run daily analytics export."""
    print(f"\n🕐 Running Daily Analytics Export - {datetime.now()}")
    print("=" * 60)
    
    try:
        result = run_analytics_export()
        if result == 0:
            print("✅ Daily analytics export completed successfully")
        else:
            print("❌ Daily analytics export failed")
        return result
    except Exception as e:
        print(f"❌ Error in daily export: {e}")
        return 1

def run_weekly_export():
    """Run weekly analytics export with additional metrics."""
    print(f"\n📅 Running Weekly Analytics Export - {datetime.now()}")
    print("=" * 60)
    
    try:
        # Run the standard export
        result = run_analytics_export()
        if result == 0:
            print("✅ Weekly analytics export completed successfully")
        else:
            print("❌ Weekly analytics export failed")
        return result
    except Exception as e:
        print(f"❌ Error in weekly export: {e}")
        return 1

def run_monthly_export():
    """Run monthly analytics export with comprehensive data."""
    print(f"\n📊 Running Monthly Analytics Export - {datetime.now()}")
    print("=" * 60)
    
    try:
        # Run the standard export
        result = run_analytics_export()
        if result == 0:
            print("✅ Monthly analytics export completed successfully")
        else:
            print("❌ Monthly analytics export failed")
        return result
    except Exception as e:
        print(f"❌ Error in monthly export: {e}")
        return 1

def setup_scheduler():
    """Set up the periodic analytics scheduler."""
    print("⏰ Setting up Periodic Analytics Scheduler")
    print("=" * 50)
    
    # Schedule daily export at 2 AM
    schedule.every().day.at("02:00").do(run_daily_export)
    print("  📅 Daily export scheduled at 2:00 AM")
    
    # Schedule weekly export on Sundays at 3 AM
    schedule.every().sunday.at("03:00").do(run_weekly_export)
    print("  📅 Weekly export scheduled on Sundays at 3:00 AM")
    
    # Schedule monthly export on the 1st at 4 AM
    schedule.every().month.do(run_monthly_export)
    print("  📅 Monthly export scheduled on the 1st at 4:00 AM")
    
    print("\n🔄 Scheduler is running. Press Ctrl+C to stop.")
    print("📝 Next scheduled runs:")
    
    # Show next scheduled runs
    for job in schedule.jobs:
        print(f"  ⏰ {job.next_run}")

def run_scheduler():
    """Run the scheduler continuously."""
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped by user")
    except Exception as e:
        print(f"\n❌ Scheduler error: {e}")

def run_manual_export():
    """Run a manual export immediately."""
    print("🚀 Running Manual Analytics Export")
    print("=" * 50)
    
    return run_analytics_export()

def main():
    """Main function for periodic analytics."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Joborra Periodic Analytics Export")
    parser.add_argument("--mode", choices=["scheduler", "daily", "weekly", "monthly", "manual"], 
                       default="manual", help="Export mode")
    
    args = parser.parse_args()
    
    print("📊 Joborra Periodic Analytics Export")
    print("=" * 50)
    
    if args.mode == "scheduler":
        setup_scheduler()
        run_scheduler()
    elif args.mode == "daily":
        return run_daily_export()
    elif args.mode == "weekly":
        return run_weekly_export()
    elif args.mode == "monthly":
        return run_monthly_export()
    elif args.mode == "manual":
        return run_manual_export()
    
    return 0

if __name__ == "__main__":
    exit(main())
