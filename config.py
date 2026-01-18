import os
from dotenv import load_dotenv

load_dotenv()

# Strava API Configuration
STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')

# Teams Configuration
TEAMS_WEBHOOK_URL = os.getenv('TEAMS_WEBHOOK_URL')

# Scheduling Configuration
TIMEZONE = os.getenv('TIMEZONE', 'America/New_York')
# Cron format: minute hour day month day-of-week
# Default: 9:00 AM on weekdays (Monday-Friday)
SCHEDULE_CRON = os.getenv('SCHEDULE_CRON', '0 9 * * 1-5')

# Lookback period in hours
LOOKBACK_HOURS = int(os.getenv('LOOKBACK_HOURS', '24'))

# Token storage
TOKEN_FILE = 'tokens.json'

# SSL Configuration - set to 'false' to disable SSL verification (needed for corporate proxies)
SSL_VERIFY = os.getenv('SSL_VERIFY', 'true').lower() != 'false'
