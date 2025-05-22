#!/bin/bash
# entrypoint.sh

# retrive secrets from Google Cloud Secret Manager
export SECRET_KEY=$(gcloud secrets versions access latest --secret=SECRET_KEY)
export DATABASE_URL=$(gcloud secrets versions access latest --secret=DATABASE_URL)

# execute migrations
python manage.py makemigrations --noinput
python manage.py migrate --noinput

exec "$@"