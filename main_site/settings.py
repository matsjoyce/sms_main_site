# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Django settings for main_site project.

Generated by 'django-admin startproject' using Django 1.8.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
import logging
try:
    from google.appengine.api import app_identity
except ImportError:
    app_identity = None
from keys import *

PROJECT_APP_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_APP = os.path.basename(PROJECT_APP_PATH)
PROJECT_ROOT = BASE_DIR = os.path.dirname(PROJECT_APP_PATH)

if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine'):
    sys.on_production = True
else:
    sys.on_production = False


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: App Engine's security features ensure that it is safe to
# have ALLOWED_HOSTS = ['*'] when the app is deployed. If you deploy a Django
# app not on App Engine, make sure to set an appropriate host here.
# See https://docs.djangoproject.com/en/1.10/ref/settings/
ALLOWED_HOSTS = ['*']

AUTHENTICATION_BACKENDS = ("mezzanine.core.auth_backends.MezzanineBackend",)

# Application definition

USE_MODELTRANSLATION = False

# Store these package names here as they may change in the future since
# at the moment we are using custom forks of them.
PACKAGE_NAME_FILEBROWSER = "filebrowser_safe"
PACKAGE_NAME_GRAPPELLI = "grappelli_safe"

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.redirects",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "mezzanine.boot",
    "mezzanine.conf",
    "mezzanine.core",
    "mezzanine.generic",
    "mezzanine.pages",
#    "mezzanine.blog",
    "mezzanine.forms",
    "mezzanine.galleries",
    "mezzanine.twitter",
#    "mezzanine.accounts",
#    "mezzanine.mobile",
    "main_site.apps",
    "compressor",
    PACKAGE_NAME_FILEBROWSER,
    PACKAGE_NAME_GRAPPELLI,
)

OPTIONAL_APPS = (
    "debug_toolbar",
    "django_extensions",
)

MIDDLEWARE = (
    "mezzanine.core.middleware.UpdateCacheMiddleware",

    'django.contrib.sessions.middleware.SessionMiddleware',
    # Uncomment if using internationalisation or localisation
    # 'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    "mezzanine.core.request.CurrentRequestMiddleware",
    "mezzanine.core.middleware.RedirectFallbackMiddleware",
    "mezzanine.core.middleware.TemplateForDeviceMiddleware",
    "mezzanine.core.middleware.TemplateForHostMiddleware",
    "mezzanine.core.middleware.AdminLoginInterfaceSelectorMiddleware",
    "mezzanine.core.middleware.SitePermissionMiddleware",
    "mezzanine.pages.middleware.PageMiddleware",
    "mezzanine.core.middleware.FetchFromCacheMiddleware",
)

ROOT_URLCONF = 'main_site.urls'
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_ROOT, "templates")
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.static",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.template.context_processors.tz",
                "mezzanine.conf.context_processors.settings",
                "mezzanine.pages.context_processors.page",
            ],
            "builtins": [
                "mezzanine.template.loader_tags",
            ],
        },
    },
]

WSGI_APPLICATION = 'main_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

## [START db_setup]
#if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine'):
    ## Running on production App Engine, so connect to Google Cloud SQL using
    ## the unix socket at /cloudsql/<your-cloudsql-connection string>
    #DATABASES = {
        #'default': {
            #'ENGINE': 'django.db.backends.mysql',
            #'HOST': '/cloudsql/<your-cloudsql-connection-string>',
            #'NAME': 'polls',
            #'USER': '<your-database-user>',
            #'PASSWORD': '<your-database-password>',
        #}
    #}
#else:
    ## Running locally so connect to either a local MySQL instance or connect to
    ## Cloud SQL via the proxy. To start the proxy via command line:
    ##
    ##     $ cloud_sql_proxy -instances=[INSTANCE_CONNECTION_NAME]=tcp:3306
    ##
    ## See https://cloud.google.com/sql/docs/mysql-connect-proxy
    #DATABASES = {
        #'default': {
            #'ENGINE': 'django.db.backends.mysql',
            #'HOST': '127.0.0.1',
            #'PORT': '3306',
            #'NAME': 'polls',
            #'USER': '<your-database-user>',
            #'PASSWORD': '<your-database-password>',
        #}
    #}
## [END db_setup]

if sys.on_production:
    # Running on production App Engine, so use a Google Cloud SQL database.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '/cloudsql/latvia-123011:django-sms',
            'NAME': 'django_main_site',
            'USER': "root"
        }
    }
else:
    # Running in development, but want to access the Google Cloud SQL instance
    # in production.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '173.194.253.108',
            'NAME': 'django_main_site',
            'USER': DB_USERNAME,
            'PASSWORD': DB_PASSWORD
        }
    }

DEFAULT_FILE_STORAGE = "main_site.storage.GoogleCloudStorage"
MEDIA_ROOT = ""
if app_identity:
    GOOGLE_CLOUD_STORAGE_BUCKET = "/" + app_identity.get_default_gcs_bucket_name()
    GOOGLE_CLOUD_STORAGE_URL = "http://storage.googleapis.com"
    GOOGLE_CLOUD_STORAGE_DEFAULT_CACHE_CONTROL = "public, max-age: 7200"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        "": {
            'handlers': ['console'],
            'level': 'DEBUG',
        }
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = "en"

# Supported languages
LANGUAGES = (
    ('en', 'English'),
)

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = True

USE_TZ = True

SITE_ID = 1

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = 'static'
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc {infile} {outfile}'),
)
COMPRESS_CSS_FILTERS = ["compressor.filters.yuglify.YUglifyCSSFilter"]
COMPRESS_JS_FILTERS = ["compressor.filters.yuglify.YUglifyJSFilter"]


def get_mezzanine_settings():
    """
    Returns the value of the mezzanine.conf.context_processors.settings context
    processor. Context processors usually can only be run during a request, but
    luckily, mezzanine ignores the request parameter, so we don't have to worry
    about it.
    """
    from mezzanine.conf.context_processors import settings
    return settings()['settings']


COMPRESS_OFFLINE_CONTEXT = {
    'STATIC_URL': STATIC_URL,

    # some mezzanine templates require the settings.
    'settings': get_mezzanine_settings
}

CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_APP

if sys.on_production:
    import settings_live

# set_dynamic_settings() will rewrite globals based on what has been
# defined so far, in order to provide some better defaults where
# applicable. We also allow this settings module to be imported
# without Mezzanine installed, as the case may be when using the
# fabfile, where setting the dynamic settings below isn't strictly
# required.
try:
    from mezzanine.utils.conf import set_dynamic_settings
except ImportError:
    pass
else:
    set_dynamic_settings(globals())
