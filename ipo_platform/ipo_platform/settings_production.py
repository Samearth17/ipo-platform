"""Render-ready production settings."""
import os
import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from .settings import *

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.environ['SECRET_KEY']
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]
DATABASES = {'default': dj_database_url.parse(os.environ['DATABASE_URL'], conn_max_age=600, ssl_require=True)}

# Render supplies these values directly. Production must never silently start
# with an empty OAuth client configuration because allauth would then build an
# invalid authorization URL without client_id.
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()
if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    raise ImproperlyConfigured(
        'Google OAuth is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.'
    )

SOCIALACCOUNT_PROVIDERS['google']['APP'].update({
    'client_id': GOOGLE_CLIENT_ID,
    'secret': GOOGLE_CLIENT_SECRET,
    'key': '',
})
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware', 'whitenoise.middleware.WhiteNoiseMiddleware'] + [m for m in MIDDLEWARE if m != 'django.middleware.security.SecurityMiddleware']
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
LOGGING = {'version': 1, 'disable_existing_loggers': False, 'handlers': {'console': {'class': 'logging.StreamHandler'}}, 'root': {'handlers': ['console'], 'level': 'INFO'}}
