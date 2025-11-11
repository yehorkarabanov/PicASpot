#!/bin/sh
set -e

echo "Waiting for PostgreSQL to be ready..."
# Wait for postgres to be ready
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - checking and running migrations safely"
alembic_head=$(uv run alembic heads | awk '{print $1}')
if [ -z "$alembic_head" ]; then
  echo "No migration heads found. Skipping migration."
else
  alembic_current=$(uv run alembic current 2>/dev/null | awk '{print $1}')
  if [ -z "$alembic_current" ]; then
    echo "Alembic not initialized or no current revision. Initializing and upgrading to head."
    uv run alembic upgrade head
  elif [ "$alembic_current" = "$alembic_head" ]; then
    echo "Database is up to date with latest migration ($alembic_head)."
  else
    if uv run alembic history | grep -q "$alembic_current"; then
      echo "Database revision ($alembic_current) is behind head ($alembic_head). Upgrading."
      uv run alembic upgrade head
    else
      echo "Warning: Database revision ($alembic_current) is ahead of current branch head ($alembic_head). Skipping migration."
    fi
  fi
fi

echo "Starting FastAPI application..."
exec "$@"
