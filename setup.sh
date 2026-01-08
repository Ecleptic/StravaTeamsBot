#!/bin/bash

# Strava Teams Bot - Quick Setup Script

echo "============================================================"
echo "Strava Teams Bot - Quick Setup"
echo "============================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  Please edit .env and add your credentials:"
    echo "   - STRAVA_CLIENT_ID"
    echo "   - STRAVA_CLIENT_SECRET"
    echo "   - TEAMS_WEBHOOK_URL"
    echo ""
    echo "Then run: ./setup.sh again"
    exit 0
fi

# Check if credentials are set
if grep -q "your_client_id_here" .env || grep -q "your_webhook_url_here" .env; then
    echo "⚠️  Please update your .env file with real credentials"
    echo ""
    echo "You need:"
    echo "  1. Strava Client ID and Secret from https://www.strava.com/settings/api"
    echo "  2. Teams Webhook URL from your Teams channel"
    echo ""
    exit 1
fi

# Check if refresh token is set
if ! grep -q "STRAVA_REFRESH_TOKEN" .env || grep -q "your_refresh_token_here" .env; then
    echo "Need to get your Strava refresh token..."
    echo ""
    echo "This will:"
    echo "  1. Install dependencies locally (temporary)"
    echo "  2. Open your browser to authorize the app"
    echo "  3. Save your refresh token"
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Install dependencies
        echo "Installing dependencies..."
        pip3 install -r requirements.txt flask --quiet
        
        # Run auth helper
        echo "Opening browser for authorization..."
        python3 auth_helper.py
        
        echo ""
        echo "Please update your .env file with the refresh token shown above"
        echo "Then run: ./setup.sh again"
        exit 0
    else
        echo "Aborted. Run ./setup.sh when ready."
        exit 0
    fi
fi

# All credentials are set, build and run
echo "All credentials configured!"
echo ""
echo "Building Docker image..."
docker-compose build

echo ""
echo "Running a test..."
docker-compose run --rm bot python main.py --dry-run

echo ""
echo "============================================================"
echo "Setup complete! 🎉"
echo "============================================================"
echo ""
echo "Available commands:"
echo "  docker-compose up -d              - Start the bot"
echo "  docker-compose logs -f            - View logs"
echo "  docker-compose down               - Stop the bot"
echo "  make test                         - Test posting to Teams"
echo "  make dry-run                      - Preview without posting"
echo ""
echo "The bot will run daily at 9 AM in your configured timezone."
echo ""
