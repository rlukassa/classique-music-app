import os
import sys

# Path to your project directory
path = '/home/rlukassa/ClassiQue/src/ClassiQue'  # Ganti 'yourusername' dengan username PythonAnywhere kamu
if path not in sys.path:
    sys.path.insert(0, path)

# Path to virtual environment
path = '/home/rlukassa/venv/lib/python3.11/site-packages'  # Ganti 'yourusername'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ClassiQue.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
