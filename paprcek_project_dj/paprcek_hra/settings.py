from pathlib import Path
import os
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-test-key-replace-me')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

CSRF_TRUSTED_ORIGINS = [
    'https://paprcekmonimerka.cz',
]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DEBUG = True  

ALLOWED_HOSTS = ['*'] 

BASE_DIR = Path(__file__).resolve().parent.parent

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

APPEND_SLASH = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tictactoe', 
    'logic',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'paprcek_hra.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Zde budeme hledat šablonu rozcestníku
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'paprcek_hra.wsgi.application'

# Databáze - SQLite pro začátek
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Jazykové nastavení
LANGUAGE_CODE = 'cs'
TIME_ZONE = 'Europe/Prague'
USE_I18N = True
USE_L10N = True

LANGUAGES = [
    ('cs', _('Czech')),
    ('en', _('English')),
]

LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_SECURE = True 
LANGUAGE_COOKIE_SAMESITE = 'Lax'
LANGUAGE_COOKIE_DOMAIN = None 

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}