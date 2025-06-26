#!/usr/bin/env bash
# Render build script - runs automatically during build phase

set -o errexit  # exit on error

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Build completed successfully!"
