# ClassiQue Deployment Guide

This guide provides instructions for deploying the ClassiQue Django application on various platforms.

## Prerequisites

- Python 3.11+
- Git
- Required system dependencies for audio/image processing

## Local Development Setup

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run deployment script:
   ```bash
   # On Linux/Mac
   chmod +x deploy.sh
   ./deploy.sh
   
   # On Windows
   deploy.bat
   ```
5. Start the development server:
   ```bash
   cd src/ClassiQue
   python manage.py runserver
   ```

## Production Deployment Options

### 1. Heroku Deployment

1. Install Heroku CLI
2. Login to Heroku: `heroku login`
3. Create new app: `heroku create your-app-name`
4. Set environment variables:
   ```bash
   heroku config:set DJANGO_SETTINGS_MODULE=ClassiQue.settings_production
   heroku config:set DEBUG=False
   ```
5. Deploy:
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```
6. Run migrations:
   ```bash
   heroku run python src/ClassiQue/manage.py migrate
   ```

### 2. Railway Deployment

1. Connect your GitHub repository to Railway
2. Set environment variables:
   - `DJANGO_SETTINGS_MODULE=ClassiQue.settings_production`
   - `DEBUG=False`
3. Railway will automatically deploy using the Procfile

### 3. DigitalOcean App Platform

1. Connect your GitHub repository
2. Configure build settings:
   - Build command: `pip install -r requirements.txt`
   - Run command: `cd src/ClassiQue && gunicorn ClassiQue.wsgi:application --bind 0.0.0.0:8080`
3. Set environment variables as above

### 4. Docker Deployment

1. Build the image:
   ```bash
   docker build -t classique .
   ```
2. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

### 5. VPS/Cloud Server Deployment

1. Set up server (Ubuntu/CentOS)
2. Install Python, pip, and dependencies:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip nginx
   ```
3. Clone repository and setup:
   ```bash
   git clone <repository-url>
   cd ClassiQue
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ./deploy.sh
   ```
4. Configure Nginx:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location /static/ {
           alias /path/to/ClassiQue/src/ClassiQue/staticfiles/;
       }
       
       location /media/ {
           alias /path/to/ClassiQue/src/ClassiQue/uploads/;
       }
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```
5. Start with Gunicorn:
   ```bash
   cd src/ClassiQue
   gunicorn ClassiQue.wsgi:application --bind 127.0.0.1:8000 --daemon
   ```

## Environment Variables

For production deployment, set these environment variables:

- `DJANGO_SETTINGS_MODULE=ClassiQue.settings_production`
- `DEBUG=False`
- `SECRET_KEY=your-secret-key` (generate a new one for production)
- `ALLOWED_HOSTS=your-domain.com,www.your-domain.com`

## Post-Deployment Steps

1. Run migrations: `python manage.py migrate`
2. Collect static files: `python manage.py collectstatic`
3. Create uploads directory and ensure proper permissions
4. Upload your dataset files to the uploads directory
5. Test the application functionality

## Troubleshooting

### Common Issues:

1. **Static files not loading**: Ensure `collectstatic` was run and web server is configured correctly
2. **File upload errors**: Check uploads directory permissions
3. **Audio/Image processing errors**: Ensure all dependencies are installed
4. **Database errors**: Run migrations and check database connectivity

### Performance Optimization:

1. Use a proper database (PostgreSQL) for production
2. Configure caching (Redis/Memcached)
3. Use a CDN for static files
4. Optimize image/audio file sizes
5. Configure proper logging and monitoring

## Security Considerations

1. Always set `DEBUG=False` in production
2. Use environment variables for sensitive data
3. Configure proper ALLOWED_HOSTS
4. Use HTTPS in production
5. Regular security updates

## Monitoring and Maintenance

1. Set up logging and error tracking
2. Monitor resource usage (CPU, memory, disk)
3. Regular backups of database and media files
4. Keep dependencies updated
5. Monitor application performance
