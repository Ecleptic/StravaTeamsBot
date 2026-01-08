# Strava Teams Bot

A Docker-based bot that automatically posts your Strava activities to Microsoft Teams.

## Features

- Posts all new Strava activities (runs, rides, walks, swims, hikes, etc.) to a Teams channel
- Runs daily at 9 AM (configurable timezone)
- Includes activity stats (distance, time, pace/speed, elevation, heart rate, calories)
- Displays activity header images when available
- Shows distance in yards for swimming, miles for everything else
- Beautiful Teams Adaptive Card formatting

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Strava account
- Microsoft Teams channel with webhook access

### 1. Get Your Credentials

**Strava API:**
1. Go to https://www.strava.com/settings/api
2. Create a new application
3. Note your `Client ID` and `Client Secret`

**Teams Webhook:**
1. In your Teams channel, click `...` → `Workflows`
2. Select `Post to a channel when a webhook request is received`
3. Add workflow and copy the webhook URL

### 2. Run Setup

```bash
# Clone or download this repo
cd stravaTeamsBot

# Run the setup script
./setup.sh
```

The setup script will:
- Create your `.env` file
- Guide you through adding credentials
- Get your Strava refresh token
- Test the bot
- Build the Docker image

### 3. Start the Bot

```bash
docker-compose up -d
```

That's it! 🎉

## Usage

### Using Docker Compose (Recommended)

```bash
# Start the bot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the bot
docker-compose down

# Restart the bot
make restart
```

### Using Docker Run

**Option 1: With .env file**

```bash
# Pull the image from Docker Hub
docker pull ecleptic/strava-teams-bot:latest

# Run the container
docker run -d \
  --name strava-teams-bot \
  --network host \
  --restart unless-stopped \
  -v $(pwd)/tokens.json:/app/tokens.json \
  --env-file .env \
  ecleptic/strava-teams-bot:latest
```

**Option 2: Without .env file (pass variables directly)**

```bash
# Pull the image
docker pull ecleptic/strava-teams-bot:latest

# Run with environment variables
docker run -d \
  --name strava-teams-bot \
  --network host \
  --restart unless-stopped \
  -v $(pwd)/tokens.json:/app/tokens.json \
  -e STRAVA_CLIENT_ID=your_client_id \
  -e STRAVA_CLIENT_SECRET=your_client_secret \
  -e STRAVA_REFRESH_TOKEN=your_refresh_token \
  -e TEAMS_WEBHOOK_URL=your_webhook_url \
  -e TIMEZONE=America/New_York \
  -e SCHEDULE_HOUR=9 \
  -e SCHEDULE_MINUTE=0 \
  ecleptic/strava-teams-bot:latest
```

**Managing the container:**

```bash
# View logs
docker logs -f strava-teams-bot

# Stop the bot
docker stop strava-teams-bot
docker rm strava-teams-bot
```

### Testing

```bash
# Test posting (dry run - no actual posting)
make dry-run

# Test posting to Teams
make test
```

## Configuration

Edit `.env` to customize:

```bash
TIMEZONE=America/New_York      # Your timezone
SCHEDULE_HOUR=9                # Hour to post (24-hour format)
SCHEDULE_MINUTE=0              # Minute to post
LOOKBACK_HOURS=24              # How many hours back to check
```

## How It Works

1. **Scheduled**: Bot runs daily at 9 AM in your configured timezone
2. **Fetches**: Gets all activities from past 24 hours
3. **Posts**: Creates beautiful adaptive cards in Teams with:
   - Activity photo (if uploaded to Strava)
   - Activity name and type
   - Date and time
   - Stats (distance, time, pace, heart rate, calories, etc.)
   - Link to view on Strava

## Project Structure

```
stravaTeamsBot/
├── main.py              # Main bot scheduler
├── strava_client.py     # Strava API integration
├── teams_poster.py      # Teams message formatting
├── config.py            # Configuration management
├── auth_helper.py       # One-time auth setup
├── setup.sh             # Quick setup script
├── Makefile             # Convenient commands
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker orchestration
└── .env                 # Your credentials (not in git)
```

## Troubleshooting

**"Authorization Error: activity:read_permission missing"**
- Your refresh token doesn't have the right permissions
- Run `python3 auth_helper.py` to get a new token

**Bot not posting at scheduled time**
- Check logs: `docker-compose logs -f`
- Verify timezone in `.env`
- Ensure container is running: `docker-compose ps`

**No activities found**
- Verify you have activities in the past 24 hours
- Check Strava API credentials are correct

## Development

```bash
# Run locally without Docker
pip3 install -r requirements.txt
python3 main.py --dry-run

# Build Docker image
docker-compose build

# Run tests
make dry-run
make test
```

## License

MIT


