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
SCHEDULE_HOUR = int(os.getenv('SCHEDULE_HOUR', '9'))
SCHEDULE_MINUTE = int(os.getenv('SCHEDULE_MINUTE', '0'))

# Lookback period in hours
LOOKBACK_HOURS = int(os.getenv('LOOKBACK_HOURS', '24'))

# Token storage
TOKEN_FILE = 'tokens.json'

# SSL Configuration - set to 'false' to disable SSL verification (needed for corporate proxies)
SSL_VERIFY = os.getenv('SSL_VERIFY', 'true').lower() != 'false'
