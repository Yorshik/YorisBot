from pathlib import Path

import decouple

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = decouple.config('SECRET_KEY', default='unsafe-secret')

DEBUG = decouple.config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "YorisDB.database",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": decouple.config('POSTGRES_DB', default='postgres'),
        "USER": decouple.config('POSTGRES_USER', default='postgres'),
        "PASSWORD": decouple.config('POSTGRES_PASSWORD', default=None),
        "HOST": decouple.config('POSTGRES_HOST', default='localhost'),
        "PORT": decouple.config('POSTGRES_PORT', default='5432'),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{decouple.config('REDIS_HOST', default='localhost')}:{decouple.config('REDIS_PORT', default='6379')}/{decouple.config('REDIS_DB', default='0')}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": decouple.config('REDIS_PASSWORD', default=None),
        },
        "KEY_PREFIX": decouple.config('REDIS_KEY_PREFIX', default='redis')
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),
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

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = False

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
