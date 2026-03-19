"""
Production settings for Railway deployment.
All secrets come from environment variables — never hardcoded.
"""

from .base import *
import os
import dj_database_url

DEBUG = False

# Railway sets DATABASE_URL automatically when you add PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,        # keep connections alive 10 min
        conn_health_checks=True,
    )

# Security headers — required for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Static files served by WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Logging for Railway's log viewer
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## Part 4 — Deployment Files

### Update `requirements.txt`
```
django>=4.2,<5.0
djangorestframework>=3.14
psycopg2-binary>=2.9
python-dotenv>=1.0
djangorestframework-simplejwt>=5.3
drf-yasg>=1.21
django-cors-headers>=4.3
django-filter>=23.0
gunicorn>=21.0
whitenoise>=6.6
dj-database-url>=2.1
requests>=2.31
Pillow>=10.0
```

---

### Update `Procfile`
```
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120