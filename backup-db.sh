#!/bin/bash
set -euo pipefail

PROJECT_DIR="$HOME/MLH-Meta-PE-Portfolio"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

cd "$PROJECT_DIR"
source .env

mkdir -p "$BACKUP_DIR"

echo "Dumping $MYSQL_DATABASE..."
docker compose -f docker-compose.prod.yml exec -T mysql \
  mariadb-dump -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" \
  | gzip > "$BACKUP_DIR/$MYSQL_DATABASE-$TIMESTAMP.sql.gz"

echo "Backup written to $BACKUP_DIR/$MYSQL_DATABASE-$TIMESTAMP.sql.gz"
