#!/bin/bash
# ---------------------------------------------------------------------------
# 🚀 Connect directly to PostgreSQL container (not backend)
# ---------------------------------------------------------------------------

DB_CONTAINER="train_db"
DB_USER="admin"
DB_NAME="train_db"

echo "🔍 Checking if database container ($DB_CONTAINER) is running..."
if ! docker ps --format '{{.Names}}' | grep -q "$DB_CONTAINER"; then
  echo "❌ Error: Container '$DB_CONTAINER' is not running!"
  echo "➡️  Start your containers first with: docker compose up -d"
  exit 1
fi

echo "🐘 Connecting to PostgreSQL inside '$DB_CONTAINER'..."
docker exec -it "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME"
