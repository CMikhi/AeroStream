#!/bin/bash

# Docker entrypoint script for the FastAPI backend
set -e

echo "Starting IgniteDemo Backend Container..."

# Set default values if environment variables are not set
DATABASE_PATH=${DATABASE_PATH:-/app/data/database.db}
PORT=${PORT:-8000}

# Create data directory if it doesn't exist
mkdir -p "$(dirname "$DATABASE_PATH")"

# Check if database exists, if not copy the initial one
if [ ! -f "$DATABASE_PATH" ]; then
    if [ -f "/app/database.db" ]; then
        echo "Copying initial database to persistent storage..."
        cp /app/database.db "$DATABASE_PATH"
    else
        echo "No initial database found, will be created automatically by the application"
    fi
fi

# Update the database path in the backend configuration if needed
# The backend already looks for database.db in the parent directory of backend/
# So we'll create a symlink to maintain compatibility
if [ "$DATABASE_PATH" != "/app/database.db" ]; then
    ln -sf "$DATABASE_PATH" /app/database.db
fi

echo "Database configured at: $DATABASE_PATH"
echo "Starting FastAPI application on port $PORT..."

# Execute the command passed to the container
exec "$@"