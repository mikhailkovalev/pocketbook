"""
Django settings for pocketbook project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

from .helpers import get_config


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))

default_config_path = os.path.abspath(
    os.path.join(
        BASE_DIR,
        os.pardir,
        'pocketbook_meta',
        'project_conf.json',
    )
)
config = get_config(default_config_path)

# Quick-start development settings - unsuitable
# for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

security_section = config.get('security', {})

# SECURITY WARNING: keep the secret key used in
# production secret!
SECRET_KEY = security_section.get('SECRET_KEY')
assert isinstance(SECRET_KEY, str)

# SECURITY WARNING: don't run with debug turned
# on in production!
DEBUG = security_section.get('DEBUG')
assert isinstance(DEBUG, bool)

ALLOWED_HOSTS = security_section.get(
    'ALLOWED_HOSTS')
assert isinstance(ALLOWED_HOSTS, list)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'sugar',
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

ROOT_URLCONF = 'main.urls'

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

WSGI_APPLICATION = 'main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = config.get('databases')
assert isinstance(DATABASES, dict)


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/
i18n_section = config.get(
    'internationalization', {})

LANGUAGE_CODE = i18n_section.get(
    'LANGUAGE_CODE', 'en-us')

TIME_ZONE = i18n_section.get(
    'TIME_ZONE', 'UTC')

USE_I18N = i18n_section.get(
    'USE_I18N', True)

USE_L10N = i18n_section.get(
    'USE_L10N', True)

USE_TZ = i18n_section.get(
    'USE_TZ', True)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
static_section = config.get('static', {})

STATIC_URL = static_section.get('STATIC_URL')
assert isinstance(STATIC_URL, str)

MEDIA_ROOT = static_section.get('MEDIA_ROOT')
assert isinstance(MEDIA_ROOT, str)

MEDIA_URL = static_section.get('MEDIA_URL')
assert isinstance(MEDIA_URL, str)

STATIC_ROOT = static_section.get('STATIC_ROOT')
assert isinstance(STATIC_ROOT, str)
