"""
Django settings for crm_upi project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import environ
import os

env = environ.Env(
    DEBUG=(bool, True)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

DJANGO_KEY = env('DJANGO_KEY')
EMAIL_USER = env('EMAIL_USER')
EMAIL_PASSWORD = env('EMAIL_PASSWORD')
AWS_ID = env('AWS_ID')
AWS_STORAGE_NAME = env('AWS_STORAGE_NAME')
AWS_KEY = env('AWS_KEY')
DB_USER = env('DB_USER')
DB_PASSWORD = env('DB_PASSWORD')
DB_HOST = env('DB_HOST')
DB_NAME = env('DB_NAME')
REDIS_URL = env('REDIS_REDIS_URL')

LOGIN_URL = '/login/'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = f'{DJANGO_KEY}'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False  # Purely for deploy

CSRF_TRUSTED_ORIGINS = ['https://crm-upi.vercel.app',
                        'https://crm-upi-jinkosizs-projects-4c8f9ac9.vercel.app',
                        'https://crm-upi-git-main-jinkosizs-projects-4c8f9ac9.vercel.app',
                        'https://127.0.0.1',
                        'https://jinkosiz-crm-upi-9cfc.twc1.net',
                        'https://demotimetracker.ru',
                        'https://89.223.120.50',
                        'https://upi-test.ru',
                        'https://jinkosiz-crm-upi-e64a.twc1.net',
                        'https://jinkosiz-crm-upi-77a2.twc1.net',
                        'https://89.23.115.23']

ALLOWED_HOSTS = ['crm-upi.vercel.app',
                 'crm-upi-jinkosizs-projects-4c8f9ac9.vercel.app',
                 'crm-upi-git-main-jinkosizs-projects-4c8f9ac9.vercel.app',
                 '127.0.0.1',
                 'jinkosiz-crm-upi-9cfc.twc1.net',
                 'demotimetracker.ru',
                 '89.223.120.50',
                 'upi-test.ru',
                 'jinkosiz-crm-upi-e64a.twc1.net',
                 'jinkosiz-crm-upi-77a2.twc1.net',
                 '89.23.115.23']

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

    'task_manager',
    'corsheaders',
    'storages',
    'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1'
]

ROOT_URLCONF = 'crm_upi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'task_manager.context_processors.all_users',
            ],
        },
    },
]

WSGI_APPLICATION = 'crm_upi.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        'NAME': f'{DB_NAME}',
        'USER': f'{DB_USER}',
        'PASSWORD': f'{DB_PASSWORD}',
        'HOST': f'{DB_HOST}',
        'PORT': '5432',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,  # Адрес Redis-сервера
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ru'  # Assuming Russian is the preferred language
TIME_ZONE = 'Europe/Moscow'  # Set the appropriate time zone
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

if DEBUG:
    # Use local static files in development
    STATIC_URL = '/static/'
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    # Use S3 for static files in production
    STATIC_URL = 'https://s3.timeweb.com/7777fb51-34f4640c-d71e-4ace-b57e-e7997a1f4952/static/'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Media files (Uploaded content)
MEDIA_URL = '/images/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/images')

# Для хранения всех собранных статических файлов (для продакшена)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Места, где Django будет искать статические файлы
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID = f'{AWS_ID}'
AWS_SECRET_ACCESS_KEY = f'{AWS_KEY}'
AWS_STORAGE_BUCKET_NAME = f'{AWS_STORAGE_NAME}'
AWS_S3_ENDPOINT_URL = 'https://s3.timeweb.com'

AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False

AUTH_USER_MODEL = 'task_manager.CustomUser'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.s-pi.ru'
EMAIL_PORT = 25
EMAIL_USE_SSL = False
EMAIL_USE_TLS = False
EMAIL_TIMEOUT = 10
EMAIL_HOST_USER = f'{EMAIL_USER}'
EMAIL_HOST_PASSWORD = f'{EMAIL_PASSWORD}'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


def show_toolbar(request):
    return False  # Всегда показывать toolbar (используйте только для отладки)


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
}
