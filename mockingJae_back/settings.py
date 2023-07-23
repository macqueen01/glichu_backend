"""
Django settings for django_backend project.
Generated by 'django-admin startproject' using Django 4.0.6.
For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
from datetime import timedelta
from rest_framework.settings import api_settings
from dotenv import load_dotenv
from storages.backends.s3boto3 import S3Boto3Storage
import os
import boto3
import freesound

from .storages import LocalStorage, S3Storage

# maybe in only local device
import pymysql

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-h%a&ef4=qi5ggo6j%od8x+*+!yn@&#&0qwl=42^)5l7vwi7*e('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]



# Application definition

INSTALLED_APPS = [
    # implemented apps
    'channels',
    'main.apps.MainConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'notifications',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # dependency
    'storages',
    'rest_framework',
    #'background_task', --> does not support current version
    'corsheaders',
    'knox',
    #'oauth2_provider',
    #'social_django',
    #'rest_framework_social_oauth2',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True

#CSRF_TRUSTED_ORIGINS = ['http://172.20.10.9:5174']

ROOT_URLCONF = 'mockingJae_back.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'mockingJae_back.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

pymysql.install_as_MySQLdb()


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get("DB_NAME"),
        'USER': os.environ.get("DB_USER"),
        'PASSWORD': os.environ.get("DB_PASSWORD"),
        'HOST': os.environ.get("DB_HOST"),
        'PORT': os.environ.get("DB_PORT"),
    }
}

# Rest framework

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        'knox.auth.TokenAuthentication',
        #'oauth2_provider.contrib.rest_framework.OAuth2Authentication',  # django-oauth-toolkit >= 1.0.0
        #'rest_framework_social_oauth2.authentication.SocialAuthentication',
    )
}


REST_KNOX = {
    'SECURE_HASH_ALGORITHM': 'cryptography.hazmat.primitives.hashes.SHA512',
    'AUTH_TOKEN_CHARACTER_LENGTH': 64,
    'TOKEN_TTL': timedelta(weeks = 8),
    'TOKEN_LIMIT_PER_USER': None,
    'AUTO_REFRESH': False,
    'EXPIRY_DATETIME_FORMAT': api_settings.DATETIME_FORMAT,
}


"""
AUTHENTICATION_BACKENDS = (
    # Instagram Auth
    'social_core.backends.instagram.InstagramOAuth2'
    # Facebook Auth
    'social_core.backends.facebook.FacebookAppOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',

    'rest_framework_social_oauth2.backends.DjangoOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)
"""


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = 'media/'

# Archives the video (before and after conversion)
ARCHIVE_URL = 'archive/'

MEDIA_ROOT = os.path.join(BASE_DIR, "media")



# ARCHIVE_ROOT stores all streamable videos with thumbnails.
# It is an essential visual database for streaming.
ARCHIVE_ROOT = os.path.join(BASE_DIR, "archive")

# TEMP_ROOT stores all temporary files.
# It is used for video conversion.
TEMP_ROOT = os.path.join(BASE_DIR, "temp")


DEFAULT_FILE_STORAGE = 'mockingJae_back.storages.LocalStorage'
SCROLLS_S3_STORAGE = 'mockingJae_back.storages.S3Storage'

# Model Defaults

AUTH_USER_MODEL = 'main.user'


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# IPFS Storage Configuration
# Only Stores scroll cells in ipfs

#IPFS_STORAGE_API_URL = 'http://localhost:5001/api/v0/'

# for daemon
#IPFS_STORAGE_GATEWAY_URL = 'http://localhost:8080/ipfs/'
# for production
# IPFS_STORAGE_GATEWAY_URL = 'https://ipfs.io/ipfs/'


# Create an S3 client instance
s3_main_bucket = os.environ.get("AWS_STORAGE_BUCKET_NAME")

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_REGION')
)

# Create an S3 resource instance
s3_resource = boto3.resource(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_REGION')
)

# Create an S3 storage instances
s3_storage = S3Storage(
    bucket_name=os.environ.get('AWS_STORAGE_BUCKET_NAME'),
    custom_domain=os.environ.get('AWS_S3_CUSTOM_DOMAIN'),
)

# Freesound api configuration

freesound_client = freesound.FreesoundClient()
freesound_client.set_token(os.environ.get('FREESOUND_API_KEY'),"token")


# Celery configurations


# Notification Settings




# Redis configuration

REDIS_BROKER_CHANEL = 'redis://localhost:6379'

# Websocket configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

ASGI_APPLICATION = 'mockingJae_back.asgi.application'


# Apple Private Key

APPLE_PRIVATE_KEY = """

"""