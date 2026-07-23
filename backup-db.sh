#!/bin/bash
set -euo pipefail

PROJECT_DIR="$HOME/MLH-Meta-PE-Portfolio"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

cd "$PROJECT_DIR"
source .env

report_failure() {
  curl -fsS -m 10 --retry 3 "$HEALTHCHECKS_URL/fail" >/dev/null 2>&1 || true
}
trap report_failure ERR

mkdir -p "$BACKUP_DIR"

echo "Dumping $MYSQL_DATABASE..."
docker compose -f docker-compose.prod.yml exec -T -e MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql \
  mariadb-dump -u root "$MYSQL_DATABASE" \
  | gzip > "$BACKUP_DIR/$MYSQL_DATABASE-$TIMESTAMP.sql.gz"

echo "Backup written to $BACKUP_DIR/$MYSQL_DATABASE-$TIMESTAMP.sql.gz"

curl -fsS -m 10 --retry 3 "$HEALTHCHECKS_URL" >/dev/null 2>&1 || true
