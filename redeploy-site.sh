#!/bin/bash
set -e

PROJECT_DIR="$HOME/MLH-Meta-PE-Portfolio"

echo "Pulling latest changes from main..."
cd "$PROJECT_DIR"
git fetch
git reset origin/main --hard

echo "Stopping containers (avoids OOM on this box while the next build runs)..."
docker compose -f docker-compose.prod.yml down

echo "Rebuilding and starting containers..."
docker compose -f docker-compose.prod.yml up -d --build

echo "Done. Container status:"
docker compose -f docker-compose.prod.yml ps
