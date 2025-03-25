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
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv

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

load_dotenv()

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
    "workspace", # 3D 모델 작업 공간 앱
    "model_storage",
    "articles", # 메인 화면에 있는 글 관리 앱
    "threeworld", # three.js app
    "utils", # 유틸리티 관련 테스팅 및 관리 앱
    "texture", # 텍스처 작업 공간 앱
    "prompts", # 유저의 프롬프트를 보조해주는 앱
    "vision", # 유저가 생성한 모델링의 이미지를 평가하는 앱

    # DRF & Swagger
    "rest_framework",
    "drf_yasg",

    'storages',

    # API v1
    'api_v1',

    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # JS와 연결하기
    "corsheaders.middleware.CorsMiddleware",
]

CORS_ALLOW_ALL_ORIGINS = True  # 개발 중에는 허용

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
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

if IS_LOCAL_ENV:
    DATABASES = {
        'default': {
            'ENGINE': os.getenv('DB_ENGINE'),
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT'),
        }
    }
else:
    KV_URI = f"https://miravelle-key.vault.azure.net/"

    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KV_URI, credential=credential)

    def get_secret(name):
        try:
            return client.get_secret(name).value
        except Exception as e:
            print(f"Failed to retrieve {name}: {e}")
            return None

    DATABASES = {
        'default': {
            'ENGINE': get_secret('DB-ENGINE'),
            'NAME': get_secret('DB-NAME'),
            'USER': get_secret('DB-USER'),
            'PASSWORD': get_secret('DB-PASSWORD'),
            'HOST': get_secret('DB-HOST'),
            'PORT': get_secret('DB-PORT'),
        }
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

# DRF 설정
# REST_FRAMEWORK = {
#     # **API 설정**

#     # 1. 기본 인증 방식 (Authentication Classes)
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.authentication.SessionAuthentication',  # Django 세션 인증 (웹 브라우저)
#         'rest_framework.authentication.TokenAuthentication',    # 토큰 인증 (API 클라이언트)
#         # 필요에 따라 JWT 인증 추가 가능:
#         # 'rest_framework_simplejwt.authentication.JWTAuthentication',
#     ],

#     # 2. 기본 권한 설정 (Permission Classes)
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.IsAuthenticatedOrReadOnly', # 읽기 권한은 누구나, 쓰기 권한은 인증된 사용자만
#         # 'rest_framework.permissions.IsAuthenticated',         # 인증된 사용자만 접근 가능
#         # 'rest_framework.permissions.AllowAny',                # 누구나 접근 가능 (개발/테스트 환경)
#     ],

#     # **페이지네이션 설정**
#     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination', # 페이지 번호 기반 페이지네이션
#     'PAGE_SIZE': 10,        # 한 페이지당 항목 수

#     # **기타 설정**

#     # 3. 예외 처리 (Exception Handling)
#     'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler', # DRF 기본 예외 처리 사용

#     # 4. Content Negotiation 설정 (콘텐츠 협상)
#     'DEFAULT_CONTENT_TYPE': 'application/json', # 기본 콘텐츠 타입

#     # 5. Renderer 설정 (응답 형식)
#     'DEFAULT_RENDERER_CLASSES': [
#         'rest_framework.renderers.JSONRenderer',           # JSON 형식
#         'rest_framework.renderers.BrowsableAPIRenderer',    # browsable API (웹 브라우저)
#     ],

#     # 6. 파서 설정 (요청 형식)
#     'DEFAULT_PARSER_CLASSES': [
#         'rest_framework.parsers.JSONParser',
#         'rest_framework.parsers.FormParser',
#         'rest_framework.parsers.MultiPartParser'
#     ],

#     # 7. API 버전 관리
#     'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning', # Accept 헤더 기반 버전 관리
#     'DEFAULT_VERSION': 'v1',  # 기본 API 버전

#     # 8. 스키마 생성 설정
#     'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
# }


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 모든 도메인 허용
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['*']
CORS_ALLOW_HEADERS = ['*']