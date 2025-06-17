#!/bin/bash
# entrypoint.sh

# retrive secrets from Google Cloud Secret Manager
export SECRET_KEY=$(gcloud secrets versions access latest --secret=SECRET_KEY)
export DATABASE_URL=$(gcloud secrets versions access latest --secret=DATABASE_URL)


# Waiting for database to be available (optional but recommended)
echo "Waiting for database..."
sleep 5

# Run migrate in production
echo "Applying database migrations..."
python manage.py migrate

# Start the application
echo "Starting application..."

exec "$@"