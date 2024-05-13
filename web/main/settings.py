from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(override=True)

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-w(5yuunt#i+31tt@912&lcw&1&(2=)8$omvt&mp&b_9mc2tw5*")

DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "daphne",
    "channels",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users.apps.UsersConfig",
    "logs.apps.LogsConfig",
    "core.apps.CoreConfig",
    "googlecharts",
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

ROOT_URLCONF = "main.urls"

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],
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

if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "postgres"),
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "123456"),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": int(os.getenv("DB_PORT", "5432")),
        }
    }

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

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Asia/Yekaterinburg"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT =  os.path.join(BASE_DIR, "collected_static")
STATICFILES_DIR = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [STATICFILES_DIR]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

LOGIN_URL = "users:user_login"
LOGIN_REDIRECT_URL = "logs:main_page"
LOGOUT_URL = "users:user_logout"

WSGI_APPLICATION = "main.wsgi.application"
ASGI_APPLICATION = 'main.asgi.application'

if DEBUG:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }
else:
    CHANNEL_REDIS_BROKER_URL = 'redis://redis/1'
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [CHANNEL_REDIS_BROKER_URL],
            },
        },
    }

CELERY_BROKER_URL = 'redis://redis/0'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# CELERY_TASK_TRACK_STARTED = True
# CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
# CELERY_TIMEZONE = 'Europe/Moscow'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.mail.ru")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "False") == "True"
EMAIL_PORT = os.getenv("EMAIL_PORT", 465)
EMAIL_USE_SSL =  os.getenv("EMAIL_USE_SSL", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "example@example.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "exampleExample")
DEFAULT_FROM_EMAIL = "log_analyzer@mail.ru"

MTS_API_KEY = os.getenv("MTS_API_KEY", "some_api_key")
MTS_NUMBER = os.getenv("MTS_NUMBER", "some_number")
MTS_SMS_API_URL = "https://api.exolve.ru/messaging/v1/SendSMS"
MTS_CALL_API_URL = "https://api.exolve.ru/call/v1/MakeVoiceMessage"
MTS_CALL_SERVICE_ID = os.getenv("MTS_CALL_SERVICE_ID", "some_call_service_id")