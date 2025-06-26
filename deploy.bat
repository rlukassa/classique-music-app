@echo off

REM Deploy script for ClassiQue application on Windows

echo Starting deployment process...

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Change to Django project directory
cd src\ClassiQue

REM Run migrations
echo Running database migrations...
python manage.py migrate

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput

REM Create uploads directory if it doesn't exist
if not exist uploads mkdir uploads

echo Deployment preparation complete!
echo To start the server, run:
echo cd src\ClassiQue ^&^& python manage.py runserver 0.0.0.0:8000
