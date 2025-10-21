"""
Django settings for Asetena School Management System.

Environment variables:
    DEBUG: Set to 'True' for debug mode (default: False for production)
    SECRET_KEY: Django secret key (required for production)
    DATABASE_URL: PostgreSQL connection string (uses SQLite if not set)
    ALLOWED_HOSTS: Comma-separated list of allowed hosts
"""

import os
from pathlib import Path
import dj_database_url
from datetime import timedelta

# =====================
# BUILD PATHS
# =====================
BASE_DIR = Path(__file__).resolve().parent.parent

# =====================
# ENVIRONMENT & DEBUG
# =====================
# Default to True for development convenience, set DEBUG=false explicitly in production
DEBUG = os.environ.get('DEBUG', 'true').lower() == 'true'

# In production, this MUST be set via environment variable
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-dev-key-change-in-production-12345'  # Development only
)

if not DEBUG and 'django-insecure' in SECRET_KEY:
    raise ValueError('SECRET_KEY must be set in production environment!')

# =====================
# HOSTS & DOMAIN CONFIGURATION
# =====================
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1', '*.localhost'])

# CSRF & CORS Configuration
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://*.up.railway.app',
    'http://localhost:3000',
    'http://127.0.0.1',
]

CSRF_COOKIE_SECURE = not DEBUG  # HTTPS only in production
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG  # HTTPS only in production
SESSION_COOKIE_HTTPONLY = True

# =====================
# INSTALLED APPLICATIONS
# =====================
INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party packages
    'crispy_forms',
    'crispy_bootstrap5',
    
    # Custom applications (Multi-tenant School Management)
    'schools',              # School model and multi-tenancy
    'accounts',             # User authentication and dashboards
    'students',             # Student profiles, grades, attendance
    'teachers',             # Teacher profiles and assignments
    'academics',            # Classes, subjects, academic years
    'parents',              # Parent accounts and child monitoring
    'communications',       # Teacher-parent messaging
    'attendance_tracking',  # Attendance management
    'user_dashboard',       # Customizable user dashboards
]

# =====================
# MIDDLEWARE
# =====================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',      # Static file serving
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'schools.middleware.TenantMiddleware',              # Multi-tenant filtering
]

ROOT_URLCONF = 'school_system.urls'

# =====================
# TEMPLATES
# =====================
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
                # Custom context processors
                'school_system.context_processors.breadcrumbs',
                'school_system.context_processors.user_notifications',
                'school_system.context_processors.school_settings',
            ],
            'builtins': [
                'django.templatetags.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'school_system.wsgi.application'


# =====================
# DATABASE CONFIGURATION
# =====================
DATABASE_URL = os.environ.get('DATABASE_URL')

DATABASES = {}

if DATABASE_URL:
    # Production: Use PostgreSQL (Railway, Heroku, etc.)
    DATABASES['default'] = dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
else:
    # Development: Use SQLite
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'ATOMIC_REQUESTS': True,
    }

# Database connection pooling (important for production)
if not DEBUG and DATABASE_URL:
    DATABASES['default'].update({
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    })


# =====================
# PASSWORD VALIDATION
# =====================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# =====================
# AUTHENTICATION
# =====================
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400 * 7  # One week
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
CSRF_COOKIE_AGE = 31449600  # One year


# =====================
# INTERNATIONALIZATION & LOCALIZATION
# =====================
LANGUAGE_CODE = 'en-gh'  # English (Ghana)
TIME_ZONE = 'Africa/Accra'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Available languages
LANGUAGES = [
    ('en', 'English'),
]


# =====================
# STATIC & MEDIA FILES
# =====================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise for serving static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =====================
# CRISPY FORMS CONFIG
# =====================
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Timetable configuration (modifiable without touching code)
TIMETABLE_TIME_SLOTS = [
    ("07:00", "08:30"),
    ("08:30", "09:45"),
    ("09:45", "10:30"),
    ("10:30", "11:30"),
    ("11:30", "13:00"),
]

# =====================
# LOGGING CONFIGURATION
# =====================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO' if DEBUG else 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console', 'file'],
            'level': 'INFO' if DEBUG else 'WARNING',
        },
        'students': {
            'handlers': ['console', 'file'],
            'level': 'INFO' if DEBUG else 'WARNING',
        },
    },
}

# =====================
# EMAIL CONFIGURATION
# =====================
if DEBUG:
    # Development: Use console email backend (prints to console)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
else:
    # Production: Use SMTP backend
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@schoolmanagement.local')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'server@schoolmanagement.local')

# =====================
# CACHING CONFIGURATION
# =====================
if DEBUG:
    # Development: Use local memory cache
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'school-management-cache',
            'TIMEOUT': 300,  # 5 minutes
        }
    }
else:
    # Production: Use Redis cache
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
            'TIMEOUT': 600,  # 10 minutes
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                }
            }
        }
    }

# Cache timeout for session
SESSION_CACHE_ALIAS = 'default'

# =====================
# ADDITIONAL SECURITY HEADERS (Production)
# =====================
if not DEBUG:
    # HTTPS and TLS settings
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Security headers
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        'default-src': ("'self'",),
        'script-src': ("'self'", "'unsafe-inline'"),  # For FullCalendar, Chart.js
        'style-src': ("'self'", "'unsafe-inline'"),   # For Bootstrap inline styles
        'img-src': ("'self'", 'data:', 'https:'),
        'font-src': ("'self'", 'data:'),
        'connect-src': ("'self'",),
    }
    X_FRAME_OPTIONS = 'SAMEORIGIN'
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# =====================
# FILE UPLOAD SETTINGS
# =====================
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Allowed file types for profile pictures
ALLOWED_UPLOAD_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_PROFILE_PICTURE_SIZE = 2 * 1024 * 1024  # 2 MB

# =====================
# CUSTOM APP CONFIGURATION
# =====================
# Multi-tenant school isolation
MULTI_TENANT = True  # When True, all queries filtered by user.school

# Grade calculation settings
GRADE_PASSING_SCORE = 40  # Minimum passing percentage
GRADE_SCALE = {
    'A+': (90, 100),
    'A': (80, 89),
    'B+': (70, 79),
    'B': (60, 69),
    'C+': (50, 59),
    'C': (40, 49),
    'D+': (30, 39),
    'D': (20, 29),
    'F': (0, 19),
}

# Attendance settings
ATTENDANCE_MARK_DEADLINE = 7  # Days after date to still mark attendance
MINIMUM_ATTENDANCE_PERCENTAGE = 80

# Pagination
PAGINATION_SIZE = 10