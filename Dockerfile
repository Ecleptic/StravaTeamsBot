FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install CA certificates
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py strava_client.py teams_poster.py config.py ./

# Create directory for token storage
RUN mkdir -p /app && touch /app/tokens.json

# Run the bot
CMD ["python", "-u", "main.py"]

