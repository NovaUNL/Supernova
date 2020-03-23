import json
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application definition
INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'captcha',
    'ckeditor',
    'ckeditor_uploader',
    'rest_framework',
    'analytical',
    'leaflet',
    'markdownx',
    'django_elasticsearch_dsl',
    'django_crontab',
    'supernova.apps.SupernovaConfig',
    'users',
    'groups',
    'college',
    'news',
    'synopses',
    'services',
    'store',
    'chat',
    'events',
    'feedback',
    'planet',
    'documents',
    'exercises',
    'api',
    'clip',
    'django_extensions',
    'debug_toolbar',
    'polymorphic',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'supernova.urls'

SITE_ID = 1

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'wsgi.application'

# Password validation
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

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Internationalization
LANGUAGE_CODE = 'pt-pt'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    "static"
]

STATIC_URL = '/static/'
STATIC_ROOT = '/srv/http/supernova/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/srv/http/supernova/media/'

# CKEditor plugin
CKEDITOR_BASEPATH = '/static/ckeditor/ckeditor/'
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_ALLOW_NONIMAGE_FILES = True
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_MATHJAX_URL = '//cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.3/MathJax.js?config=TeX-AMS_HTML'
CKEDITOR_SIMPLE_TOOLBAR = [
    {'name': 'styles', 'items': ['Styles']},
    {'name': 'basicstyles',
     'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
    {'name': 'colors', 'items': ['TextColor', 'BGColor']},
    {'name': 'paragraph', 'items': ['NumberedList', 'BulletedList', 'Blockquote']},
    {'name': 'insert', 'items': ['Image', 'Table', 'Mathjax', 'CodeSnippet']},
    {'name': 'tools', 'items': ['Source', 'Preview', 'Maximize']}
]
CKEDITOR_COMPLEX_TOOLBAR = [
    {'name': 'styles', 'items': ['Styles', 'Format', 'FontSize']},
    {'name': 'basicstyles',
     'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
    {'name': 'colors', 'items': ['TextColor', 'BGColor']},
    {'name': 'paragraph',
     'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', '-',
               'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
    {'name': 'links', 'items': ['Link', 'Unlink']},
    {'name': 'insert',
     'items': ['Image', 'Table', 'HorizontalRule', 'SpecialChar', 'Mathjax', 'CodeSnippet', 'Iframe']},
    {'name': 'tools', 'items': ['ShowBlocks', 'Source', 'Preview', 'Maximize']}
]
CKEDITOR_EXTRA_PLUGINS = 'uploadimage,mathjax,codesnippet,div,autolink,autoembed,embedsemantic,' \
                         'autogrow,widget,lineutils,clipboard,dialog,dialogui,elementspath'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar_Simple': CKEDITOR_SIMPLE_TOOLBAR,
        'toolbar': 'Simple',
        'width': '100%',
        'skin': 'moono-dark',
        'mathJaxLib': CKEDITOR_MATHJAX_URL,
        'tabSpaces': 4,
        'extraPlugins': CKEDITOR_EXTRA_PLUGINS,
    },
    'complex': {
        'toolbar_Complex': CKEDITOR_COMPLEX_TOOLBAR,
        'toolbar': 'Complex',
        'width': '100%',
        'skin': 'moono-dark',
        'mathJaxLib': CKEDITOR_MATHJAX_URL,
        'tabSpaces': 4,
        'extraPlugins': CKEDITOR_EXTRA_PLUGINS,
    },
}

# Captcha plugin
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_null',)

if os.path.isdir(f'{BASE_DIR}/.git/'):
    VERSION = subprocess.check_output([
        "git",
        f"--git-dir={BASE_DIR}/.git/",
        "rev-parse",
        "HEAD"
    ]).decode('ascii')
else:
    VERSION = "0.0"

REGISTRATIONS_ENABLED = False
REGISTRATIONS_ATTEMPTS_TOKEN = 3
REGISTRATIONS_TIMEWINDOW = 60  # Minutes
REGISTRATIONS_TOKEN_LENGTH = 6

AUTH_USER_MODEL = 'users.User'

COLLEGE_YEAR = 2020  # TODO deduce me PS: 2018 = 2017/2018
COLLEGE_PERIOD = 2  # TODO deduce me

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

LOGIN_URL = '/entrar'

LEAFLET_CONFIG = {
    'SPATIAL_EXTENT': (-9.20209, 38.65727, -9.20955, 38.66384),
    'DEFAULT_CENTER': (38.6608, -9.205576),
    'DEFAULT_ZOOM': 18,
    'MIN_ZOOM': 16,
    'MAX_ZOOM': 19,
    'TILES': 'https://cartodb-basemaps-{s}.global.ssl.fastly.net/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    'ATTRIBUTION_PREFIX': 'Leaflet',
    'RESET_VIEW': False,
}

DEBUG = False
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
VULNERABILITY_CHECKING = False

INTERNAL_IPS = ['127.0.0.1', ]

assert 'SN_CONFIG' in os.environ
CONFIG_PATH = os.environ['SN_CONFIG']
assert os.path.isfile(CONFIG_PATH)

ABS_CONFIG_PATH = os.path.abspath(CONFIG_PATH)
CRONTAB_COMMAND_PREFIX = "SN_CONFIG=%s" % ABS_CONFIG_PATH

with open(CONFIG_PATH) as file:
    locals().update(json.load(file))

if DEBUG:
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
