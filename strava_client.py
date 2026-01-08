import json
import os
from datetime import datetime, timedelta
from stravalib.client import Client
from stravalib import unithelper
import config
import requests
import urllib3

# Disable SSL warnings if SSL verification is disabled
if not config.SSL_VERIFY:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Monkey patch requests to disable SSL verification globally
    original_request = requests.Session.request
    def patched_request(self, *args, **kwargs):
        kwargs['verify'] = False
        return original_request(self, *args, **kwargs)
    requests.Session.request = patched_request


class StravaClient:
    def __init__(self):
        self.client = Client()
        self.access_token = None
        self.refresh_token = config.STRAVA_REFRESH_TOKEN
        self.token_expires_at = None
        self._load_tokens()
        
    def _load_tokens(self):
        """Load saved tokens from file if available"""
        if os.path.exists(config.TOKEN_FILE):
            try:
                with open(config.TOKEN_FILE, 'r') as f:
                    data = json.load(f)
                    self.access_token = data.get('access_token')
                    self.refresh_token = data.get('refresh_token')
                    self.token_expires_at = data.get('expires_at')
                    # Set the access token on the client
                    if self.access_token:
                        self.client.access_token = self.access_token
            except Exception as e:
                print(f"Error loading tokens: {e}")
    
    def _save_tokens(self, token_response):
        """Save tokens to file"""
        data = {
            'access_token': token_response['access_token'],
            'refresh_token': token_response['refresh_token'],
            'expires_at': token_response['expires_at']
        }
        with open(config.TOKEN_FILE, 'w') as f:
            json.dump(data, f)
        
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']
        self.token_expires_at = data['expires_at']
    
    def _refresh_access_token(self):
        """Refresh the access token if needed"""
        if not self.access_token or not self.token_expires_at or \
           datetime.now().timestamp() >= self.token_expires_at:
            print("Refreshing Strava access token...")
            token_response = self.client.refresh_access_token(
                client_id=config.STRAVA_CLIENT_ID,
                client_secret=config.STRAVA_CLIENT_SECRET,
                refresh_token=self.refresh_token
            )
            self._save_tokens(token_response)
            self.client.access_token = self.access_token
    
    def get_recent_activities(self, hours=24):
        """Get activities from the last N hours"""
        self._refresh_access_token()
        
        after = datetime.now() - timedelta(hours=hours)
        activities = self.client.get_activities(after=after)
        
        # Convert to list and get full details for each activity to include photos
        activity_list = []
        for activity in activities:
            # Get full activity details which includes photos
            full_activity = self.get_activity_details(activity.id)
            activity_list.append(full_activity)
        
        return activity_list
    
    def get_activity_details(self, activity_id):
        """Get detailed information about a specific activity"""
        self._refresh_access_token()
        return self.client.get_activity(activity_id)
