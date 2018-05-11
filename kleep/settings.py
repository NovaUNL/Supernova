import json
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(BASE_DIR + '/settings.json') as json_data:
    settings = json.load(json_data)
    SECRET_KEY = settings['SECRET_KEY']
    CLIP_USERNAME = settings['CLIP_USERNAME']
    CLIP_PASSWORD = settings['CLIP_PASSWORD']
    EMAIL_SERVER = settings['EMAIL_SERVER']
    EMAIL_SUFFIX = settings['EMAIL_SUFFIX']
    EMAIL_ACCOUNT = settings['EMAIL_ACCOUNT']
    EMAIL_PASSWORD = settings['EMAIL_PASSWORD']
    DATABASES = settings['DATABASES']
    PIWIK_DOMAIN_PATH = settings['PIWIK_DOMAIN_PATH']
    PIWIK_SITE_ID = settings['PIWIK_SITE_ID']
    ALLOWED_HOSTS = settings['HOSTS']

DEBUG = False
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
else:
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False

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
    'captcha',
    'ckeditor',
    'ckeditor_uploader',
    'rest_framework',
    'analytical',
    'clip',
    'kleep.apps.KleepConfig',
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
    'api',
    'django_extensions',
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

ROOT_URLCONF = 'kleep.urls'

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

WSGI_APPLICATION = 'kleep.wsgi.application'

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

# Internationalization
LANGUAGE_CODE = 'pt-pt'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/srv/http/kleep/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/srv/http/kleep/media/'

# CKEditor plugin
CKEDITOR_BASEPATH = '/static/ckeditor/ckeditor/'
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_ALLOW_NONIMAGE_FILES = True
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar_ToolbarConfig': [
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
            {'name': 'links', 'items': ['Link', 'Unlink']},
            {'name': 'insert',
             'items': ['Image', 'Table', 'HorizontalRule', 'SpecialChar', 'Mathjax', 'CodeSnippet', 'Iframe']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['ShowBlocks', 'Source', 'Preview', 'Maximize']}
        ],
        'toolbar': 'ToolbarConfig',
        'width': '100%',
        'mathJaxLib': '//cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.3/MathJax.js?config=TeX-AMS_HTML',
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage',
            'mathjax',
            'codesnippet',
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
    }
}

# Captcha plugin
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_null',)

VERSION = subprocess.check_output([
    "git",
    f"--git-dir={BASE_DIR}/.git/",
    "rev-parse",
    "HEAD"
]).decode('ascii')

REGISTRATIONS_ENABLED = True
REGISTRATIONS_ATTEMPTS_TOKEN = 3
REGISTRATIONS_TIMEWINDOW = 60  # Minutes
REGISTRATIONS_TOKEN_LENGTH = 6

AUTH_USER_MODEL = 'users.User'

COLLEGE_YEAR = 2018  # TODO deduce me PS: 2018 = 2017/2018
COLLEGE_PERIOD = 3  # TODO deduce me

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

VULNERABILITY_CHECKING = 'vulnerabilities' in DATABASES

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/kleep.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
        },
    },
}
if DEBUG:
    LOGGING['loggers']['django']['level'] = 'DEBUG'
