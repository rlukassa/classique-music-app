#!/usr/bin/env bash
# Render deployment script

set -o errexit  # exit on error

# Install dependencies
pip install -r requirements.txt

# Navigate to Django project
cd src/ClassiQue

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Copy demo data if available
mkdir -p uploads
cp -r demo/* uploads/ 2>/dev/null || echo "No demo data found"

echo "Build completed successfully!"
