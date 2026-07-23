#!/bin/bash
set -euo pipefail

PROJECT_DIR="$HOME/MLH-Meta-PE-Portfolio"
BACKUP_DIR="$PROJECT_DIR/backups"
SCRATCH_CONTAINER="myportfolio-restore-check"
SCRATCH_PASSWORD=$(openssl rand -hex 16)

cleanup() {
  docker rm -f "$SCRATCH_CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

cd "$PROJECT_DIR"
source .env

LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/*.sql.gz | head -n1)
if [ -z "$LATEST_BACKUP" ]; then
  echo "No backups found in $BACKUP_DIR"
  exit 1
fi
echo "Verifying $LATEST_BACKUP..."

docker run -d --name "$SCRATCH_CONTAINER" \
  -e MYSQL_ROOT_PASSWORD="$SCRATCH_PASSWORD" \
  -e MYSQL_DATABASE="$MYSQL_DATABASE" \
  mariadb >/dev/null

echo "Waiting for scratch database to come up..."
until docker exec -e MYSQL_PWD="$SCRATCH_PASSWORD" "$SCRATCH_CONTAINER" mariadb -uroot -e "SELECT 1;" >/dev/null 2>&1; do
  sleep 2
done

echo "Loading backup into scratch database..."
gunzip -c "$LATEST_BACKUP" | docker exec -i -e MYSQL_PWD="$SCRATCH_PASSWORD" "$SCRATCH_CONTAINER" \
  mariadb -uroot "$MYSQL_DATABASE"

RESTORED_COUNT=$(docker exec -e MYSQL_PWD="$SCRATCH_PASSWORD" "$SCRATCH_CONTAINER" \
  mariadb -uroot -N -e "SELECT COUNT(*) FROM timelinepost;" "$MYSQL_DATABASE")
LIVE_COUNT=$(docker compose -f docker-compose.prod.yml exec -T -e MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql \
  mariadb -uroot -N -e "SELECT COUNT(*) FROM timelinepost;" "$MYSQL_DATABASE")

echo "Live row count: $LIVE_COUNT"
echo "Restored row count: $RESTORED_COUNT"

if [ "$RESTORED_COUNT" -eq "$LIVE_COUNT" ]; then
  echo "PASS: backup restores cleanly and row counts match."
else
  echo "FAIL: row count mismatch between live database and restored backup."
  exit 1
fi
