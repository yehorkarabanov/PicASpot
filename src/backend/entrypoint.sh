#!/bin/sh
set -e

echo "Waiting for PostgreSQL to be ready..."
# Wait for postgres to be ready
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - running migrations"
uv run alembic upgrade head

echo "Starting FastAPI application..."
exec "$@"

