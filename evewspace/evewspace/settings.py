
DEBUG = True
TEMPLATE_DEBUG = DEBUG
MULTI_TENANT = True
AUTH_USER_MODEL = 'account.EWSUser'
ADMINS = (
        # ('Your Name', 'your_email@example.com'),
)

# import Celery config
import djcelery
djcelery.setup_loader()

BROKER_URL = 'amqp://guest:guest@localhost:5672/'
ALLOWED_HOSTS = ['*',]
from datetime import timedelta
from celery.schedules import crontab
CELERYBEAT_SCHEDULE = {
        'map_stats':{
                'task': 'Map.tasks.update_system_stats',
                'schedule': timedelta(hours=1),
                'args': ()
            },
        'map_sov':{
                'task': 'Map.tasks.update_system_sov',
                'schedule': crontab(minute=0, hour=10),
                'args': ()
            },
        'jump_cache':{
                'task': 'Map.tasks.fill_jumps_cache',
                'schedule': timedelta(minutes=10),
                'args': ()
            },
        'downtime_sites': {
                'task': 'Map.tasks.downtime_site_update',
                'schedule': crontab(minute=5, hour=11),
                'args': ()
            },
        'alliance_update':{
                'task': 'core.tasks.update_all_alliances',
                'schedule': crontab(minute=30, hour=10, day_of_week="tue"),
                'args': ()
            },
        'stale_locations':{
                'task': 'Map.tasks.clear_stale_records',
                'schedule': timedelta(minutes=5),
                'args': ()
            },
        'cache_reddit':{
                'task': 'core.tasks.cache_eve_reddit',
                'schedule': timedelta(minutes=45),
                'args': ()
            },
        'cache_feeds':{
                'task': 'core.tasks.update_feeds',
                'schedule': timedelta(minutes=30),
                'args': ()
            },
        'char_data':{
                'task': 'API.tasks.update_char_data',
                'schedule': timedelta(hours=1),
                'args': ()
            },
        'char_location_data':{
                'task': 'API.tasks.update_char_location',
                'schedule': timedelta(seconds=30),
                'args': ()
            },
        'update_account_status':{
                'task': 'API.tasks.update_account_status',
                'schedule': timedelta(hours=1),
                'args': ()
            },
        }


MANAGERS = ADMINS

DATABASES = {
        'default': {
                'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                'NAME': 'djangotest',                      # Or path to database file if using sqlite3.
                'USER': 'root',                      # Not used with sqlite3.
                'PASSWORD': '',                  # Not used with sqlite3.
                'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
                'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
        }
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': None
    }
}
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'
USE_TZ = True
# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Change the default login behavior
LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL ='/'

# Additional locations of static files
STATICFILES_DIRS = (
        # Put strings here, like "/home/html/static" or "C:/www/django/static".
        # Always use forward slashes, even on Windows.
        # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
# Make this unique, and don't share it with anybody.
SECRET_KEY = '^28avlv8e$sky_08pu926q^+b5&4&5&+ob7ma%v(tn$bg#=&k4'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'eveigb.middleware.IGBMiddleware',
)

ROOT_URLCONF = 'evewspace.urls'

TEMPLATE_DIRS = (
        # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
        # Always use forward slashes, even on Windows.
        # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.humanize',
        # Uncomment the next line to enable the admin:
        #'django.contrib.admin',
        'core',
        'account',
        'search',
        'Map',
        'POS',
        'SiteTracker',
        'API',
        'Alerts',
        'Jabber',
        'Slack',
        'eveigb',
        'djcelery',
        # Uncomment the next line to enable admin documentation:
        # 'django.contrib.admindocs',
)
#Require a registration code to register
ACCOUNT_REQUIRE_REG_CODE=True

import django.conf.global_settings as DEFAULT_SETTINGS
TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + ('core.context_processors.site', 'eveigb.context_processors.igb',)
# ejabberd auth gateway log settings

import logging

TUNNEL_EJABBERD_AUTH_GATEWAY_LOG = '/tmp/ejabberd.log'
TUNNEL_EJABBERD_AUTH_GATEWAY_LOG_LEVEL = logging.DEBUG

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
                'mail_admins': {
                        'level': 'ERROR',
                        'class': 'django.utils.log.AdminEmailHandler'
                }
        },
        'loggers': {
                'django.request': {
                        'handlers': ['mail_admins'],
                        'level': 'ERROR',
                        'propagate': True,
                },
        }
}

#SSO
SSO_LOGIN_SERVER = 'login.eveonline.com' #check http://eveonline-third-party-documentation.readthedocs.io/en/latest/reference/reference.html for sisi

#CREST
CREST_SERVER = 'crest-tq.eveonline.com' #check http://eveonline-third-party-documentation.readthedocs.io/en/latest/reference/reference.html for sisi

#ESI - Uses same enabled/secret key/client ID/base URL/login server/scope as CREST
ESI_SERVER = 'esi.tech.ccp.is/dev'
ESI_SOURCE = 'tranquility' #alternative is singularity

# Dirty hack to provide configuration overriding semantics. Use local_settings to override or add upon the default.
try:
    LOCAL_SETTINGS
except NameError:
    try:
        from local_settings import *
    except ImportError:
        pass


if not DEBUG:
    # when not in debug mode, add cached loader on top of template loaders
    TEMPLATE_LOADERS = (
        ('django.template.loaders.cached.Loader', TEMPLATE_LOADERS),
    )
