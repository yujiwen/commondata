"""
Django settings for testsite project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
from os import path, getenv
from django.conf.locale.ja import formats as ja_formats

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(-s#=c&605*a_#urt&8+n6xv=gc8a9mtzk6^5-km69*l-vrlj*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'checked_csv',
    'commndata',
    'testsite',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'testsite.urls'

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

WSGI_APPLICATION = 'testsite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

# LANGUAGE_CODE = 'en-us'
# LANGUAGE_CODE = 'ja'
LANGUAGES = (
    ('en', 'English'),
    ('ja', 'Japanese'),
)


# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

USE_THOUSAND_SEPARATOR = True
NUMBER_GROUPING = (3, 0)

ja_formats.DATE_FORMAT = 'Y/m/d'                    # default: 'Y???n???j???'
ja_formats.DATETIME_FORMAT = 'Y/m/d H:i:s'          # default: 'Y???n???j???G:i'
ja_formats.SHORT_DATETIME_FORMAT = 'Y/m/d H:i'      # default: 'Y/m/d G:i'

ja_formats.DATE_INPUT_FORMATS = ['%Y/%m/%d', '%Y-%m-%d', '%Y%m%d']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}.{msecs:0<3.0f}][{module}:{filename}:{funcName}][{levelname}][{process:d}][{thread:d}]: {message}',
            'datefmt' : '%Y/%m/%d %H:%M:%S',
            'style': '{',
        },
        'simple': {
            'format': '[{asctime}][{module}][{levelname}]: {message}',
            'datefmt' : '%Y/%m/%d %H:%M:%S',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'sql_log': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': '/temp/django_sql_log.log',
            'encoding':'utf8',
        },
        'root_log': {
            'level': 'DEBUG',
            'filters': ['require_debug_false'],
            # TimedRotatingFileHandler must be used with --noreload option
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 5,
            'backupCount': 100,
            'formatter': 'simple',
            'filename': '/temp/django_root_log.log',
            'encoding':'utf8',
        },
        'testsite_log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': '/temp/testsite_log.log',
            'encoding':'utf8',
        },
        'console': {
            'level': 'DEBUG',
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        }
    },
    'root': {
        # 'handlers': ['console', 'root_log', 'testsite_log'],
        'handlers': ['console', 'testsite_log'],
        'level': 'WARNING',
    },
    'loggers': {
        'testsite': {
            'handlers': ['console', 'testsite_log'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['console', ],
            'level': getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['sql_log', 'console'],
            'propagate': False
        }
    }
}