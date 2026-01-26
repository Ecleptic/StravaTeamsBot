import requests
from datetime import datetime
import config


class TeamsPoster:
    def __init__(self, dry_run=False):
        self.webhook_url = config.TEAMS_WEBHOOK_URL
        self.dry_run = dry_run
    
    def format_activity_card(self, activity):
        """Format a Strava activity as a Teams Adaptive Card"""
        
        # Format date
        activity_date = activity.start_date_local
        date_str = activity_date.strftime('%A, %B %d, %Y')
        time_str = activity_date.strftime('%I:%M %p')
        
        # Convert units
        # Strava API returns distance in meters
        # For swimming, display in yards; for others, display in miles
        if activity.type == 'Swim':
            distance_yards = float(activity.distance) * 1.09361 if activity.distance else 0
            distance_display = f"{distance_yards:.0f} yd"
        else:
            distance_miles = float(activity.distance) * 0.000621371 if activity.distance else 0
            distance_display = f"{distance_miles:.2f} mi"
        
        moving_time_seconds = int(activity.moving_time.total_seconds()) if activity.moving_time else 0
        elapsed_time_seconds = int(activity.elapsed_time.total_seconds()) if activity.elapsed_time else 0
        elevation_feet = float(activity.total_elevation_gain) * 3.28084 if activity.total_elevation_gain else 0
        
        # Format time
        hours = moving_time_seconds // 3600
        minutes = (moving_time_seconds % 3600) // 60
        seconds = moving_time_seconds % 60
        if hours > 0:
            time_formatted = f"{hours}h {minutes}m {seconds}s"
        else:
            time_formatted = f"{minutes}m {seconds}s"
        
        # Build facts (stats)
        facts = []
        
        # Distance
        if activity.type == 'Swim' and distance_yards > 0:
            facts.append({
                "title": "Distance",
                "value": f"{distance_yards:.0f} yd"
            })
        elif activity.type != 'Swim' and distance_miles > 0:
            facts.append({
                "title": "Distance",
                "value": f"{distance_miles:.2f} mi"
            })
        
        # Time
        if moving_time_seconds > 0:
            facts.append({
                "title": "Time",
                "value": time_formatted
            })
        
        # Pace/Speed
        if activity.type == 'Swim' and distance_yards > 0:
            pace_seconds_per_100yd = (moving_time_seconds / distance_yards) * 100
            pace_minutes = int(pace_seconds_per_100yd // 60)
            pace_secs = int(pace_seconds_per_100yd % 60)
            facts.append({
                "title": "Pace",
                "value": f"{pace_minutes}:{pace_secs:02d} /100yd"
            })
        elif activity.type != 'Swim' and distance_miles > 0:
            if activity.type in ['Run', 'Walk', 'Hike']:
                pace_seconds = moving_time_seconds / distance_miles
                pace_minutes = int(pace_seconds // 60)
                pace_secs = int(pace_seconds % 60)
                facts.append({
                    "title": "Pace",
                    "value": f"{pace_minutes}:{pace_secs:02d} /mi"
                })
            else:
                speed_mph = distance_miles / (moving_time_seconds / 3600)
                facts.append({
                    "title": "Speed",
                    "value": f"{speed_mph:.1f} mph"
                })
        
        # Elevation
        if elevation_feet > 0:
            facts.append({
                "title": "Elevation",
                "value": f"{elevation_feet:.0f} ft"
            })
        
        # Heart rate
        if hasattr(activity, 'average_heartrate') and activity.average_heartrate:
            facts.append({
                "title": "Avg HR",
                "value": f"{activity.average_heartrate:.0f} bpm"
            })
        
        if hasattr(activity, 'max_heartrate') and activity.max_heartrate:
            facts.append({
                "title": "Max HR",
                "value": f"{activity.max_heartrate:.0f} bpm"
            })
        
        # Calories
        if hasattr(activity, 'calories') and activity.calories:
            facts.append({
                "title": "Calories",
                "value": f"{activity.calories:.0f}"
            })
        
        # Build the adaptive card
        card = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": []
                    }
                }
            ]
        }
        
        body = card["attachments"][0]["content"]["body"]
        
        # Add header image if available
        photo_url = None
        if hasattr(activity, 'photos') and hasattr(activity.photos, 'primary') and activity.photos.primary:
            # Use the primary photo
            photo_url = activity.photos.primary.urls.get('600') or activity.photos.primary.urls.get('1000')
        elif hasattr(activity, 'total_photo_count') and activity.total_photo_count > 0:
            # If photos exist but we don't have the URL in summary, we'd need to fetch full activity
            # For now, we'll skip this to avoid extra API calls
            pass
        
        if photo_url:
            body.append({
                "type": "Image",
                "url": photo_url,
                "size": "Stretch"
            })
        
        # Title
        body.append({
            "type": "TextBlock",
            "text": activity.name,
            "size": "Large",
            "weight": "Bolder"
        })
        
        # Date and time
        if config.SHOW_WORKOUT_TIME:
            date_time_text = f"{date_str} at {time_str}"
        else:
            date_time_text = date_str
        body.append({
            "type": "TextBlock",
            "text": date_time_text,
            "size": "Small",
            "color": "Default",
            "spacing": "None"
        })
        
        # Activity type
        body.append({
            "type": "TextBlock",
            "text": activity.type,
            "size": "Small",
            "weight": "Lighter",
            "spacing": "None"
        })
        
        # Stats
        if facts:
            body.append({
                "type": "FactSet",
                "facts": facts,
                "spacing": "Medium"
            })
        
        # Description if available
        if activity.description:
            body.append({
                "type": "TextBlock",
                "text": activity.description,
                "wrap": True,
                "spacing": "Medium"
            })
        
        # Link to activity
        body.append({
            "type": "ActionSet",
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "View on Strava",
                    "url": f"https://www.strava.com/activities/{activity.id}"
                }
            ]
        })
        
        return card
    
    def post_activities(self, activities):
        """Post activities to Teams"""
        if not activities:
            print("No activities to post")
            return
        
        for activity in activities:
            card = self.format_activity_card(activity)
            if self.dry_run:
                print(f"\n{'='*60}")
                print(f"ACTIVITY: {activity.name}")
                print(f"{'='*60}")
                print(f"Type: {activity.type}")
                print(f"Date: {activity.start_date_local}")
                print(f"Distance: {float(activity.distance) * 0.000621371:.2f} mi" if activity.distance else "Distance: N/A")
                print(f"Time: {activity.moving_time}" if activity.moving_time else "Time: N/A")
                print(f"Elevation: {float(activity.total_elevation_gain) * 3.28084:.0f} ft" if activity.total_elevation_gain else "Elevation: N/A")
                if hasattr(activity, 'average_heartrate') and activity.average_heartrate:
                    print(f"Avg HR: {activity.average_heartrate:.0f} bpm")
                if hasattr(activity, 'calories') and activity.calories:
                    print(f"Calories: {activity.calories:.0f}")
                print(f"\nCard JSON:")
                import json
                print(json.dumps(card, indent=2))
                print(f"{'='*60}\n")
                continue
            
            if self.dry_run:
                print("\n" + "="*60)
                print("No activities in the last 24 hours. Rest day! 😴")
                print("="*60 + "\n")
                return
                
            
            try:
                response = requests.post(
                    self.webhook_url,
                    json=card,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code in [200, 202]:
                    print(f"✓ Posted activity: {activity.name}")
                else:
                    print(f"✗ Failed to post activity: {activity.name} - Status: {response.status_code}")
                    print(f"  Response: {response.text}")
            except Exception as e:
                print(f"✗ Error posting activity: {activity.name} - {str(e)}")
    
    def post_summary(self, activities):
        """Post a summary card with all activities"""
        if not activities:
            # Skip posting when there are no activities
            print("No activities in the last 24 hours - skipping post")
            return
        
        # Post individual activity cards
        self.post_activities(activities)
