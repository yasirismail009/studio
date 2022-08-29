# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from decouple import config
from unipath import Path
import sys
from core import secrets

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent

CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_1122')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# load production server from .env
ALLOWED_HOSTS = ['localhost', '*', '127.0.0.1', config('SERVER', default='127.0.0.1')]

# Fix for Font-Awesome Invalid Package name because of dashes in it
sys.modules['fontawesome_free'] = __import__('fontawesome-free')
# Application definition

INSTALLED_APPS = [
    'admin_volt.apps.AdminVoltConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.home',  # Enable the inner home (home)
    "fontawesome_free",

]

MIDDLEWARE = [
    # 'honeybadger.contrib.DjangoHoneybadgerMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'
LOGIN_REDIRECT_URL = "home"  # Route defined in home/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in home/urls.py
TEMPLATE_DIR = os.path.join(CORE_DIR, "apps/templates")  # ROOT dir for templates

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = secrets.DATABASE

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

#############################################################
# SRC: https://devcenter.heroku.com/articles/django-assets

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(CORE_DIR, 'apps/static2'),
)

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR.parent, 'media')
# print(MEDIA_ROOT)
# MEDIA_URL = 'media/'

# import os.path
# ABSOLUTE_PATH = lambda x: os.path.join(os.path.abspath(os.path.dirname(__file__)), x)
# MEDIA_ROOT = ABSOLUTE_PATH('media/')
#############################################################
#############################################################


# BROKER_URL = "redis://:" + secrets.REDIS_PASSWORD + "@127.0.0.1:" + str(secrets.REDIS_PORT)
# CELERY_RESULT_BACKEND = "redis://:" + secrets.REDIS_PASSWORD + "@127.0.0.1:" + str(secrets.REDIS_PORT)
# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_TASK_TRACK_STARTED = True
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = TIME_ZONE
# DJANGO_CELERY_BEAT_TZ_AWARE = False
#
# CELERY = {
#     'BROKER_URL': 'redis://localhost:6379',
#     'CELERY_RESULT_BACKEND': 'redis://localhost:6379',
#     'CELERYBEAT_SCHEDULER': 'djcelery.schedulers.DatabaseScheduler',
#     'CELERY_TIMEZONE': TIME_ZONE,
#     'CELERY_ACCEPT_CONTENT': ['application/json'],
#     "CELERY_TASK_SERIALIZER": 'json',
#     "CELERY_RESULT_SERIALIZER": 'json',
#     "CELERY_TASK_TRACK_STARTED": True
#
# }
# CELERY STUFF
# CELERY_BROKER_URL = 'redis://localhost:6379'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379'
# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TASK_TRACK_STARTED = True
# CELERY_TIMEZONE = 'Africa/Nairobi'
# CELERY_TIMEZONE = TIME_ZONE
# DJANGO_CELERY_BEAT_TZ_AWARE = False
CELERY_BROKER_URL = 'amqp://localhost'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s',
            'datefmt': '%y %b %d, %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'celery': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'celery.log',
            'formatter': 'simple',
            'maxBytes': 1024 * 1024 * 100,  # 100 mb
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['celery', 'console'],
            'level': 'INFO',
        },
    }
}

from logging.config import dictConfig

dictConfig(LOGGING)

# WKHTMLTOPDF_CMD = 'C:\Program Files\wkhtmltopdf\bin'

