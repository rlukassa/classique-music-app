# Docker configuration for ClassiQue
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Change to Django directory
WORKDIR /app/src/ClassiQue

# Collect static files
RUN python manage.py collectstatic --noinput --settings=ClassiQue.settings_production

# Create uploads directory and copy demo data
RUN mkdir -p uploads
RUN cp -r demo/* uploads/ 2>/dev/null || true

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "ClassiQue.wsgi:application", "--bind", "0.0.0.0:8000"]
