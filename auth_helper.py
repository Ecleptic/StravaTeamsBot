#!/usr/bin/env python3
"""
Helper script to authenticate with Strava and get a refresh token.
Run this once to authorize the app and save your refresh token.
"""

import json
from stravalib.client import Client
from flask import Flask, request
import webbrowser
import config
import threading
import time

app = Flask(__name__)
client = Client()
token_data = {}


@app.route('/authorization')
def authorization():
    """Handle the authorization callback from Strava"""
    global token_data
    
    code = request.args.get('code')
    if not code:
        return "Error: No authorization code received", 400
    
    try:
        token_response = client.exchange_code_for_token(
            client_id=config.STRAVA_CLIENT_ID,
            client_secret=config.STRAVA_CLIENT_SECRET,
            code=code
        )
        
        token_data = {
            'access_token': token_response['access_token'],
            'refresh_token': token_response['refresh_token'],
            'expires_at': token_response['expires_at']
        }
        
        # Save to file
        with open(config.TOKEN_FILE, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        return f"""
        <html>
            <body style="font-family: Arial; padding: 40px; text-align: center;">
                <h1 style="color: #FC4C02;">✓ Authorization Successful!</h1>
                <p>Your refresh token has been saved to <code>{config.TOKEN_FILE}</code></p>
                <p><strong>Refresh Token:</strong></p>
                <pre style="background: #f5f5f5; padding: 20px; border-radius: 5px; text-align: left; display: inline-block;">
{token_data['refresh_token']}</pre>
                <p>Copy this refresh token to your <code>.env</code> file as <code>STRAVA_REFRESH_TOKEN</code></p>
                <p style="color: #666; margin-top: 40px;">You can close this window now.</p>
            </body>
        </html>
        """
    except Exception as e:
        return f"Error exchanging code for token: {str(e)}", 500


def shutdown_server():
    """Shutdown the Flask server after a delay"""
    time.sleep(3)
    print("\nAuthorization complete! Check your browser for the refresh token.")
    print(f"Token saved to: {config.TOKEN_FILE}")
    if token_data:
        print(f"\nAdd this to your .env file:")
        print(f"STRAVA_REFRESH_TOKEN={token_data['refresh_token']}")
    print("\nShutting down server...")
    import os
    os._exit(0)


def main():
    """Main function to start the authorization flow"""
    if not config.STRAVA_CLIENT_ID or not config.STRAVA_CLIENT_SECRET:
        print("ERROR: Please set STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET in your .env file first!")
        return
    
    print("="*60)
    print("Strava Authorization Helper")
    print("="*60)
    print("\nThis will open your browser to authorize the application.")
    print("After authorization, you'll be redirected back here.\n")
    
    # Generate authorization URL
    authorize_url = client.authorization_url(
        client_id=config.STRAVA_CLIENT_ID,
        redirect_uri='http://localhost:5000/authorization',
        scope=['read', 'activity:read_all', 'activity:read']
    )
    
    print(f"Authorization URL: {authorize_url}\n")
    print("Opening browser in 2 seconds...")
    time.sleep(2)
    
    # Open browser
    webbrowser.open(authorize_url)
    
    # Start Flask server
    print("Waiting for authorization callback...")
    print("If your browser doesn't open, copy the URL above and paste it in your browser.\n")
    
    # Run Flask in a way that we can shut it down after callback
    app.run(port=5000, debug=False)


if __name__ == '__main__':
    main()
