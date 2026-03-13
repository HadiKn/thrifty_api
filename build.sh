#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate --no-input

# Collect static files
python manage.py collectstatic --no-input --clear

# Create superuser with error handling
echo "Creating superuser..."
cat <<EOF | python manage.py shell || true
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if not all([username, email, password]):
    print("Error: Missing required environment variables")
    exit(1)

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser {username} created successfully")
else:
    print(f"Superuser {username} already exists")
EOF