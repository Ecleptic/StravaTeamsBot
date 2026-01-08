import sys
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import config
from strava_client import StravaClient
from teams_poster import TeamsPoster


def post_activities(dry_run=False):
    """Main function to fetch and post activities"""
    print(f"\n{'='*60}")
    print(f"Running at {datetime.now(pytz.timezone(config.TIMEZONE))}")
    if dry_run:
        print("MODE: DRY RUN (no posting to Teams)")
    print(f"{'='*60}\n")
    
    try:
        # Initialize clients
        strava = StravaClient()
        teams = TeamsPoster(dry_run=dry_run)
        
        # Get recent activities
        print(f"Fetching activities from the last {config.LOOKBACK_HOURS} hours...")
        activities = strava.get_recent_activities(hours=config.LOOKBACK_HOURS)
        
        print(f"Found {len(activities)} activity(ies)")
        
        # Post to Teams
        teams.post_summary(activities)
        
        print(f"\n{'='*60}")
        print("✓ Completed successfully")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"✗ Error: {str(e)}")
        print(f"{'='*60}\n")
        raise


def main():
    """Main entry point"""
    # Check if running in test mode
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("Running in TEST mode - posting immediately")
        post_activities(dry_run=False)
        return
    
    # Check if running in dry-run mode
    if len(sys.argv) > 1 and sys.argv[1] == '--dry-run':
        print("Running in DRY RUN mode - showing logs only, no posting")
        post_activities(dry_run=True)
        return
    
    # Validate configuration
    if not config.STRAVA_CLIENT_ID or not config.STRAVA_CLIENT_SECRET:
        print("ERROR: Strava API credentials not configured!")
        print("Please set STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET in .env file")
        sys.exit(1)
    
    if not config.TEAMS_WEBHOOK_URL:
        print("ERROR: Teams webhook URL not configured!")
        print("Please set TEAMS_WEBHOOK_URL in .env file")
        sys.exit(1)
    
    # Set up scheduler
    scheduler = BlockingScheduler(timezone=pytz.timezone(config.TIMEZONE))
    
    # Schedule daily at specified time
    trigger = CronTrigger(
        hour=config.SCHEDULE_HOUR,
        minute=config.SCHEDULE_MINUTE,
        timezone=config.TIMEZONE
    )
    
    scheduler.add_job(
        post_activities,
        trigger=trigger,
        id='post_strava_activities',
        name='Post Strava Activities to Teams',
        misfire_grace_time=3600  # Allow 1 hour grace period
    )
    
    print(f"{'='*60}")
    print("Strava Teams Bot Started")
    print(f"{'='*60}")
    print(f"Timezone: {config.TIMEZONE}")
    print(f"Schedule: Daily at {config.SCHEDULE_HOUR:02d}:{config.SCHEDULE_MINUTE:02d}")
    print(f"{'='*60}\n")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\nShutting down...")


if __name__ == '__main__':
    main()
