.PHONY: help build up down logs test dry-run clean restart

help:
	@echo "Strava Teams Bot - Available Commands:"
	@echo ""
	@echo "  make build     - Build the Docker image"
	@echo "  make up        - Start the bot in background"
	@echo "  make down      - Stop the bot"
	@echo "  make logs      - View bot logs (follow mode)"
	@echo "  make test      - Test posting to Teams"
	@echo "  make dry-run   - Show what would be posted (no actual posting)"
	@echo "  make restart   - Restart the bot"
	@echo "  make clean     - Remove containers and images"
	@echo ""

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✓ Bot started! View logs with: make logs"

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	docker-compose run --rm bot python main.py --test

dry-run:
	docker-compose run --rm bot python main.py --dry-run

restart:
	docker-compose restart
	@echo "✓ Bot restarted!"

clean:
	docker-compose down -v --rmi all
	@echo "✓ Cleaned up containers and images"
