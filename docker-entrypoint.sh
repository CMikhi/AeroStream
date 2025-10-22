#!/bin/sh

# Docker entrypoint script for the NestJS backend
set -e

echo "Starting IgniteDemo NestJS Backend Container (entrypoint)..."

# Set default values if environment variables are not set
DATABASE_PATH=${DATABASE_PATH:-/app/data/database.db}
PORT=${PORT:-3000}
NODE_ENV=${NODE_ENV:-production}

echo "Environment: $NODE_ENV"
echo "Port: $PORT"

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
# Create a symlink to maintain compatibility with the NestJS application
if [ "$DATABASE_PATH" != "/app/database.db" ]; then
    ln -sf "$DATABASE_PATH" /app/database.db
fi

echo "Database configured at: $DATABASE_PATH"

# Wait a moment to ensure all setup is complete
sleep 2

echo "Starting NestJS application on port $PORT..."

# Execute the command passed to the container
exec "$@"