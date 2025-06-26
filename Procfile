web: cd src/ClassiQue && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn ClassiQue.wsgi:application --bind 0.0.0.0:$PORT
