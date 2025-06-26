#!/bin/bash

# Deploy script for ClassiQue application

echo "Starting deployment process..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Change to Django project directory
cd src/ClassiQue

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create uploads directory if it doesn't exist
mkdir -p uploads

echo "Deployment preparation complete!"
echo "To start the server, run:"
echo "cd src/ClassiQue && python manage.py runserver 0.0.0.0:8000"
