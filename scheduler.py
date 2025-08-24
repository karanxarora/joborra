#!/usr/bin/env python3
"""
Job Scraping Scheduler for Joborra
Runs automated scraping every alternate day with duplicate detection
"""

import asyncio
import logging
import schedule
import time
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
import os
from typing import Set, List, Dict
import json
from sqlalchemy import func

# Use the shared SQLAlchemy session and models (points to Supabase when DATABASE_URL is Postgres)
from app.database import SessionLocal
from app.models import Job

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JobScrapingScheduler:
    """Automated job scraping scheduler with duplicate detection"""
    
    def __init__(self):
        self.db_path = "joborra.db"
        self.last_run_file = "last_scraping_run.json"
        self.scraping_script = "simple_scraping.py"
        
    def get_existing_job_urls(self) -> Set[str]:
        """Get all existing job URLs from database to avoid duplicates"""
        existing_urls: Set[str] = set()
        try:
            db = SessionLocal()
            urls = db.query(Job.source_url).filter(Job.source_url.isnot(None)).all()
            existing_urls = {u[0] for u in urls if u and u[0]}
            logger.info(f"Found {len(existing_urls)} existing job URLs in database")
        except Exception as e:
            logger.error(f"Error fetching existing job URLs: {e}")
        finally:
            try:
                db.close()
            except Exception:
                pass
        return existing_urls
    
    def get_last_run_info(self) -> Dict:
        """Get information about the last scraping run"""
        try:
            if os.path.exists(self.last_run_file):
                with open(self.last_run_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not read last run info: {e}")
        
        return {
            "last_run_date": None,
            "jobs_scraped": 0,
            "total_jobs": 0
        }
    
    def save_run_info(self, jobs_scraped: int, total_jobs: int):
        """Save information about the current scraping run"""
        run_info = {
            "last_run_date": datetime.now().isoformat(),
            "jobs_scraped": jobs_scraped,
            "total_jobs": total_jobs
        }
        
        try:
            with open(self.last_run_file, 'w') as f:
                json.dump(run_info, f, indent=2)
            logger.info(f"Saved run info: {jobs_scraped} new jobs scraped, {total_jobs} total jobs")
        except Exception as e:
            logger.error(f"Error saving run info: {e}")
    
    def should_run_scraping(self) -> bool:
        """Check if scraping should run based on alternate day schedule"""
        last_run_info = self.get_last_run_info()
        
        if not last_run_info["last_run_date"]:
            logger.info("No previous run found, scheduling scraping")
            return True
        
        try:
            last_run = datetime.fromisoformat(last_run_info["last_run_date"])
            days_since_last_run = (datetime.now() - last_run).days
            
            if days_since_last_run >= 2:  # Run every alternate day (2+ days)
                logger.info(f"Last run was {days_since_last_run} days ago, scheduling scraping")
                return True
            else:
                logger.info(f"Last run was {days_since_last_run} days ago, skipping scraping")
                return False
                
        except Exception as e:
            logger.error(f"Error checking last run date: {e}")
            return True  # Default to running if we can't determine
    
    def get_job_count_before_scraping(self) -> int:
        """Get current job count before scraping"""
        db = None
        try:
            db = SessionLocal()
            count = db.query(func.count(Job.id)).scalar() or 0
            return int(count)
        except Exception as e:
            logger.error(f"Error getting job count: {e}")
            return 0
        finally:
            if db:
                try:
                    db.close()
                except Exception:
                    pass
    
    def run_scraping_job(self):
        """Execute the scraping job"""
        logger.info("=== STARTING SCHEDULED SCRAPING JOB ===")
        
        # Check if we should run based on schedule
        if not self.should_run_scraping():
            logger.info("Skipping scraping - not scheduled to run today")
            return
        
        # Get job count before scraping
        jobs_before = self.get_job_count_before_scraping()
        logger.info(f"Jobs in database before scraping: {jobs_before}")
        
        try:
            # Run the scraping script
            logger.info(f"Executing scraping script: {self.scraping_script}")
            result = subprocess.run(
                [sys.executable, self.scraping_script],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                logger.info("Scraping completed successfully")
                
                # Get job count after scraping
                jobs_after = self.get_job_count_before_scraping()
                new_jobs = jobs_after - jobs_before
                
                logger.info(f"Jobs in database after scraping: {jobs_after}")
                logger.info(f"New jobs added: {new_jobs}")
                
                # Save run information
                self.save_run_info(new_jobs, jobs_after)
                
                # Log some output from the scraping
                if result.stdout:
                    logger.info("Scraping output (last 500 chars):")
                    logger.info(result.stdout[-500:])
                    
            else:
                logger.error(f"Scraping failed with return code: {result.returncode}")
                if result.stderr:
                    logger.error(f"Error output: {result.stderr}")
                    
        except subprocess.TimeoutExpired:
            logger.error("Scraping timed out after 1 hour")
        except Exception as e:
            logger.error(f"Error running scraping job: {e}")
        
        logger.info("=== SCHEDULED SCRAPING JOB COMPLETED ===")
    
    def cleanup_old_jobs(self):
        """Remove jobs older than 30 days to keep database fresh"""
        db = None
        try:
            db = SessionLocal()
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            deleted_count = db.query(Job).filter(Job.scraped_at < thirty_days_ago).delete(synchronize_session=False)
            db.commit()
            if deleted_count:
                logger.info(f"Cleaned up {deleted_count} jobs older than 30 days")
        except Exception as e:
            logger.error(f"Error cleaning up old jobs: {e}")
            try:
                if db:
                    db.rollback()
            except Exception:
                pass
        finally:
            if db:
                try:
                    db.close()
                except Exception:
                    pass
    
    def run_daily_maintenance(self):
        """Run daily maintenance tasks"""
        logger.info("=== RUNNING DAILY MAINTENANCE ===")
        
        # Cleanup old jobs
        self.cleanup_old_jobs()
        
        # Log current database statistics
        db = None
        try:
            db = SessionLocal()
            total_jobs = db.query(func.count(Job.id)).scalar() or 0
            visa_jobs = db.query(func.count(Job.id)).filter(Job.visa_sponsorship.is_(True)).scalar() or 0
            rows = db.query(Job.state, func.count(Job.id)).group_by(Job.state).order_by(func.count(Job.id).desc()).all()
            jobs_by_state = {state: count for state, count in rows if state is not None}

            logger.info("Database statistics:")
            logger.info(f"  Total jobs: {int(total_jobs)}")
            logger.info(f"  Visa-friendly jobs: {int(visa_jobs)}")
            logger.info(f"  Jobs by state: {jobs_by_state}")
        except Exception as e:
            logger.error(f"Error getting database statistics: {e}")
        finally:
            if db:
                try:
                    db.close()
                except Exception:
                    pass
        
        logger.info("=== DAILY MAINTENANCE COMPLETED ===")
    
    def start_scheduler(self):
        """Start the job scheduler"""
        logger.info("Starting Joborra Job Scraping Scheduler")
        
        # Schedule scraping job to run every day at 2 AM (will check internally if it should run)
        schedule.every().day.at("02:00").do(self.run_scraping_job)
        
        # Schedule daily maintenance at 1 AM
        schedule.every().day.at("01:00").do(self.run_daily_maintenance)
        
        # Also allow manual trigger for testing
        schedule.every().day.at("10:00").do(self.run_scraping_job)  # 10 AM for testing
        
        logger.info("Scheduled jobs:")
        logger.info("  - Scraping job: Every day at 2:00 AM (runs every alternate day)")
        logger.info("  - Daily maintenance: Every day at 1:00 AM")
        logger.info("  - Test scraping: Every day at 10:00 AM")
        
        # Run initial maintenance
        self.run_daily_maintenance()
        
        # Keep the scheduler running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")

def main():
    """Main function to start the scheduler"""
    scheduler = JobScrapingScheduler()
    
    # Check command line arguments for immediate actions
    if len(sys.argv) > 1:
        if sys.argv[1] == "run-now":
            logger.info("Running scraping job immediately...")
            scheduler.run_scraping_job()
            return
        elif sys.argv[1] == "maintenance":
            logger.info("Running maintenance immediately...")
            scheduler.run_daily_maintenance()
            return
        elif sys.argv[1] == "status":
            # Show current status
            last_run_info = scheduler.get_last_run_info()
            job_count = scheduler.get_job_count_before_scraping()
            
            print(f"=== JOBORRA SCHEDULER STATUS ===")
            print(f"Database jobs: {job_count}")
            print(f"Last run: {last_run_info.get('last_run_date', 'Never')}")
            print(f"Jobs scraped in last run: {last_run_info.get('jobs_scraped', 0)}")
            print(f"Should run today: {scheduler.should_run_scraping()}")
            return
    
    # Start the scheduler
    scheduler.start_scheduler()

if __name__ == "__main__":
    main()
