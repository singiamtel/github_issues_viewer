#!/bin/sh

set -e

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start server
echo "Starting server..."
gunicorn github_issues.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile - --error-logfile - --log-level info 