"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-ahgtht+0)cqb@vhats1co9jsj622h9)zvy845)sl644ws-5j2$"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# 로컬 환경인지 배포 환경인지 체크(Main의 경우 항상 False 유지)
IS_LOCAL_ENV = False

# CSRF 설정
CSRF_TRUSTED_ORIGINS = [
    'https://miravelle-appservice-dsecega7bbhvefem.koreacentral-01.azurewebsites.net'
]

# Session 설정
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Cache 설정
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# user 모델 선언
AUTH_USER_MODEL = "users.User"

ALLOWED_HOSTS = [
    "miravelle-appservice-dsecega7bbhvefem.koreacentral-01.azurewebsites.net",
    "127.0.0.1",
    "localhost",
]
# 로그인 URL 추가
LOGIN_URL = "/users/login/"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = ""
if IS_LOCAL_ENV:
    STATIC_URL = "/static/"
else:
    STATIC_URL = f"https://miravelledevstorage.blob.core.windows.net/staticfiles/"

# 정적 파일 경로 설정
STATICFILES_DIRS = [
os.path.join(BASE_DIR, 'core/static'),
]

# 배포 환경에서 정적 파일을 모을 경로
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (Uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # Uploaded files save path

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # Create app list
    "users", # 유저 관라 앱
    "assets", # 유저가 생상한 모델을 볼 수 있는 공간 관리 앱
    "workspace", # 작업 공간 앱
    "model_storage",
    "articles", # 메인 화면에 있는 글 관리 앱
    "threeworld", # three.js app
    "utils", # 유틸리티 관련 테스팅 및 관리 앱

    # DRF & Swagger
    "rest_framework",
    "drf_yasg",

    'storages',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# 개발/배포 환경 구분 
IS_PRODUCTION = os.environ.get('AZURE_WEBSITE_NAME') is not None 

# 추후에 PostgreSQL로 전환 (권장)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:' if IS_PRODUCTION else os.path.join(BASE_DIR, 'db.sqlite3'),
    } # 메모리 기반 DB, 만약 로컬 서버라면 db.sqlite3
}

# File Permissions
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
