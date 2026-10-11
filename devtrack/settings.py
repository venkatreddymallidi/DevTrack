"""Minimal settings for the JSON-backed DevTrack exercise.

Do not use this development configuration directly in production.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-devtrack-local-development-only')
DEBUG = os.environ.get('DJANGO_DEBUG', 'true').lower() == 'true'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

INSTALLED_APPS = ['issues']
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]
ROOT_URLCONF = 'devtrack.urls'
TEMPLATES = []
WSGI_APPLICATION = 'devtrack.wsgi.application'
ASGI_APPLICATION = 'devtrack.asgi.application'

# No Django ORM models or SQL database: this assignment stores records in JSON files.
DATABASES = {}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
