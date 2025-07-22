import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
from decimal import Decimal

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_yasg',
    'core',
    'promos',
    'restaurants',
    'menu',
    'orders',
    'courier',
    'reviews',
    'notifications',
    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jetfood_backend.urls'
AUTH_USER_MODEL = 'core.User'
WSGI_APPLICATION = 'jetfood_backend.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
}

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

RESTAURANT_COMMISSION_PERCENT = Decimal(os.getenv('RESTAURANT_COMMISSION_PERCENT', '20'))
COURIER_COMMISSION_PERCENT = Decimal(os.getenv('COURIER_COMMISSION_PERCENT', '5.0'))
CLIENT_SERVICE_FEE_PERCENT = Decimal(os.getenv('CLIENT_SERVICE_FEE_PERCENT', '5.0'))
MIN_CLIENT_SERVICE_FEE = Decimal(os.getenv('MIN_CLIENT_SERVICE_FEE', '100.0'))
MAX_CLIENT_SERVICE_FEE = Decimal(os.getenv('MAX_CLIENT_SERVICE_FEE', '300.0'))

ROBOKASSA_MERCHANT_LOGIN = os.getenv('ROBOKASSA_MERCHANT_LOGIN')
ROBOKASSA_PASSWORD_1 = os.getenv('ROBOKASSA_PASSWORD_1')
ROBOKASSA_PASSWORD_2 = os.getenv('ROBOKASSA_PASSWORD_2')
ROBOKASSA_IS_TEST = os.getenv('ROBOKASSA_IS_TEST', '1') == '1'
