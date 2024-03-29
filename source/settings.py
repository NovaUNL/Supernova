import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from django.urls import reverse

BASE_DIR = Path(__file__).resolve().parent

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
    'django.contrib.sitemaps',
    'rest_framework',
    'rest_framework.authtoken',
    'elasticsearch_dsl',
    'django_elasticsearch_dsl',
    'django_elasticsearch_dsl_drf',
    'reversion',
    'supernova',
    'users',
    'groups',
    'college',
    'learning',
    'news',
    'services',
    'chat',
    'feedback',
    'documents',
    'api',
    'management',
    'clip',
    'captcha',
    'imagekit',
    'markdownx',
    'leaflet',
    'polymorphic',
    'django_extensions',
    'analytical',
    'channels',
    'pwa',
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
]

ROOT_URLCONF = 'supernova.urls'

SITE_ID = 1

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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
ASGI_APPLICATION = "asgi.application"

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

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('localhost', 6379)],
        },
    },
}

MAX_PASSWORD_CORRELATION = 0.7

FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 10  # 10 MB

# Internationalization
LANGUAGE_CODE = 'pt-pt'
TIME_ZONE = 'Europe/Lisbon'
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
PROTECTED_URL = '/protected'
PROTECTED_ROOT = '/srv/protected'
EXTERNAL_URL = '/external'
EXTERNAL_ROOT = '/srv/external'

IMAGEKIT_CACHEFILE_DIR = 'cache/images'

THUMBNAIL_SIZE = (220, 150)
COVER_SIZE = (1920, 500)
BIG_ICON_SIZE = (256, 256)
MEDIUM_ICON_SIZE = (128, 128)
SMALL_ICON_SIZE = (64, 64)

MEDIUM_QUALITY = 70
HIGH_QUALITY = 85

# Captcha plugin
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_null',)

REGISTRATIONS_ENABLED = False
REGISTRATIONS_ATTEMPTS_TOKEN = 3
REGISTRATIONS_TIMEWINDOW = 60  # Minutes
REGISTRATIONS_TOKEN_LENGTH = 10

AUTH_USER_MODEL = 'users.User'

_now = datetime.now()
if _now.month > 7:
    COLLEGE_YEAR = _now.year + 1
    COLLEGE_PERIOD = 2
else:
    COLLEGE_YEAR = _now.year
    COLLEGE_PERIOD = 3

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ]
}

LOGIN_URL = '/entrar'

REVIEWABLE_ENTITIES = (
    ('college', 'teacher'),
    ('college', 'class'),
    ('college', 'classinstance'),
    ('groups', 'group'),
    ('services', 'service'),
)

SUGGESTABLE_ENTITIES = (
    ('college', 'teacher'),
    ('groups', 'group'),
    ('services', 'service'),
)

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

MARKDOWNX_MARKDOWN_EXTENSIONS = [
    'markdown.extensions.tables',
    'pymdownx.arithmatex',
    'pymdownx.details',
    'pymdownx.inlinehilite',
    'pymdownx.highlight',
    'pymdownx.keys',
    'pymdownx.mark',
    'pymdownx.smartsymbols',
    'pymdownx.striphtml',
    'pymdownx.superfences',
    'pymdownx.tilde'
]

MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS = {
    'pymdownx.arithmatex': {
        'smart_dollar': False
    },
    'pymdownx.superfences': {
        'css_class': '',
    },
    'pymdownx.highlight': {
        'use_pygments': False,
        'guess_lang': True,
    },
}
MARKDOWNX_UPLOAD_CONTENT_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/svg+xml']
MARKDOWNX_IMAGE_MAX_SIZE = {'size': (1500, 1500), 'quality': 90}

MARKDOWNX_SERVER_CALL_LATENCY = 1000
# MARKDOWNX_URLS_PATH = '/md/markdownify/'
# MARKDOWNX_UPLOAD_URLS_PATH = '/md/upload/'

PWA_APP_NAME = 'Supernova'
PWA_APP_DESCRIPTION = "A integrar o teu conteúdo"
# PWA_APP_THEME_COLOR = '#323138'
# PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'any'
PWA_APP_START_URL = '/?pwa'
# PWA_APP_STATUS_BAR_COLOR = '#323138'
PWA_APP_ICONS = [
    {
        "src": "/static/img/pwa/icon.svg",
        "sizes": "36x36 48x48 72x72 96x96 120x120 128x128 144x144 152x152 180x180 192x192 384x384 512x512",
        "type": "image/svg+xml",
        "purpose": "any maskable",
    },
    {
        "src": "/static/img/pwa/icon-152.png",
        "sizes": "36x36 48x48 72x72 96x96 120x120 128x128 144x144 152x152",
        "type": "image/png",
    },
    {
        "src": "/static/img/pwa/icon-192.png",
        "sizes": "180x180 192x192",
    },
    {
        "src": "/static/img/pwa/icon-384.png",
        "sizes": "384x384",
    },
    {
        "src": "/static/img/pwa/icon-512.png",
        "sizes": "512x512",
    },
    {
        "src": "/static/img/pwa/icon-96.png",
        "sizes": "32x32"
    },
]
PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'pt-PT'
PWA_APP_DEBUG_MODE = True

# Ignore auto updating of Elasticsearch when a model is saved or deleted:
ELASTIC_IGNORE_SIGNALS = True
# Don't perform an index refresh after every update (overrides global setting):
ELASTIC_AUTO_REFRESH = False
# Paginate the django queryset used to populate the index with the specified size
# (by default it uses the database driver's default setting)
ELASTIC_QUERYSET_PAGINATION = 5000
ELASTIC_INDEX_SETTINGS = {
    'number_of_shards': 1,
    'number_of_replicas': 0
}

DEBUG = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
VULNERABILITY_CHECKING = False
CAMPUS_EMAIL_SUFFIX = ''

INTERNAL_IPS = ['127.0.0.1', ]

INDEX_MESSAGE = None

GENERAL_CHAT = 'geral'

MATRIX_URL = None
MASTODON_URL = None
SIGNAL_URL = None
GITLAB_URL = None
TELEGRAM_URL = None

REWARDS = {
    'add_section': 200,
    'add_exercise': 100,
    'major_tweak': 0,
    'minor_tweak': 0,
    'post_question': -5,
    'post_answer': 10,
    'accepted_answer': 100,
    'vote_cost': -1,
    'upvoted': 10,
    'downvoted': -15,
    'invited': 1000,
}

CLIPY = {
    'host': "clipy:5000",
}
CLIPY_HOST = "clipy:5000"
CLIPY_MIN_UPDATE_MARGIN = 6  # Hours
CLIPY_MIN_EXPLICIT_UPDATE_MARGIN = 5  # Minutes
CLIPY_RECENT_YEAR_MARGIN = 2  # Years

# Load config from external settings, overriding current settings
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

    INSTALLED_APPS += ["silk", 'debug_toolbar']
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "silk.middleware.SilkyMiddleware"]
