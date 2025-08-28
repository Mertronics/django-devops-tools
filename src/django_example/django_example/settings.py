# src/project/project/settings.py

import os
from pathlib import Path
import sys

# Build paths inside the project
# Root directory
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
# `src/project` directory
BASE_DIR = Path(__file__).resolve().parent.parent

# If apps directory is needed
#APPS_DIR = BASE_DIR / 'apps'
#sys.path.insert(0, str(APPS_DIR))
#sys.path.insert(0, str(BASE_DIR))

# Determine if running in a Docker container
IS_DOCKER = os.getenv('IS_DOCKER', 'false').lower() == 'true'

# This is crucial for making the setup project-agnostic.
DJANGO_PROJECT_NAME = os.getenv('DJANGO_PROJECT_NAME', BASE_DIR.name)

# Debugging
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'

# Data directory - defaults to project root for standalone, /data for Docker
if IS_DOCKER:
    DATA_DIR = Path('/data')
else:
    # For standalone, create a 'data' directory alongside 'src'
    DATA_DIR = ROOT_DIR / 'data'
    DATA_DIR.mkdir(exist_ok=True)

# Security
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
# If the secret key is not found, we handle it based on the DEBUG state.
if not SECRET_KEY:
    if DEBUG:
        # In development, silently use a predictable, insecure key.
        SECRET_KEY = 'django-insecure-!qa$ob$jie7p-z$k1o280+mtypn39+^$d*y1i+bj(ng%nzz7qs'
    else:
        # In production, a missing key is a fatal error.
        raise ValueError(
            "DJANGO_SECRET_KEY environment variable is required for production (when DEBUG=False)."
        )

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]

# --- PROJECT-SPECIFIC CONFIGURATION ---
# When adapting this template, you will primarily change the settings below.

# Import the modular configurations.
# This works because APPS_DIR is in the sys.path.
#from installed_apps import PROJECT_APPS, THIRD_PARTY_APPS
#from middleware import PROJECT_MIDDLEWARE
#from apps.installed_apps import PROJECT_APPS, THIRD_PARTY_APPS
#from apps.middleware import PROJECT_MIDDLEWARE

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
# Combine the app lists. The order can be important.
# Typically: Django Apps -> Third-Party Apps -> Your Project Apps
#INSTALLED_APPS += THIRD_PARTY_APPS + PROJECT_APPS

# The project's root URL configuration
ROOT_URLCONF = f'{DJANGO_PROJECT_NAME}.urls'

# The WSGI application entrypoint
WSGI_APPLICATION = f'{DJANGO_PROJECT_NAME}.wsgi.application'

# --- END PROJECT-SPECIFIC CONFIGURATION ---

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# Add your project-specific middleware.
# The order matters, so appending is often the safest approach.
#MIDDLEWARE += PROJECT_MIDDLEWARE

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database
# WARNING: SQLite is not recommended for production with multiple workers (Gunicorn)
# due to potential 'database is locked' errors under concurrent write load.
# Consider PostgreSQL for production environments.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATA_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
            # WAL mode is essential for improving SQLite concurrency.
            'init_command': 'PRAGMA journal_mode=WAL;',
        },
    }
}

# Cache configuration
USE_REDIS = os.getenv('USE_REDIS', 'False').lower() == 'true'

if USE_REDIS:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'KEY_PREFIX': os.getenv('COMPOSE_PROJECT_NAME', 'django-project'),
            'TIMEOUT': 300,
        }
    }

    # Use Redis for sessions
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')
USE_I18N = os.getenv('USE_I18N', 'True')
USE_TZ = True

# --- Static and Media Files (Corrected and Consolidated) ---
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# The absolute path to the directory where collectstatic will gather files.
if IS_DOCKER:
    STATIC_ROOT = Path('/app/static') # <-- CHANGED
else:
    STATIC_ROOT = BASE_DIR.parent / 'static' # <-- CHANGED

# The absolute path to the directory that will hold user-uploaded files.
MEDIA_ROOT = DATA_DIR / 'media'

# A list of locations where Django will look for additional static files.
if IS_DOCKER:
    STATICFILES_DIRS = [
        Path('/app/static_source'),
    ]
else:
    STATICFILES_DIRS = [
        BASE_DIR.parent / 'static_source',
    ]

# WhiteNoise configuration for serving static files efficiently
# This section should come AFTER the main MIDDLEWARE list is defined.
if IS_DOCKER:
    # Use the recommended storage backend for production
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    # Insert the WhiteNoise middleware directly after the SecurityMiddleware.
    # This is the officially recommended and most efficient placement.
    try:
        # Find the index of SecurityMiddleware
        security_middleware_index = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
        # Insert WhiteNoiseMiddleware right after it
        MIDDLEWARE.insert(security_middleware_index + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    except ValueError:
        # If SecurityMiddleware is not found, you might have a different setup.
        # A safe fallback is to insert it at the beginning of the list,
        # but be aware of the security implications.
        # For most standard setups, the `try` block will succeed.
        MIDDLEWARE.insert(0, 'whitenoise.middleware.WhiteNoiseMiddleware')
        
# --- End Static and Media Files Section ---


# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
    # This is crucial for SECURE_SSL_REDIRECT to work correctly behind a reverse proxy.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]

# Session settings
SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', '3600'))  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Logging
# Conditionally DEFINE the file handler to prevent
# FileNotFoundError during Docker builds.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose' if DEBUG else 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# For local/standalone runs, add the file handler to the configuration.
if not IS_DOCKER:
    # --- START MODIFICATION ---
    # Define the log directory and ensure it exists before configuring the handler.
    LOG_DIR = DATA_DIR / 'logs'
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    # --- END MODIFICATION ---

    LOGGING['handlers']['file'] = {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': LOG_DIR / 'django.log', # Use the new LOG_DIR variable
        'maxBytes': 10 * 1024 * 1024,  # 10MB
        'backupCount': 5,
        'formatter': 'verbose',
    }
    # These lines remain the same.
    LOGGING['root']['handlers'].append('file')
    LOGGING['loggers']['django']['handlers'].append('file')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'